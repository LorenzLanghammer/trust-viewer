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

crl = Path("ca2/crl.der").read_bytes()
payload = encode_trustlist_with_trusted_crls([crl])
crl_hex = payload.hex()
print(crl_hex)

