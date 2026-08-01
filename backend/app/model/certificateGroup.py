from . import trustlist

class CertificateGroup:
    def __init__(self, 
                 name, 
                 trust_list: trustlist.TrustList, 
            ):
        self.name = name
        self.trust_list = trust_list

    def __repr__(self):
        return f"name: {self.name}, trustList: {[cert for cert in self.trust_list]}"
    
    def to_dict(self):
        return {
            "name": self.name,
            "trust_list": self.to_dict(self.trust_list)
        }