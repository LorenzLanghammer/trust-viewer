class CertificateGroup:
    def __init__(self, 
                 name: str, 
                 certificate_type: str, 
                 trust_list: list[str], 
                 revocation_list: list[str]
            ):
        self.name = name
        self.certificate_type = certificate_type
        self.trust_list = trust_list
        self.revocation_list = revocation_list