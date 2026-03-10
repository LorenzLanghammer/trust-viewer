class Application:
    def __init__(self, 
                 applicationuri: str, 
                 names: list[str], 
                 discoveryurls: list[str],
                 certificate_groups: list[str]
            ):
        self.applicationuri = applicationuri
        self.names = names
        self.discoveryurls = discoveryurls
        self.certificate_groups = certificate_groups


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