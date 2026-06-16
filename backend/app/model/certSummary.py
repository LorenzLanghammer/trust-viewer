
class CertSummary:
    def __init__(self, 
                 subject: str,
                 issuer: str,
                 fingerprint
            ):
        self.subject = subject
        self.issuer = issuer
        self.fingerprint = fingerprint


    def to_dict(self):
        return {
            "subject": self.subject,
            "issuer": self.issuer,
            "fingerprint": self.fingerprint
        }
    def __repr__(self):
        return f"subject: {self.subject} issuer: {self.issuer}"