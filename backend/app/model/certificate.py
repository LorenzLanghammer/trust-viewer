class Certificate:
    def __init__(self, 
                 id: int, 
                 public_key: str, 
                 name: str,
                 extensions: list[str]
            ):
        self.id = id
        self.public_key = public_key
        self.name = name
        self.extensions = extensions   