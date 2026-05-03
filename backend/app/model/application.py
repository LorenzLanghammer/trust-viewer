import model.structures as structures
import model.certificate as certificate

class Application:
    def __init__(self,
                 node_id,
                 applicationuri, 
                 names, 
                 discoveryurls,
                 issued_certificates,
                 trustlists
            ):
        self.node_id = node_id
        self.applicationuri = applicationuri
        self.names = names
        self.discoveryurls = discoveryurls
        self.issued_certificates = issued_certificates
        self.trustlists = trustlists

    def __repr__(self):
        return f"nodeId: {self.node_id}, applicationuri: {self.applicationuri}, names: {self.names}"
    
    def __eq__(self, other):
        if not isinstance(other, Application):
            return False

        if hasattr(self.node_id, "namespace") and hasattr(self.node_id, "id"):
            return (self.node_id.namespace, self.node_id.id) == (other.node_id.namespace, other.node_id.id)
        return self.applicationuri == other.applicationuri

    def __hash__(self):
        if hasattr(self.node_id, "namespace") and hasattr(self.node_id, "id"):
            return hash((self.node_id.namespace, self.node_id.id))
        return hash(self.applicationuri)
    