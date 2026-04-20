import model.application as application
import model.certificateGroup as certificateGroup
import model.structures as structures

class Domain:
    def __init__(self, 
                 certificate_group_id: structures.NodeId,
            ):
        self.applications = []
        self.certificate_group_id = certificate_group_id

    def add_application(self, application: application.Application):
        self.applications.append(application)

    def __repr__(self):
        return f"Domain: (Applications: {self.applications}, CertificateGroup: {self.certificate_group_id})"
