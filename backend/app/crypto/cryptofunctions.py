from ..model import crl
from ..model import extension
from ..model import certificate
from ..model import trustlist
from ..model import certSummary
from cryptography import x509
from cryptography.x509.oid import ExtensionOID
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
from io import BytesIO
import struct
from OpenSSL import crypto as ossl
from OpenSSL._util import ffi as _ffi, lib as _lib
from OpenSSL import crypto as ossl
from OpenSSL.crypto import X509StoreFlags
from cryptography import x509


def verify_certs_against_trustlists(certs, trustlists):
    for cert in certs:
        for trustlist in trustlists:
            if verify_cert(cert, trustlist):
                return True
    return False

def _load_certs(der_list):
    return [ossl.X509.from_cryptography(x509.load_der_x509_certificate(c)) for c in (der_list or [])]


def verify_cert(cert_bytes, trustlist):
    ossl_cert = ossl.X509.from_cryptography(x509.load_der_x509_certificate(cert_bytes))

    trusted_certs = _load_certs(trustlist.get("trusted_certificates"))
    issuer_certs = _load_certs(trustlist.get("issuers"))
    crls = (trustlist.get("trusted_crls") or []) + (trustlist.get("issuer_crls") or [])

    store = ossl.X509Store()
    for c in trusted_certs:
        store.add_cert(c)
    for crl_bytes in crls:
        crl_crypto = x509.load_der_x509_crl(crl_bytes)
        store.add_crl(crl_crypto)

    for issuer in issuer_certs:
        print("issuer cert subject")
        print(issuer.get_subject())

    flags = X509StoreFlags.PARTIAL_CHAIN
    flags |= X509StoreFlags.CRL_CHECK | X509StoreFlags.CRL_CHECK_ALL
    store.set_flags(flags)

    store_ctx = ossl.X509StoreContext(store, ossl_cert, chain=issuer_certs)
    try:
        store_ctx.verify_certificate()
        return True
    except ossl.X509StoreContextError as e:
        print(f"Certificate verification failed: {e}")
        return False


def bytes_2_cert(bytes: str):
    cert = x509.load_der_x509_certificate(bytes)
    pubkey = cert.public_key()
    key_bytes = pubkey.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    key_hex = key_bytes.hex()

    subject_name = cert.subject
    serial_number = cert.serial_number
    #country_value = subject_name.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value
    common_name = subject_name.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    issuer_name = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    not_before = cert.not_valid_before
    not_after = cert.not_valid_after
    extensions = cert.extensions
    extensions_list = get_extensions(extensions)
    fingerprint = cert_id(cert)
    
    result_cert = certificate.Certificate(
        serial_number,
        key_hex,
        common_name,
        issuer_name,
        str(not_before),
        str(not_after),
        extensions_list
    )
    
    return(result_cert, fingerprint)


def hex_2_cert(hex: str):
    der_bytes = bytes.fromhex(hex)
    return bytes_2_cert(der_bytes)
    

def get_extensions(extensions: x509.Extensions):
    extensions_list = []
    for ext in extensions._extensions:

        if (ext._oid == ExtensionOID.SUBJECT_ALTERNATIVE_NAME):
            name = ext._oid._name
            value = ext.value.get_values_for_type(x509.UniformResourceIdentifier)
            extensions_list.append(extension.Extension(name, value))
            
        elif (ext._oid == ExtensionOID.AUTHORITY_KEY_IDENTIFIER):
            name = ext._oid._name
            identifier_bytes = ext.value.key_identifier
            value = identifier_bytes.hex()
            extensions_list.append(extension.Extension(name, value))
        
        elif (ext._oid == ExtensionOID.SUBJECT_KEY_IDENTIFIER):
            name = ext._oid._name
            identifier_bytes = ext.value._digest
            value = identifier_bytes.hex()
            extensions_list.append(extension.Extension(name, value))
        
        elif (ext._oid == ExtensionOID.EXTENDED_KEY_USAGE):
            name = ext._oid._name
            usages = ext.value
            usage_list = []

            for usage in usages:
                usage_list.append(usage._name)
            
            extensions_list.append(extension.Extension(name, usage_list))
        
        elif (ext._oid == ExtensionOID.KEY_USAGE):
            name = ext._oid._name
            ext_value = ext._value

            usage_list = []
            if (ext_value.digital_signature):
                usage_list.append("digital signature")
            if (ext_value.content_commitment):
                usage_list.append("content_commitment")
            if (ext_value.key_encipherment):
                usage_list.append("key_encipherment")
            if (ext_value.data_encipherment):
                usage_list.append("data_encipherment")
            if (ext_value.key_agreement):
                usage_list.append("key_agreement")
            if (ext_value.key_cert_sign):
                usage_list.append("key_cert_sign")
            if (ext_value.crl_sign):
                usage_list.append("crl_sign")
            if (ext_value._encipher_only):
                usage_list.append("encipher_only")
            if (ext_value._decipher_only):
                usage_list.append("decipher_only")

            extensions_list.append(extension.Extension(name, usage_list))

        elif (ext._oid == ExtensionOID.BASIC_CONSTRAINTS):
            name = ext._oid._name
            val = ext.value

            constraint_list = []
            constraint_list.append(f"CA: {val.ca}")
            constraint_list.append(f"Path length: {val.path_length if val.path_length is not None else 'None'}")

            extensions_list.append(extension.Extension(name, constraint_list))
        
    return extensions_list


