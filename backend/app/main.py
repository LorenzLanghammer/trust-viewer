from fastapi import FastAPI
from asyncua import Client, ua
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from opcua.gdsInterface import open62541GDS
from model import structures, domain, certificateGroup, application
from crypto import cryptofunctions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/opcuaconnect")
async def opcuaconnect():
    print("Connecting to OPC UA server...")


async def main():
    gds_url = "opc.tcp://localhost:4840"
    client = Client(gds_url)

    gds_interface = open62541GDS(client,
                                structures.NodeId(3, 5005),
                                structures.NodeId(2, 141),
                                structures.NodeId(3, 5004),
                                structures.NodeId(3, 7020),
                                structures.NodeId(3, 7011),
                                structures.NodeId(2, 204),
                                structures.NodeId(3, 7019),
                                structures.NodeId(3, 7010),
                                structures.NodeId(3, 7014),
                                structures.NodeId(3, 7009)
                                )
    await gds_interface.connect()
 
    applications = []
    certificate_groups = await gds_interface.getCertificateGroups()
    domains = [] * len(certificate_groups)

    group_details = await gds_interface.getCertificateGroupAssignments(certificate_groups)
    for group_detail in group_details:
        trustlist = await gds_interface.readTrustList(structures.uaNodeId_2_nodeid(group_detail.TrustList))
        new_domain = domain.Domain(structures.uaNodeId_2_nodeid(group_detail.CertificateGroupId))

        for app in group_detail.Applications:
            app_id = structures.uaNodeId_2_nodeid(app)
            app_detail = await gds_interface.getApplicationDetails(structures.uaNodeId_2_nodeid(app))
            application_info = app_detail[0]

            newApplication = application.Application(structures.uaNodeId_2_nodeid(application_info.Application.ApplicationId), 
                                                         application_info.Application.ApplicationUri, 
                                                         application_info.Application.ApplicationNames, 
                                                         application_info.Application.DiscoveryUrls)   

            certs = await gds_interface.getCertificates(app_id, structures.uaNodeId_2_nodeid(group_detail.CertificateGroupId))
            result = cryptofunctions.get_certs_and_trustlist(certs[0], trustlist)

            if result[0]:
                if not result[0][0].revoked:
                    new_domain.add_application(newApplication)

        domains.append(new_domain)
    print(domains)

if __name__ == "__main__":
    asyncio.run(
        main()
    )