
class Certificate:
    def __init__(self, 
                 serial,
                 public_key: str, 
                 name: str,
                 issuer: str,
                 not_before: str,
                 not_after: str,
                 extensions: list[str],
                 revoked = False
            ):
        self.serial = serial
        self.public_key = public_key
        self.name = name
        self.issuer = issuer
        self.not_before = not_before
        self.not_after = not_after
        self.extensions = extensions   
        self.revoked = revoked
    
    def revoke_Cert(self):
        self.revoked = True
    
    def to_dict(self):
        return {
            "serial": self.serial,
            "key": self.public_key,
            "name": self.name,
            "issuer": self.issuer,
            "notbefore": self.not_before,
            "notafter": self.not_after,
            "extensions": [ext.to_dict() for ext in self.extensions]
        }

    def __repr__(self):
        return f"serial: {self.serial}, public_key: {self.public_key}, name: {self.name}, issuer: {self.issuer}, notbefore: {self.not_before}, notafter: {self.not_after} extensions: {self.extensions}, revoked: {self.revoked}"