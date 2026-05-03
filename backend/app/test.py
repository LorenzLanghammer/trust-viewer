from crypto import cryptofunctions
from model import structures
from model import domain
from domain_builder import *
from opcua.gdsInterface import open62541GDS
from asyncua import Client
import asyncio

async def test():
    gds_url = "opc.tcp://localhost:4840"
    client = Client(gds_url)
    #await client.connect()

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
                                structures.NodeId(3, 7009),
                                structures.NodeId(2, 508)
                                )

    await gds_interface.connect()
    applications = await gds_interface.getApplicationInfos()
    applications_dict = {}

    domains = []
    
    for app in applications:
        applications_dict[app.node_id] = {}
    
    for i, first_app in enumerate(applications):
        for j in range(i, len(applications)):
            if (i == j):
                applications_dict[first_app.node_id][first_app.node_id] = True
                continue

            second_app = applications[j]

            trusts_1_to_2 = cryptofunctions.verify_certs_against_trustlists(
                first_app.issued_certificates,
                second_app.trustlists
            )

            trusts_2_to_1 = cryptofunctions.verify_certs_against_trustlists(
                second_app.issued_certificates, 
                first_app.trustlists
            )

            if (trusts_1_to_2 and trusts_2_to_1):
                applications_dict[first_app.node_id][second_app.node_id] = True
                applications_dict[second_app.node_id][first_app.node_id] = True
                domains.append(domain.Domain([first_app, second_app]))
            else:
                applications_dict[first_app.node_id][second_app.node_id] = False


    result_domains = find_cliques(applications_dict)
    print(result_domains)
    
    
if __name__ == "__main__":
    asyncio.run(
        test()
    )