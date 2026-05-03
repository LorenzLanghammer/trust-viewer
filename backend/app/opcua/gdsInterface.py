
from abc import ABC, abstractmethod
from model import application, certificate, domain, certificateGroup, trustlist, structures
from crypto import cryptofunctions
from asyncua import Client, ua

class GdsInterface(ABC):
    @abstractmethod
    async def connect(self):
        pass
    @abstractmethod
    async def disconnect(self):
        pass
    @abstractmethod
    async def getApplicationInfos(self):
        pass
    @abstractmethod
    async def getCertificateGroups(self):
        pass
    @abstractmethod 
    async def getTrustList(self, applicationId: structures.NodeId, certificateGroupId: structures.NodeId):
        pass
    @abstractmethod
    async def getCertificateGroupAssignments(self, certificate_groups: list[certificateGroup.CertificateGroup]):
        pass
    @abstractmethod
    async def getApplicationDetails(self, applicationId: structures.NodeId):
        pass
    @abstractmethod
    async def getCertificates(self, aplicationId: structures.NodeId, certificateGroupId: structures.NodeId):
        pass
    @abstractmethod
    async def readTrustList(self, nodeId: structures.NodeId):
        pass



class open62541GDS(GdsInterface):
    def __init__(self, 
                 client, 
                 registration_mgmt: structures.NodeId, 
                 directory: structures.NodeId,
                 certificate_management_node: structures.NodeId,
                 get_applications: structures.NodeId,
                 get_certificate_groups: structures.NodeId,
                 get_trustlist: structures.NodeId,
                 get_application_details: structures.NodeId,
                 get_certificate_group_details: structures.NodeId,
                 get_certificates: structures.NodeId,
                 get_certificate_details: structures.NodeId,
                 get_certificate_groups_for_app: structures.NodeId
                 ):
        self.client = client
        self.registration_mgmt = registration_mgmt
        self.directory = directory
        self.certificate_management_node = certificate_management_node
        self.get_applications = get_applications
        self.get_certificate_groups = get_certificate_groups
        self.get_trustlist = get_trustlist
        self.get_application_details = get_application_details
        self.get_certificate_group_details = get_certificate_group_details
        self.get_certificates = get_certificates
        self.get_certificate_details = get_certificate_details
        self.get_certificate_groups_for_app = get_certificate_groups_for_app


    async def connect(self):
        print("Connecting to OPC UA server...")

        try:
            await self.client.connect()
            await self.client.load_type_definitions()
        except Exception as e:
            print("error: " + str(e))
            return {"error": str(e)}
        
    async def disconnect(self):
        await self.client.disconnect()
         
    async def getApplicationInfos(self) -> list[application.Application]:

        registration_mgmt = structures.nodeid_2_uaNode(self.registration_mgmt, self.client)
        get_apps_method = structures.nodeid_2_uaNode(self.get_applications, self.client)
        get_app_details_method = structures.nodeid_2_uaNode(self.get_application_details, self.client)
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
            nodeId = app.Application.ApplicationId
            id = structures.NodeId(nodeId.NamespaceIndex, nodeId.Identifier)
            appuri = app.Application.ApplicationUri
            appname = app.Application.ApplicationNames[0]
            discoveryurl = app.Application.DiscoveryUrls[0]
            certinfos = await self.getCertificates(id, structures.NodeId(0, 0))
            issued_certs = [certinfo.Certificate for certinfo in certinfos]
            trustlists = []

            certificate_groups = await self.getCertificateGroupsForApplication(id)

            for certificate_group in certificate_groups:
                trustlist = await self.getTrustList(id, structures.uaNodeId_2_nodeid(certificate_group))
                trustlist_bytes = await self.readTrustList(structures.uaNodeId_2_nodeid(trustlist))
                trustlists.append(cryptofunctions.bytes_2_trustlist(trustlist_bytes))
            
            all_applications.append(application.Application(id, appuri, appname, discoveryurl, issued_certs, trustlists))

        return all_applications

    async def getCertificateGroupsForApplication(self, applicationId: structures.NodeId):
        applicationId_node = structures.nodeid_2_uaNodeId(applicationId)
        directory_node = structures.nodeid_2_uaNode(self.directory, self.client)
        get_certificate_grous_for_app_method = structures.nodeid_2_uaNode(self.get_certificate_groups_for_app, self.client)

        certificate_groups_for_app = await directory_node.call_method(
            get_certificate_grous_for_app_method,
            ua.Variant(applicationId_node, ua.VariantType.NodeId)
        )

        return certificate_groups_for_app

        
    async def getCertificateGroups(self):
        
        certificate_management : ua.NodeId = self.client.get_node(ua.NodeId(5004, 3))
        get_certificate_groups_method = self.client.get_node(ua.NodeId(7011, 3))
        starting_id = ua.NodeId(0, 0)

        groups = await certificate_management.call_method(
            get_certificate_groups_method,
            ua.Variant(starting_id, ua.VariantType.NodeId),
            ua.Variant(starting_id, ua.VariantType.NodeId),
            ua.Variant(50, ua.VariantType.UInt32)          
        )
        return groups
    

    async def getCertificateGroupAssignments(self, certificateGroups: list):
        certificate_manager = structures.nodeid_2_uaNode(self.certificate_management_node, self.client)
        get_certificate_group_details_node = structures.nodeid_2_uaNode(self.get_certificate_group_details, self.client)
        
        certificate_group_details = await certificate_manager.call_method(
            get_certificate_group_details_node,
            ua.Variant(certificateGroups, ua.VariantType.NodeId)
        )
        return certificate_group_details

    
    async def getTrustList(self, applicationId: structures.NodeId, certificateGroupId: structures.NodeId):
        
        applicationId_node = structures.nodeid_2_uaNodeId(applicationId)
        certificateGroupId_node = structures.nodeid_2_uaNodeId(certificateGroupId)
        directory_node = structures.nodeid_2_uaNode(self.directory, self.client)
        get_trustlist_node = structures.nodeid_2_uaNode(self.get_trustlist, self.client)

        list = await directory_node.call_method(
            get_trustlist_node,
            ua.Variant(applicationId_node, ua.VariantType.NodeId),
            ua.Variant(certificateGroupId_node, ua.VariantType.NodeId)
        )
        return list


    async def getApplicationDetails(self, applicationId):
        applicationId_node = structures.nodeid_2_uaNodeId(applicationId)
        get_application_details_node = structures.nodeid_2_uaNode(self.get_application_details, self.client)
        registration_management = structures.nodeid_2_uaNode(self.registration_mgmt, self.client)

        app_details = await registration_management.call_method(
            get_application_details_node,
            ua.Variant([applicationId_node], ua.VariantType.NodeId)
        )
        return app_details

    async def getCertificates(self, applicationId, certificateGroupId):
        certificate_management_node = structures.nodeid_2_uaNode(self.certificate_management_node, self.client)
        get_certificates_node = structures.nodeid_2_uaNode(self.get_certificates, self.client)
        applicationId_node = structures.nodeid_2_uaNodeId(applicationId)
        certificateGroupId_node = structures.nodeid_2_uaNodeId(certificateGroupId)
        starting_id = ua.NodeId(0, 0)

        certnodes = await certificate_management_node.call_method(
           get_certificates_node,
           ua.Variant(certificateGroupId_node, ua.VariantType.NodeId),
           ua.Variant(applicationId_node, ua.VariantType.NodeId),
           ua.Variant(starting_id, ua.VariantType.NodeId),
           ua.Variant(50, ua.VariantType.UInt32)          
        )

        #certs = []
        get_certificate_details_node = structures.nodeid_2_uaNode(self.get_certificate_details, self.client)
        cert_details = await certificate_management_node.call_method(
            get_certificate_details_node,
            ua.Variant(certnodes, ua.VariantType.NodeId)
        )
        
        '''
        for cert_detail in cert_details:
            cert = cryptofunctions.bytes_2_cert(cert_detail.Certificate)
            certs.append(cert)
        '''

        return cert_details
    
    async def readTrustList(self, nodeId: structures.NodeId):
        trustlist_node = structures.nodeid_2_uaNode(nodeId, self.client)
        open_node = await trustlist_node.get_child(ua.QualifiedName("Open", 0))
        handle = await trustlist_node.call_method(
            open_node,
            ua.Variant(1, ua.VariantType.Byte)
        )

        read_node = await trustlist_node.get_child(ua.QualifiedName("Read", 0))
        
        
        data = b""
        chunk_size = 1024
        while True:
            chunk = await trustlist_node.call_method(
                read_node,
                ua.Variant(handle, ua.VariantType.UInt32),
                ua.Variant(chunk_size, ua.VariantType.Int32)
            )
            
            if not chunk:
                break

            data += chunk
            if len(chunk) < chunk_size:
                break


        close_node = await trustlist_node.get_child(ua.QualifiedName("Close", 0))
        
        await trustlist_node.call_method(
            close_node,
            ua.Variant(handle, ua.VariantType.UInt32),
        )
        
        #trustlist = cryptofunctions.bytes_2_trustlist(trustlist_bytes)
        return(data)
    
