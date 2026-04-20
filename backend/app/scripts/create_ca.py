from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
import datetime


key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME,"DE"),
    x509.NameAttribute(NameOID.COUNTRY_NAME, "DE"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "BW"),
    x509.NameAttribute(NameOID.COMMON_NAME, "ca2"),
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


with open("gds_ca_cert.der", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.DER))

with open("gds_ca_key.der", "wb") as f:
    f.write(
        key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

with open("gds_ca_crl.der", "wb") as f:
    f.write(crl.public_bytes(serialization.Encoding.DER))
