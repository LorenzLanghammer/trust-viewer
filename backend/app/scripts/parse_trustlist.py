import struct
from cryptography import x509
from binascii import unhexlify
from pathlib import Path
import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
from cryptography.x509.oid import NameOID


def parse_trustlist(data):
    #data = bytes.fromhex(hex_string)
    offset = 0

    def read_i32():
        nonlocal offset
        val = struct.unpack_from("<i", data, offset)[0]
        offset += 4
        return val

    def read_bytes():
        nonlocal offset
        length = read_i32()
        if length < 0:
            return None
        val = data[offset:offset+length]
        offset += length
        return val

    def read_array():
        count = read_i32()
        if count < 0:
            return []
        return [read_bytes() for _ in range(count)]

    result = {}

    result["specified_lists"] = read_i32()
    result["trusted_certificates"] = read_array()
    result["trusted_crls"] = read_array()
    result["issuer_certificates"] = read_array()
    result["issuer_crls"] = read_array()

    return result

def encode_bytes(b):
    if b is None:
        return struct.pack("<i", -1)
    return struct.pack("<i", len(b)) + b

def encode_array(arr):
    if arr is None:
        return struct.pack("<i", -1)

    out = struct.pack("<i", len(arr))
    for item in arr:
        out += encode_bytes(item)
    return out


def build_trustlist_bytes(tl):
    out = b""
    out += struct.pack("<i", tl["specifiedLists"])
    out += encode_array(tl.get("trustedCertificates"))
    out += encode_array(tl.get("trustedCrls"))
    out += encode_array(tl.get("issuerCertificates"))
    out += encode_array(tl.get("issuerCrls"))

    return out

def add_crl_to_trustlist(tl, crl_bytes):
    tl["specifiedLists"] |= 0x02

    crls = tl.get("trustedCrls") or []
    crls.append(crl_bytes)
    tl["trustedCrls"] = crls

    return tl


def trustlist_2_bytes(trustlist):
        def write_u32(val):
            return struct.pack("<i", val)

        def write_bytes(b):
            if b is None:
                return write_u32(-1)
            return write_u32(len(b)) + b

        out = bytearray()
        out += write_u32(trustlist["specified_lists"])
        certs = trustlist.get("trusted_certificates") or []
        out += write_u32(len(certs))
        for c in certs:
            out += write_bytes(c)

        crls = trustlist.get("trusted_crls") or []
        out += write_u32(len(crls))
        for c in crls:
            out += write_bytes(c)

        issuers = trustlist.get("issuer_certificates") or []
        out += write_u32(len(issuers))
        for c in issuers:
            out += write_bytes(c)

        issuer_crls = trustlist.get("issuer_crls") or []
        out += write_u32(len(issuer_crls))
        for c in issuer_crls:
            out += write_bytes(c)

        return bytes(out)


def build_trustlist(trusted_certs=None, issuer_certs=None, trusted_crls=None, issuer_crls=None):
    def to_der_list(items):
        return [c.public_bytes(Encoding.DER) for c in (items or [])]
    return {
        "trusted_certificates": to_der_list(trusted_certs),
        "issuer_certificates": to_der_list(issuer_certs),
        "trusted_crls": to_der_list(trusted_crls),
        "issuer_crls": to_der_list(issuer_crls),
    }

def add_issuer_cert(hew_string):
    raw = bytes.fromhex(hex_string)
    old_trustlist = parse_trustlist(raw)
    with open("ca4/gds_ca_cert.der", "rb") as f:
        ca_cert = x509.load_der_x509_certificate(f.read())

    with open("ca4/gds_ca_key.der", "rb") as f:
        ca_key = serialization.load_der_private_key(
            f.read(),
            password=None
        )

    
