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
