from . import structures
from . import certificate
from . import certSummary
from .  import trustlist

class Application:
    def __init__(self,
                 node_id,
                 applicationuri, 
                 names, 
                 discoveryurls,
                 issued_certificates,
                 issued_certs_summaries: list[certSummary.CertSummary],
                 trustlists: list[trustlist.TrustList]
            ):
        self.node_id = node_id
        self.applicationuri = applicationuri
        self.names = names
        self.discoveryurls = discoveryurls
        self.issued_certificates = issued_certificates
        self.issued_certs_summaries = issued_certs_summaries
        self.trustlists = trustlists

    def __repr__(self):
        return f"(nodeId: {self.node_id}, applicationuri: {self.applicationuri}, names: {self.names})"
    
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
    
    def to_dict(self):
        return {
            "node_id": {
                "namespace": self.node_id.namespace,
                "id": self.node_id.id
            },
            "applicationuri": self.applicationuri,
            "name": self.names.Text if hasattr(self.names, "Text") else str(self.names),
            "locale": self.names.Locale if hasattr(self.names, "Locale") else "",
            "discoveryurls": self.discoveryurls,
            "issued_certificates": [
                str(c) for c in self.issued_certificates
            ],
            "issued_certs_summaries": [
                summary.to_dict()
                for summary in self.issued_certs_summaries
            ],
            "trustlists": [
                str(t) for t in self.trustlists
            ]
        }