def bytes_2_trustlist(data):
    offset = 0
    def read_u32():
        nonlocal offset
        if offset + 4 > len(data):
            raise ValueError("Buffer too small for u32")
        val = struct.unpack_from("<i", data, offset)[0]
        offset += 4
        return val

    def read_bytes():
        nonlocal offset
        length = struct.unpack_from("<i", data, offset)[0]
        offset += 4

        if length < 0:
            return None
        if offset + length > len(data):
            raise ValueError(f"Invalid length {length}, buffer too small")

        val = data[offset:offset+length]
        offset += length
        return val

    result = {}
    result["specified_lists"] = read_u32()

    cert_count = read_u32()
    certs = [read_bytes() for _ in range(cert_count)]
    result["trusted_certificates"] = certs

    crl_count = read_u32()
    crls = [read_bytes() for _ in range(crl_count)]
    result["trusted_crls"] = crls

    issuer_count = read_u32()
    issuers = [read_bytes() for _ in range(issuer_count)]
    result["issuers"] = issuers

    issuer_crl_count = read_u32()
    issuer_crls = [read_bytes() for _ in range(issuer_crl_count)]
    result["issuer_crls"] = issuer_crls

    return result

def trustlist_2_bytes(trustlist):
        def write_u32(val):
            return struct.pack("<i", val)

        def write_bytes(b):
            if b is None:
                return write_u32(-1)
            return write_u32(len(b)) + b

        out = bytearray()
        out += write_u32(trustlist["specifiec_lists"])
        certs = trustlist.get("trusted_certificates") or []
        out += write_u32(len(certs))
        for c in certs:
            out += write_bytes(c)

        crls = trustlist.get("trusted_crls") or []
        out += write_u32(len(crls))
        for c in crls:
            out += write_bytes(c)

        issuers = trustlist.get("issuers") or []
        out += write_u32(len(issuers))
        for c in issuers:
            out += write_bytes(c)

        issuer_crls = trustlist.get("issuer_crls") or []
        out += write_u32(len(issuer_crls))
        for c in issuer_crls:
            out += write_bytes(c)

        return bytes(out)

def cert_bytes_2_certSummary(cert):
    x509_cert = x509.load_der_x509_certificate(cert)
    subject_name = x509_cert.subject
    common_name = subject_name.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    issuer_name = x509_cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    return certSummary.CertSummary(common_name, issuer_name, cert_id(x509_cert))

def crl_2_crlSummary(revocation_list):
    x509_crl = x509.load_der_x509_crl(revocation_list)    
    issuer_name = x509_crl.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    return crl.Crl(issuer_name, [r.serial_number for r in x509_crl])

def get_certs_and_trustlist(cert, trustlist_bytes):

    trustlists = bytes_2_trustlist(trustlist_bytes)
    trusted_certs = trustlists["trusted_certs"]
    trusted_crls = trustlists["trusted_crls"]
    ua_cert = x509.load_der_x509_certificate(cert.Certificate)

    result_cert = bytes_2_cert(cert.Certificate)
    result_trustlist = []
    trustlist_certs = {}

    for trusted_crl in trusted_crls:

        crl = x509.load_der_x509_crl(trusted_crl)
        cert_serial = ua_cert.serial_number

        is_revoked = any(
            revoked.serial_number == cert_serial
            for revoked in crl
        )
        
        if is_revoked:
            result_cert[0].revoked = True
        
        for trusted_cert_bytes in trusted_certs:
            trusted_cert = bytes_2_cert(trusted_cert_bytes)
            trustlist_certs[trusted_cert[1]] = trusted_cert[0]
    
    result_trustlist = trustlist.TrustList(trustlist_certs)
    result = (result_cert, result_trustlist)
    
    return result
            
def cert_id(cert: x509):
    return cert.fingerprint(hashes.SHA256()).hex()