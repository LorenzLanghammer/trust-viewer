from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding
import hashlib
import struct
from pathlib import Path




def encode_trustlist_with_trusted_crls(crl_bytes_list):
    parts = []
    # specifiedLists (UInt32) — Bit1 = trustedCrls
    parts.append(struct.pack('<I', 0x02))
    # trustedCertificatesSize (Int32) — no certs supplied
    parts.append(struct.pack('<i', 0))
    # trustedCertificates[]: (none)
    # trustedCrlsSize (Int32)
    parts.append(struct.pack('<i', len(crl_bytes_list)))
    # trustedCrls[]: each UA_ByteString = Int32 length + bytes
    for crl in crl_bytes_list:
        parts.append(struct.pack('<i', len(crl)))
        parts.append(crl)
    # issuerCertificatesSize (Int32) — none
    parts.append(struct.pack('<i', 0))
    # issuerCrlsSize (Int32) — none
    parts.append(struct.pack('<i', 0))
    return b''.join(parts)

crl = Path("ca4/gds_ca_crl.der").read_bytes()
payload = encode_trustlist_with_trusted_crls([crl])
crl_hex = payload.hex()
print(crl_hex)


import struct

def encode_trustlist(certs, crls):
    out = bytearray()

    specified = 0
    if certs:
        specified |= 0x01
    if crls:
        specified |= 0x02

    out += struct.pack("<I", specified)

    # trustedCertificates
    out += struct.pack("<i", len(certs))
    for cert in certs:
        out += struct.pack("<i", len(cert))
        out += cert

    # trustedCRLs
    out += struct.pack("<i", len(crls))
    for crl in crls:
        out += struct.pack("<i", len(crl))
        out += crl

    # issuerCertificates
    out += struct.pack("<i", 0)

    # issuerCRLs
    out += struct.pack("<i", 0)

    return bytes(out)
