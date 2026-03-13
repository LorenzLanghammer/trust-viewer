class TrustList:
    def __init__(self, 
                 id: int,
                 certificates: list[str]
            ):
        self.id = id
        self.certificates = certificates