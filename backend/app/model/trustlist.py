from . import crl
from . import certSummary

class TrustList:
    def __init__(self, 
                 trustedCertificates: list[certSummary.CertSummary],
                 trustedCrls: list[crl.Crl],
                 issuerCertificates: list[certSummary.CertSummary],
                 issuerCrls: list[crl.Crl]
            ):
        self.trustedCertificates = trustedCertificates
        self.trustedCrls = trustedCrls
        self.issuerCertificates = issuerCertificates
        self.issuerCrls = issuerCrls
    
    def __repr__(self):
        return f"trusted certificates: {self.trustedCertificates}, trusted crls: {self.trustedCrls}, issuers: {self.issuerCrls}, issuer certificates: {self.issuerCertificates}, issuer crls: {self.issuerCrls}"
    
    def to_dict(self):
        return {
            "trustedCertificates": self.trustedCertificates, 
            "trustedCrls": [crl.to_dict() for crl in self.trustedCrls], 
            "issuerCertificates": self.issuerCertificates, 
            "issuerCrls": [crl.to_dict() for crl in self.issuerCrls]
            }