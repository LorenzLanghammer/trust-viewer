from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "DE"),
    x509.NameAttribute(NameOID.COMMON_NAME, "app6"),
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
        x509.UniformResourceIdentifier("app6:uri")
    ]),
    critical=False
)

csr = csr_builder.sign(
    private_key,
    hashes.SHA256()
)

csr_der = csr.public_bytes(serialization.Encoding.DER)
print(csr_der)

with open("app6_req.der", "wb") as f:
    f.write(csr_der)

with open("app6.key", "wb") as f:
    f.write(
        private_key.private_bytes(
            serialization.Encoding.DER,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()
        )
    )