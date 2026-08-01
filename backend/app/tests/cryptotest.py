from app.scripts.create_ca import generate_ca, generate_csr, sign_csr, generate_intermediate_ca, add_revocation_to_crl
import app.crypto.cryptofunctions as cryptofunctions
from cryptography.hazmat.primitives.serialization import Encoding
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa


tests_dir = Path(__file__).resolve().parent

new_ca = generate_ca(
    "My CA",
    str(tests_dir/ "new_ca" / "new_ca.der"),
    str(tests_dir / "new_ca" / "new_key.der"),
    str(tests_dir / "new_ca" / "new_crl.der"),
)

def build_trustlist(trusted_certs=None, issuer_certs=None, trusted_crls=None, issuer_crls=None):
    def to_der_list(items):
        return [c.public_bytes(Encoding.DER) for c in (items or [])]
    return {
        "trusted_certificates": to_der_list(trusted_certs),
        "issuer_certificates": to_der_list(issuer_certs),
        "trusted_crls": to_der_list(trusted_crls),
        "issuer_crls": to_der_list(issuer_crls),
    }

new_ca_certificate, new_ca_key, new_ca_crl = new_ca

new_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
new_csr = generate_csr("app1", new_key)
new_cert = sign_csr(new_csr, new_ca_certificate, new_ca_key)
cert_der = new_cert.public_bytes(Encoding.DER)
trustlist1 = build_trustlist(
    trusted_certs=[new_ca_certificate],
    trusted_crls=[new_ca_crl],
    issuer_certs=[],
    issuer_crls=[]
)

#Test simple certificate validation for certificate issued by root ca
assert(cryptofunctions.verify_cert(cert_der, trustlist1))

csr2= generate_csr("app2", new_key)
intermediate_ca1_cert, intermediate_ca1_key, intermediate_ca1_crl = generate_intermediate_ca("ica1", new_ca_certificate, new_ca_key)
cert2 = sign_csr(csr2, intermediate_ca1_cert, intermediate_ca1_key)
cert2_der = cert2.public_bytes(Encoding.DER)
trustlist2 = build_trustlist(
    trusted_certs=[new_ca_certificate],
    trusted_crls=[new_ca_crl],
    issuer_certs=[intermediate_ca1_cert],
    issuer_crls = [intermediate_ca1_crl]
)

#Test certificate validation for certificate issued by intermediate ca
assert(cryptofunctions.verify_cert(cert2_der, trustlist2))

csr3 = generate_csr("app3", new_key)
intermediate_ca2_cert, intermediate_ca2_key, intermediate_ca2_crl = generate_intermediate_ca("ica2", new_ca_certificate, new_ca_key)
cert3 = sign_csr(csr3, intermediate_ca2_cert, intermediate_ca2_key)
cert3_der = cert3.public_bytes(Encoding.DER)
new_crl = add_revocation_to_crl(intermediate_ca2_cert, intermediate_ca2_key, intermediate_ca2_crl, cert3.serial_number)
trustlist3 = build_trustlist(
    trusted_certs=[new_ca_certificate],
    trusted_crls=[new_ca_crl],
    issuer_certs=[intermediate_ca2_cert],
    issuer_crls=[new_crl]
)

#Test certificate revoked in intermediate cas crl
assert(cryptofunctions.verify_cert(cert3_der, trustlist3) == False)

csr4 = generate_csr("app4", new_key)
intermediate_ca3_cert, intermediate_ca3_key, intermediate_ca3_crl = generate_intermediate_ca("ica3", new_ca_certificate, new_ca_key)
cert4 = sign_csr(csr4, intermediate_ca3_cert, intermediate_ca3_key)
cert4_der = cert4.public_bytes(Encoding.DER)
new_crl = add_revocation_to_crl(new_ca_certificate, new_ca_key, new_ca_crl, intermediate_ca3_cert.serial_number)
trustlist4 = build_trustlist(
    trusted_certs=[new_ca_certificate],
    trusted_crls=[new_crl],
    issuer_certs=[intermediate_ca3_cert],
    issuer_crls=[intermediate_ca3_crl]
)

#Test intermediate ca certificate revoked in crl of root ca
assert(cryptofunctions.verify_cert(cert4_der, trustlist4) == False)

csr5 = generate_csr("app5", new_key)
cert5 = sign_csr(csr5, new_ca_certificate, new_ca_key)
cert5_der = cert5.public_bytes(Encoding.DER)
trustlist5 = build_trustlist(
    trusted_certs=[cert5],
    trusted_crls=[new_ca_crl],
    issuer_certs=[],
    issuer_crls=[]
)

assert(cryptofunctions.verify_cert(cert5_der, trustlist5))