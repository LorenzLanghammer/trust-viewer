
class Extension:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"{self.name}: {self.value}"

    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value
        }