def add_revocation(hex_string):
    raw = bytes.fromhex(hex_string)
    old_trustlist = parse_trustlist(raw)
    with open("ca4/gds_ca_cert.der", "rb") as f:
        ca_cert = x509.load_der_x509_certificate(f.read())

    with open("ca4/gds_ca_key.der", "rb") as f:
        ca_key = serialization.load_der_private_key(
            f.read(),
            password=None
        )

    now = datetime.datetime.now(datetime.UTC)
    revoked_cert = (
        x509.RevokedCertificateBuilder()
        .serial_number(15)
        .revocation_date(now)
        .build()
    )
    crl_builder = (
                x509.CertificateRevocationListBuilder()
                .issuer_name(ca_cert.subject)
                .last_update(now)
                .next_update(now + datetime.timedelta(days=365))
                .add_revoked_certificate(revoked_cert)
            )
    new_crl = crl_builder.sign(
        private_key=ca_key,
        algorithm=hashes.SHA256()
    )

    new_crl_der = new_crl.public_bytes(Encoding.DER)
    new_trustlist = dict(old_trustlist)
    new_trustlist["trusted_crls"] = [new_crl_der]
    new_trustlist_bytes = trustlist_2_bytes(new_trustlist)

    new_trustlist_recovered = parse_trustlist(new_trustlist_bytes)
    new_crl_recovered = new_trustlist["trusted_crls"][0]
    crl_crypto = x509.load_der_x509_crl(new_crl_recovered)

    with open("ca4/updated_trustlist.der", "wb") as f:
        f.write(new_trustlist_bytes)

def add_revocation_to_crl(crl: x509.CertificateRevocationList, serial: int, issuer_key: PrivateKeyTypes) -> x509.CertificateRevocationList:
    now = datetime.datetime.now(datetime.timezone.utc)
    revocation_date = now

    builder = x509.CertificateRevocationListBuilder()
    builder = builder.issuer_name(crl.issuer)
    builder = builder.last_update(now)
    builder = builder.next_update(now + datetime.timedelta(days=365))

    for revoked in crl:
        builder = builder.add_revoked_certificate(revoked)

    new_entry = (
        x509.RevokedCertificateBuilder()
        .serial_number(serial)
        .revocation_date(revocation_date)
        .build()
    )
    builder = builder.add_revoked_certificate(new_entry)
    return builder.sign(private_key=issuer_key, algorithm=hashes.SHA256())

def add_issuer_revocation(trustlist_hex, issuer_name, issuer_key, serial, trustlist_path):
    raw = bytes.fromhex(trustlist_hex)
    trustlist = parse_trustlist(raw)
    issuer_crls = trustlist["issuer_crls"]
    for i, crl_der in enumerate(issuer_crls):
        crl = x509.load_der_x509_crl(crl_der)
        cn_attrs = crl.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
        if cn_attrs and cn_attrs[0].value == issuer_name:
            new_crl = add_revocation_to_crl(crl, serial, issuer_key)            
            issuer_crls[i] = new_crl.public_bytes(Encoding.DER)
            break
    else:
        raise ValueError(f"No CRL found for issuer '{issuer_name}'")

    trustlist["issuer_crls"] = issuer_crls
    new_trustlist_bytes = trustlist_2_bytes(trustlist)

    with open (trustlist_path, "wb") as f:
        f.write(new_trustlist_bytes)


def renew_trustlist(hex_string):
    raw = bytes.fromhex(hex_string)
    old_trustlist = parse_trustlist(raw)

    with open("ca4/gds_ca_cert.der", "rb") as f:
        ca_cert = x509.load_der_x509_certificate(f.read())

    with open("ca4/gds_ca_key.der", "rb") as f:
        ca_key = serialization.load_der_private_key(f.read(), password=None)

    now = datetime.datetime.now(datetime.UTC)
    crl_builder = (
            x509.CertificateRevocationListBuilder()
            .issuer_name(ca_cert.subject)
            .last_update(now)
            .next_update(now + datetime.timedelta(days=365))
        )

    new_crl = crl_builder.sign(
        private_key=ca_key,
        algorithm=hashes.SHA256()
    )
    new_crl_der = new_crl.public_bytes(Encoding.DER)
    new_trustlist = dict(old_trustlist)
    new_trustlist["trusted_crls"] = [new_crl_der]
    new_trustlist_bytes = trustlist_2_bytes(new_trustlist)

    with open("ca4/updated_trustlist.der", "wb") as f:
        f.write(new_trustlist_bytes)


