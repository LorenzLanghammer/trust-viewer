from . import trustlist

class CertificateGroup:
    def __init__(self, 
                 node_id,
                 name, 
                 certificate_type, 
                 trust_list: trustlist.TrustList, 
            ):
        self.node_id = node_id
        self.name = name
        self.certificate_type = certificate_type
        self.trust_list = trust_list

    def __repr__(self):
        return f"nodeId: {self.node_id}, name: {self.name}, certificateType: {self.certificate_type}, trustList: {[cert for cert in self.trust_list]}"
    
    def to_dict(self):
        return {
            "nodeId": self.node_id,
            "name": self.name,
            "trust_list": self.to_dict(self.trust_list)
        }