import model.certificateGroup as certificateGroup
import model.certificate as certificate

class TrustList:
    def __init__(self, 
                 trustedCertificates: dict[str, certificate.Certificate],
            ):
        self.trustedCertificates = trustedCertificates
    
    def __repr__(self):
        return f"certificates: {self.trustedCertificates}"