def add_issuer_certificate(trustlist_hex, issuer_cert: x509.Certificate, trustlist_path):
    raw = bytes.fromhex(trustlist_hex)
    trustlist = dict(parse_trustlist(raw))
    issuers: list = trustlist["issuer_certificates"]
    issuers.append(issuer_cert.public_bytes(encoding=Encoding.DER))
    trustlist["issuer_certificates"] = issuers
    new_trustlist_bytes = trustlist_2_bytes(trustlist)
    with open (trustlist_path, "wb") as f:
        f.write(new_trustlist_bytes)

def add_issuer_crl(trustlist_hex, issuer_key: PrivateKeyTypes, issuer_certificate: x509.Certificate, trustlist_path):
    raw = bytes.fromhex(trustlist_hex)
    old_trustlist = dict(parse_trustlist(raw))

    now = datetime.datetime.now(datetime.UTC)
    crl_builder = (
            x509.CertificateRevocationListBuilder()
            .issuer_name(issuer_certificate.subject)
            .last_update(now)
            .next_update(now + datetime.timedelta(days=365))
        )

    new_crl = crl_builder.sign(
        private_key=issuer_key,
        algorithm=hashes.SHA256()
    )
    new_crl_der = new_crl.public_bytes(Encoding.DER)
    new_trustlist = dict(old_trustlist)
    new_trustlist["issuer_crls"] = [new_crl_der]
    new_trustlist_bytes = trustlist_2_bytes(new_trustlist)

    with open(trustlist_path, "wb") as f:
        f.write(new_trustlist_bytes)

def add_trusted_crl(trustlist_hex, issuer_key: PrivateKeyTypes, issuer_certificate: x509.Certificate, trustlist_path):
    raw = bytes.fromhex(trustlist_hex)
    trustlist = dict(parse_trustlist(raw))
    now = datetime.datetime.now(datetime.UTC)
    crl_builder = (
            x509.CertificateRevocationListBuilder()
            .issuer_name(issuer_certificate.subject)
            .last_update(now)
            .next_update(now + datetime.timedelta(days=365))
        )

    new_crl = crl_builder.sign(
        private_key=issuer_key,
        algorithm=hashes.SHA256()
    )
    new_crl_der = new_crl.public_bytes(Encoding.DER)
    new_trustlist = dict(trustlist)
    new_trustlist["trusted_crls"] = [new_crl_der]
    new_trustlist_bytes = trustlist_2_bytes(new_trustlist)
    
    with open(trustlist_path, "wb") as f:
            f.write(new_trustlist_bytes)

