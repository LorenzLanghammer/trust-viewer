class Domain:
    def __init__(self, 
                 applications: list[str],
                 trustlists: list[str],
            ):
        self.applications = applications
        self.trustlists = trustlists