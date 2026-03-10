
from abc import ABC, abstractmethod




@app.get("/opcuaconnect")
async def opcuaconnect():
    print("Connecting to OPC UA server...")
    gds_url = "opc.tcp://localhost:4840"
    client = Client(gds_url)
    client.set_user("admin")
    client.set_password("admin123")

    try:

        await client.connect()
        registration_mgmt = client.get_node(ua.NodeId(5005, 3))
        get_apps_method = client.get_node(ua.NodeId(7020, 3))
        get_app_details_method = client.get_node(ua.NodeId(7019, 3))

        await client.load_type_definitions()

        starting_id = ua.NodeId(0, 0)
        all_applications = []
        nodeids = await registration_mgmt.call_method(
                get_apps_method,
                ua.Variant(starting_id, ua.VariantType.NodeId),
                ua.Variant(0, ua.VariantType.UInt32)          
            )

        apps = await registration_mgmt.call_method(
            get_app_details_method,
            nodeids 
        )
        
        for app in apps:
            all_applications.append((app.Application.ApplicationUri, app.Application.ApplicationNames[0].Text))
        
        return all_applications
    except Exception as e:
        print("error: " + str(e))
        return {"error": str(e)}




class GdsInterface(ABC):
    @abstractmethod
    def connect(self):
        pass
    def disconnect(self):
        pass
    def getApplications(self):
        pass
    def getCertificateGroups(self):
        pass


class open62541GDS(GdsInterface):
    def __init__(self, client):
        self.client = client

    def connect(self):
        pass
    def disconnect(self):
        pass
    def getApplications(self):
        pass
    def getCertificateGroups(self):
        pass