hex_string = "0f00000002000000510500003082054d30820335a003020102021403fee654c933499207c89c06b740829515dc62bc300d06092a864886f70d01010b05003036310b3009060355040613024445310b300906035504080c024257310c300a060355040a0c036f7267310c300a06035504030c03636137301e170d3236303632393139303335385a170d3336303632363139303335385a3036310b3009060355040613024445310b300906035504080c024257310c300a060355040a0c036f7267310c300a06035504030c0363613730820222300d06092a864886f70d01010105000382020f003082020a0282020100d7fb1438c2b3c1ec12a5bcca050b8245217830a1092513f3b86b819fa798931cff06a5542d93593e40d50d4c56b47192979dda1ddd4986f752441b377aa262591b9d9030c9d741d2ba9ea03e4102c65d781bc7c5a66458584198d669b734bf6c5840d0ee1ed3e13ffdb48fddae9d91490b97d15883fb872e0b0850df9dade0fb1f6b3447514ab6cfcf0fc0512a53be9e50a2059b1e2e6fb53473f6618daff3231157e805caf6670d131c200e42c3793d410015717c00ddcc6fec96ead63dd31d8a01e8e63d94976101266f4b9a7962292aa3e5dda752ee94e6afc7d6e2c443bfd88acf1f946190a43f58ced495f6017f38f8e9ac4e2bb787f06d19adad52d8486af4c1e4151f88f3abe05c1448ba747726dbf5006fce2aebd21c452866c622200bef91bceac85fb746ab5d8e8f0c55dc1abad03b4c159c54bbd79a1b3773ed3581a1beaa208093057097cf6ed4304d8ba2b18a7159f71b53e1dc8a487daaf8915a0ff80ff2b83dfa572362d87a7efabfc6a2a4903e93309bfcab92462c73d36b51be48f4643ddbfb442a2e762a5fb35f60935253cb933d044fdc7b598d7a1d40c0ca439e6e1a9eb39ac8613673baa2bf11cc9b54c2bb1bf76e433359db994afd398048132eac8c1ea2a75dcbe3d9491fa89ca7be110ce6be84a06ddbcf6b77f71c0623aba62064bea770d13737369cb57fbddf79a0a0751f8f1c95f59e2c9df70203010001a3533051301d0603551d0e041604146c916e18bd421c6b9e4bd75122dccdad6069a3fa301f0603551d230418301680146c916e18bd421c6b9e4bd75122dccdad6069a3fa300f0603551d130101ff040530030101ff300d06092a864886f70d01010b050003820201005a3f21e48af08317ea483275fd4853a0bff0ce46173715ee93c49bfd54882a3b2114f3b394cda5a2aaece2608765a27a22e0e3a8209c5756746ce37f1b0622a2041cb8e693ff8d935805edee825d401ababd22a92d2242aac0ebdc91d4b1e29322bf2fb4976a2b9f45b962de4654ad42d22fdcf990a5fb37f525a31386dc913f35ab414ce18b08cf03136c94a6d30143ceb859f0a4070f12ea354e034788c67612c12ba0c0988a38719a71aa6f0c7832426e38227b9bcd62f78f78a3df46bfc3b06bb8fcc8680a35557136832d5a13e9adcfcdc437e49e64c58b732ac9072aeaffbcf47ab7feb10ab79f767df349c3660723c12edc4b93f39aa79e600845022692cb4cb7fb0fa8ac87ec7c907af08da74139a0806036cbddd2b60fd98a62ecc93c15cf6d77c53541fcac7f94d0ec5ecdbbabfc1b84c313ef3dba4d07ead5e923b1ba0e3f29cf37b5ac41657cd011212e20448e6e40a27997a49456bfc4676c9cf4933607d1a27d083af64971ea75cd85ded090de1328688a5dcb810664901fe876d0bb1e49e8fff9bf5b66275911976828cbf0cd3a97c93a2127395731dcc17ea5f8532e8df35a7b805322fea73407fe068277ee26292af8005e6941d7268803691dc31271df4a1c7ffe76df804052cfdf776b6574fa7f201b50e20ab1a9e530ba8a897122c9263b38c1153e01d45540537073b3d32559c4de0581230ee0c1c87a050000308205763082035ea003020102020118300d06092a864886f70d01010b05003036310b3009060355040613024445310b300906035504080c024257310c300a060355040a0c036f7267310c300a06035504030c03636138301e170d3236303632393232333533345a170d3237303632393232333633345a302d310b3009060355040613024445310e300c060355040a0c054d794f7267310e300c06035504030c05617070313730820222300d06092a864886f70d01010105000382020f003082020a0282020100baab491c0632e09f52e0221fe5b4f24b32f159417a20c8a24e61222dea9d42caef90fc00549ac0232676004231a61ea67e7f7c9c4d8f510746e1cb7afee48c5a72e2dd3a0e3b60776090913cee0532bd54d4189ea06f862038319c5cdef07a7ba55683b3baa5ded46c66c63677454c69989c75f5f2a09548e7313941dc63256428afa5f6d218bdaf915807e07f12f6cae0c5808d848a06860fe94ec23f51a0e5aa6cb89c3642d4ef6047f3dd8098aa3deef8b9beea4905d08f160ff7acf7c615f5514b74716fac3a9d3c71ef97019cbde1013dfaee3c7fe4ab6c65b38183fefa10511aaf8afb85de3003961fde08606bc6e639fbbf7f277fa12872a791a20a74e11f5d430092c716cfa94f4decdb1fe7d66ede4f79e5d964b2ad0be1d3fdbf5b80fcdb82c0fdf31a102c7e8da07313040e370a413eca75e67376ae16633ecbeac963f4223eb00944b5aa4a16ae07da1a9c860970f89c0fd386872e5a73745d87eaef393e90f353aebd23ecad6f7630409ba305430ea03d545b40d09e2028e044c53d1a725f9ab496883c26101a5611f51d8b83a2315666ef494259b5761d69fcd4e6be46d0b3100628bc39e3a9aac2e9875ecaff87ee787287cfc02b44419e35ff5c4a160b288e47d48e2e2f60cf21abf9cbb0e87bbabaf8df3c267e0ea00320c66ceee5490dc456e7c71dd08ef4cc733502c417fc969dc924b41d897ff362ab0203010001a3819730819430090603551d1304023000300b0603551d0f0404030204f030130603551d25040c300a06082b06010505070301301f0603551d23041830168014ec5fb366b9cc8299fc85f269493f3bdecf4dc29d301d0603551d0e04160414b927b5e368270df9f2e041078ac64d116119ca6830250603551d11041e301c860961707031373a75726982096c6f63616c686f737487047f000001300d06092a864886f70d01010b05000382020100e035bfc29c5290cbb488852b8655e8036f4408a36b88829d8b0758efde4fc642c83f685bc3323587026da704d73f0bdbd7880598979d06c8fc5ddd13792d289882aad143064f4b0617790633bb559581cfc945da3af14deb1d7d2ed0a973f61baeee3c848a299ebded874349c1e85b8fa1530cab427f5214b809f3f35057de43629588ac767228791678a0985189e7fd5d5e8d5f95e5f5d6d35499f4278e45cf3de90a03cb58eada7de7742ac254e20e9f4b523af4311ee8f8f8ed02e29c37d70ffb5a34af0f140201eb9e779e5edec58058223151b2b81cae2ee41bb569bf802c2cedb1b9dc35b3cbddca2e8458d5ba47e424ed49d064d6dd329dc7cbb453eb5352fb1ae6c13e59a2f80b11891d9658ee8a8228472462dae95d11560d66bf89463d47baeb77405ee422fc01617e0945cc6eb59482936105f82dc61ed33059d526e36fa36151e5df83a7f3b3547c0fe40ee08d4d0b7c09d6f931a7d2dc95b1dc2a2ac879fa785c481686500dd4fd8a0b6fafd818242f7b20f7733bbf556c30e18f150ec50aadb6e10b1814a42ce76122e625009e97b2cd8082ddab0ef13ee7abab526f32df6d815be9ce145dab308ff957c442860ae1cc61a34fa2a12228bef0e042e2f1203cc91536823c77b87f8e0b7885e38f4b9813236f3a254a3f6f386b88588f90320ba04f24ab59e418c19c3af721f0ea8fd457838d1d4fcab8bc1ecf0000000001000000510500003082054d30820335a0030201020214645c1d86b06304d804fa82834464fd9ee1d5072b300d06092a864886f70d01010b05003036310b3009060355040613024445310b300906035504080c024257310c300a060355040a0c036f7267310c300a06035504030c03636138301e170d3236303632393139323630355a170d3336303632363139323630355a3036310b3009060355040613024445310b300906035504080c024257310c300a060355040a0c036f7267310c300a06035504030c0363613830820222300d06092a864886f70d01010105000382020f003082020a0282020100e08808e771bdb5e2aabc4fe70292bd4eafb1107927fcf5ff6679b9c17e67da4de5545122d53c51cbfa9de511bb806ca000c69f4fa03751a6390ca8f720e3756293a7cb883511d18f28b3275539e2fbf1d11e546e5bc92959cd5752f7755928dd42b63d4ae94fbe3fe0ff1c95ff533e36bdc249ef031415aa71098ced9659e9aa713d20ae538319782754bb8cf5207f63637391399ec8213a1cfe571caba44fb31c9d30d55730a7fd7eaaa76895eb255fc16e824b572bd1e7bfd99ca56c7fad2b22c7809b2e46a822dbb631bf5ac5e00f24794cee0974667ee32ae54bd432acfc69e08ee7e4b7a31fff451974ebae3b5d5294f90117fa36592b2d5d92488c8c92336e97109673177e9caabde3d80c27cc53d3e796f67480cc4249c3eaf0263e7906c121dac979ba42f4aabcc752b6ca0381ebee157b66949e41b3aeac3c0017a03515d2e00f7aba19f62462226cd62127323c14f0673cb559e01e62f5dd87bbc900dc9fff123bdf1cd967a657117720f0cc50aa59435a5a1cc00662d1211bd432c324db72fae7f7528729b46944ef653e5bb0fb4367232618be9e0d942e0b5932f3b672cbcd1db72b7135a3c425b0e108472839401c59776b4bc3781099b032e1ae5dcf4eab0baf4c3d09190ed75d25ac4e7640ed563ae8c9239f89fe3c7ee953749063b45121b9816e034df46ee709746b09c4cf34b65a79062640ad4dbfc66d0203010001a3533051301d0603551d0e04160414ec5fb366b9cc8299fc85f269493f3bdecf4dc29d301f0603551d23041830168014ec5fb366b9cc8299fc85f269493f3bdecf4dc29d300f0603551d130101ff040530030101ff300d06092a864886f70d01010b050003820201003d28aa3645f3d96fd3870f4ee4545b84be9c913d83716aa67b223dc38daf240c80b8991f208c1d11171b14f1897b65eb0e4846f09cdc846768fd188f7e98f6574f4e72151d351f0406be21bc3106113677f4f299a852d94667fd7277425ecfc415a21783bd680d23120d9377760268a27161fbfb79f9f3a0c339ba2307ab64e0387bd8cfc563138037820c2ef7b544bd849e0c01eb3a3871c58f84717b726b3f31f86ebd7d751faaa5bac57b3023edbb2e555021aaaa2fe5a452c7da33c6297c80cdde89a61ca4a2fe407a22a9dfcd7d9dcc91a80c6945017fb9b0988531be3ebadd81c1a045e2bf201939f21670d6dec577eeeabdb5ca5fbff7f934f8f2d1b623720dc394589e10fe7ce6703ecb896d19ea8dd18b32fd128cd84dc68e41c7d04eae93b5357c7d2b004024c675e4fb6cece79c4c020695b124ef83bf71f075a279cf36d1eb1257941c7b3d20096eda5e43170651d21a46bde08b2c87048b011fc08c6d9fb69e89694e741236239b910451515dff678a7657ee43711e14d8d41ab67f934aa99f5c0dfeb372d53dd74ef17af4027519795a96c07cb48ec6f00f20a800a4ec3cb9d6f0320da4b38fc07614778f2dd80e3bca7110bad9838b6c550f110f92da04157666d70d5a2f13f6190327647d1107884829e58d2534dcafa4b3f94112e0cee329bac326a2ccdedd7365d19ba78f1b28ef1b6e3110d6d5c1389800000000"
with open("ca8/gds_ca_cert.der", "rb") as ca_cert:
    ca_cert = x509.load_der_x509_certificate(ca_cert.read())

with open("ca8/gds_ca_key.der", "rb") as ca_key:
    ca_key = serialization.load_der_private_key(ca_key.read(), None)

#add_issuer_certificate(hex_string, ca_cert, "ca8/updated_trustlist.der")
add_issuer_crl(hex_string, ca_key, ca_cert, "ca8/updated_trustlist.der")
