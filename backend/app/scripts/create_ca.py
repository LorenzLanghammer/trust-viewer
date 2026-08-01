from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import Encoding
import datetime

def generate_ca(common_name, ca_file, key_file, crl_file):
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME,"DE"),
        x509.NameAttribute(NameOID.COUNTRY_NAME, "DE"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "BW"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        )).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(key.public_key()),
            critical = False
        ).add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(key.public_key()),
            critical = False
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical = True
        ).sign(key, hashes.SHA256())


    now = datetime.datetime.now(datetime.UTC)
    crl_builder = (
        x509.CertificateRevocationListBuilder()
        .issuer_name(cert.subject)
        .last_update(now)
        .next_update(now + datetime.timedelta(days=7))
    )

    crl = crl_builder.sign(
        private_key=key,
        algorithm=hashes.SHA256()
    )

    with open(ca_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.DER))

    with open(key_file, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(crl_file, "wb") as f:
        f.write(crl.public_bytes(serialization.Encoding.DER))

    return (
        cert, 
        key,
        crl
    )

def generate_intermediate_ca(common_name, issuer_cert, issuer_key):
    intermediate_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "DE"),
        x509.NameAttribute(NameOID.COUNTRY_NAME, "DE"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "BW"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    intermediate_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer_cert.subject)
        .public_key(intermediate_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        )).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(intermediate_key.public_key()),
            critical = False
        ).add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(issuer_key.public_key()),
            critical = False
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical = True
        ).sign(issuer_key, algorithm=hashes.SHA256())
    
    now = datetime.datetime.now(datetime.UTC)
    crl_builder = (
        x509.CertificateRevocationListBuilder()
        .issuer_name(intermediate_cert.subject)
        .last_update(now)
        .next_update(now + datetime.timedelta(days=7))
    )

    intermediate_crl = crl_builder.sign(
        private_key=intermediate_key,
        algorithm=hashes.SHA256()
    )

    return intermediate_cert, intermediate_key, intermediate_crl

def generate_csr(common_name, private_key):
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "DE"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])
    csr_builder = x509.CertificateSigningRequestBuilder().subject_name(subject)

    csr_builder = csr_builder.add_extension(
        x509.KeyUsage(
            digital_signature=False,
            content_commitment=False,
            key_encipherment=True,
            data_encipherment=True,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True
    )
    csr_builder = csr_builder.add_extension(
        x509.ExtendedKeyUsage([
            ExtendedKeyUsageOID.SERVER_AUTH
        ]),
        critical=False
    )
    csr_builder = csr_builder.add_extension(
        x509.SubjectAlternativeName([
            x509.UniformResourceIdentifier(common_name + ":uri")
        ]),
        critical=False
    )
    csr = csr_builder.sign(
        private_key,
        hashes.SHA256()
    )
    return csr


def sign_csr(csr, issuer_cert, issuer_key, days_valid=365):
    if not csr.is_signature_valid:
        raise ValueError("CSR signature is invalid")

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(csr.subject)
    builder = builder.issuer_name(issuer_cert.subject)
    builder = builder.public_key(csr.public_key())
    builder = builder.serial_number(x509.random_serial_number())

    now = datetime.datetime.now(datetime.timezone.utc)
    builder = builder.not_valid_before(now)
    builder = builder.not_valid_after(now + datetime.timedelta(days=days_valid))

    for ext in csr.extensions:
        builder = builder.add_extension(ext.value, critical=ext.critical)

    builder = builder.add_extension(
        x509.AuthorityKeyIdentifier.from_issuer_public_key(issuer_cert.public_key()),
        critical=False,
    )
    builder = builder.add_extension(
        x509.SubjectKeyIdentifier.from_public_key(csr.public_key()),
        critical=False,
    )

    certificate = builder.sign(
        private_key=issuer_key,
        algorithm=hashes.SHA256(),
    )
    return certificate

def add_revocation_to_crl(ca_cert, ca_key, old_crl, serial_to_revoke, revocation_date=None, days_valid=365):
    now = datetime.datetime.now(datetime.timezone.utc)
    revocation_date = revocation_date or now

    builder = x509.CertificateRevocationListBuilder()
    builder = builder.issuer_name(ca_cert.subject)
    builder = builder.last_update(now)
    builder = builder.next_update(now + datetime.timedelta(days=days_valid))

    for revoked in old_crl:
        builder = builder.add_revoked_certificate(revoked)

    new_entry = (
        x509.RevokedCertificateBuilder()
        .serial_number(serial_to_revoke)
        .revocation_date(revocation_date)
        .build()
    )
    builder = builder.add_revoked_certificate(new_entry)
    return builder.sign(private_key=ca_key, algorithm=hashes.SHA256())
    
def generate_crl(ca_cert, ca_key, revoked_serials=None, days_valid=365):
    now = datetime.datetime.now(datetime.timezone.utc)
    builder = x509.CertificateRevocationListBuilder()
    builder = builder.issuer_name(ca_cert.subject)
    builder = builder.last_update(now)
    builder = builder.next_update(now + datetime.timedelta(days=days_valid))

    for serial, revocation_date in (revoked_serials or []):
        revoked_cert = (
            x509.RevokedCertificateBuilder()
            .serial_number(serial)
            .revocation_date(revocation_date)
            .build()
        ) 
        builder = builder.add_revoked_certificate(revoked_cert)

    return builder.sign(private_key=ca_key, algorithm = hashes.SHA256)

def write_ca_files(ca_cert_path, ca_key_path, ca_crl_path, ca_cert, ca_key, ca_crl):

    with open (ca_cert_path, "wb") as gds_cert:
        gds_cert.write(ca_cert.public_bytes(encoding=Encoding.DER))

    with open (ca_key_path, "wb") as gds_key:
        gds_key.write(ca_key.private_bytes(format=serialization.PrivateFormat.PKCS8, encoding=Encoding.DER, encryption_algorithm=serialization.NoEncryption()))

    with open (ca_crl_path, "wb") as gds_crl:
        gds_crl.write(ca_crl.public_bytes(encoding=Encoding.DER))

app11_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )


'''
with open ("ca5/gds_ca_cert.der", "rb") as gds_cert:
    gds_cert = x509.load_der_x509_certificate(gds_cert.read())

with open ("ca5/gds_ca_key.der", "rb") as gds_key:
    gds_key = serialization.load_der_private_key(gds_key.read(), password=None)

(ica2_cert, ica2_key, ica2_crl) = generate_intermediate_ca("ica2", gds_cert, gds_key)

with open ("ica2/gds_ca_cert.der", "wb") as gds_cert:
    gds_cert.write(ica2_cert.public_bytes(encoding=Encoding.DER))

with open ("ica2/gds_ca_key.der", "wb") as gds_key:
    gds_key.write(ica2_key.private_bytes(encoding=Encoding.DER,   
                                         format=serialization.PrivateFormat.TraditionalOpenSSL,
                                         encryption_algorithm=serialization.NoEncryption()))

with open ("ica2/gds_ca_crl.der", "wb") as gds_crl:
    gds_crl.write(ica2_crl.public_bytes(encoding=Encoding.DER))
'''



'''
csr = generate_csr("app18", app18_key)
with open ("ica1/app18_req.der", "wb") as app18_req:
    app18_req.write(csr.public_bytes(encoding=Encoding.DER))
'''