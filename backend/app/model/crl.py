
class Crl:
    def __init__(self, 
                 issuer: str,
                 revoked: list[int]
            ):
        self.revoked = revoked
        self.issuer = issuer

    def __repr__(self):
        return f"serials: {self.revoked}, issuer: {self.issuer}"
    
    def to_dict(self):
        return {"issuer": self.issuer, "revoked": [r for r in self.revoked]}