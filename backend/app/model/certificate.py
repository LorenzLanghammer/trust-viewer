
class Certificate:
    def __init__(self, 
                 public_key: str, 
                 name: str,
                 extensions: list[str],
                 revoked = False
            ):
        self.public_key = public_key
        self.name = name
        self.extensions = extensions   
        self.revoked = revoked
    
    def revoke_Cert(self):
        self.revoked = True
        
    def __repr__(self):
        return f"public_key: {self.public_key}, name: {self.name}, extensions: {self.extensions}, revoked: {self.revoked}"