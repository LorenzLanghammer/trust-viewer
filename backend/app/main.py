from fastapi import FastAPI
from asyncua import Client, ua
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from .opcua.gdsInterface import open62541GDS
from .model import structures, domain, certificateGroup, application
from .crypto import cryptofunctions
from .domain_builder import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # Allow all origins during development so the frontend (vite) can call the backend
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/opcuaconnect")
async def opcuaconnect():
    print("Connecting to OPC UA server...")
    try:
        result_domains = await main()

        if result_domains is None:
            return {"domains": []}
        
        print(result_domains)
        return {"domains": domains_to_json(result_domains)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"domains": None, "error": str(e)}


@app.get("/getCertificateGroups")
async def getcertificategroups():
    # Call OPC UA GDS to get certificate groups with proper connect/disconnect
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
                                structures.NodeId(3, 7009),
                                structures.NodeId(2, 508)
                                )

    print("Getting certificate groups")
    try:
        await gds_interface.connect()
        cert_groups = await gds_interface.getCertificateGroups()
        cert_group_details = await gds_interface.getCertificateGroupAssignments(cert_groups)

        if not hasattr(cert_group_details, '__iter__') or isinstance(cert_group_details, (str, bytes)):
            cert_group_details_list = [cert_group_details]
        else:
            try:
                cert_group_details_list = list(cert_group_details)
            except Exception:
                cert_group_details_list = [cert_group_details]

        groups_apps: list[list[dict]] = []
        for item in cert_group_details_list:
            apps = getattr(item, "Applications", []) or []
            group_apps: list[dict] = []
            for a in apps:
                try:
                    nid = nodeid_to_dict(a)
                except Exception:
                    nid = {"namespace": None, "id": str(a)}
                group_apps.append(nid)
            groups_apps.append(group_apps)

        print(groups_apps)
        return {"status": "ok", "groups": groups_apps}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}
    finally:
        try:
            await gds_interface.disconnect()
        except Exception:
            pass


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
    return result_domains



def nodeid_to_dict(nodeid):
    if nodeid is None:
        return {"namespace": None, "id": None}

    if hasattr(nodeid, "namespace") and hasattr(nodeid, "id"):
        ns = nodeid.namespace
        idv = nodeid.id
    elif hasattr(nodeid, "NamespaceIndex") and hasattr(nodeid, "Identifier"):
        ns = nodeid.NamespaceIndex
        idv = nodeid.Identifier
    else:
        try:
            ns, idv = nodeid
        except Exception:
            ns = None
            idv = str(nodeid)

    return {"namespace": ns, "id": idv}

def domains_to_json(result_domains):
    if not result_domains:
        return []

    return [
        [nodeid_to_dict(node) for node in domain]
        for domain in result_domains
    ]


if __name__ == "__main__":
    asyncio.run(
        main()
    )