import model.application as application
import model.certificateGroup as certificateGroup
import model.structures as structures

class Domain:
    def __init__(self,
                 applications
            ):
        self.applications = applications

    def add_application(self, application: application.Application):
        self.applications.append(application)

    def __repr__(self):
        return f"Domain: (Applications: {self.applications})"
