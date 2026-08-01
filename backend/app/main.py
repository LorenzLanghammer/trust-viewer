from fastapi import FastAPI
from asyncua import Client, ua
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from .opcua.gdsInterface import open62541GDS
from .model import structures, domain, certificateGroup, application, certSummary, trustlist
from .crypto import cryptofunctions
from .domain_builder import *
from cryptography.x509.oid import NameOID


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

applications_list = []
application_store = {}
certificates_store = {}
trustlists_store = {}
group_store = {}
crl_store = {}


@app.get("/getcertificate/{certificate_id}")
async def getcertificates(certificate_id: str):
    certificate = certificates_store[certificate_id]
    certificate_dict = certificate.to_dict()
    return certificate.to_dict()


@app.get("/getapplication/{app_id}")
async def getapplication(app_id: int):
    application = application_store[app_id]
    return application.to_dict()


@app.get("/trustlist/{group_id}")
async def get_trustlist(group_id: int):
    trustlist = trustlists_store[group_id]
    return(trustlist.to_dict())

@app.get("/getcertgroups/{group_id}")
async def get_certgroup(group_id: int):
    group = group_store[group_id]
    return(group.to_dict())

@app.get("/getcrl/{crl_id}")
async def get_crl(crl_id: int):
    print("get crl")


@app.get("/opcuaconnect")
async def opcuaconnect():

    try:
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

        all_applications = await gds_interface.getApplicationInfos()
        all_x509 = await gds_interface.getCertificates(structures.NodeId(0, 0), structures.NodeId(0, 0))

        for x509 in all_x509:
            global certificates_store
            certificate, fingerprint = cryptofunctions.bytes_2_cert(x509.Certificate)
            certificates_store[fingerprint] = certificate

        global applications_list
        applications_list = []

        for app in all_applications:
            nodeId = app.Application.ApplicationId
            id = structures.NodeId(nodeId.NamespaceIndex, nodeId.Identifier)
            appuri = app.Application.ApplicationUri
            appname = app.Application.ApplicationNames[0]
            discoveryurl = app.Application.DiscoveryUrls[0]
            certinfos = await gds_interface.getCertificates(id, structures.NodeId(0, 0))
            issued_certs = [certinfo.Certificate for certinfo in certinfos]
            
            cert_summaries = []

            for issued_cert in issued_certs:
                cert, fingerprint = cryptofunctions.bytes_2_cert(issued_cert)
                cert_summaries.append(certSummary.CertSummary(str(cert.name), str(cert.issuer), fingerprint))

            trustlists = []
            certificate_groups = await gds_interface.getCertificateGroupsForApplication(id)

            for certificate_group in certificate_groups:
                trustlist = await gds_interface.getTrustList(id, structures.uaNodeId_2_nodeid(certificate_group))
                trustlist_bytes = await gds_interface.readTrustList(structures.uaNodeId_2_nodeid(trustlist))
                test = cryptofunctions.bytes_2_trustlist(trustlist_bytes)
                trustlists.append(cryptofunctions.bytes_2_trustlist(trustlist_bytes))
            
            applications_list.append(application.Application(id, appuri, appname, discoveryurl, issued_certs, cert_summaries, trustlists))

        global application_store
        application_store = {
            app.node_id.id: app
            for app in applications_list
        }
        applications_dict = {}
        domains = []
        
        for app in applications_list:
            applications_dict[app.node_id] = {}
        
        for i, first_app in enumerate(applications_list):
            for j in range(i, len(applications_list)):
                if (i == j):
                    applications_dict[first_app.node_id][first_app.node_id] = True
                    continue

                second_app = applications_list[j]

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
        if result_domains is None:
            return {"domains": []}
        
        domains = domains_to_json(result_domains)

        names = {}
        for app in application_store:
            name = application_store[app].names.Text
            names[str(app)] = name

        print(names)        
        return {"domains": domains, "names": names}
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"domains": None, "error": str(e)}


@app.get("/getCertificateGroups")
async def getcertificategroups():
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

    try:
        await gds_interface.connect()
        cert_groups: list[ua.NodeId] = await gds_interface.getCertificateGroups()
        cert_group_details = await gds_interface.getCertificateGroupAssignments(cert_groups)

        groups = []

        for cert_group_detail in cert_group_details:
            group_name = str(cert_group_detail.Name)
            cert_group_node = cert_group_detail.CertificateGroupId
            trustlist_node = cert_group_detail.TrustList
            trustlist_bytes = await gds_interface.readTrustList(structures.uaNodeId_2_nodeid(trustlist_node))
            result_trustlist = cryptofunctions.bytes_2_trustlist(trustlist_bytes)

            trusted_cert_bytes = result_trustlist['trusted_certificates']
            trusted_cert_summaries = []
            for trusted_cert in trusted_cert_bytes:
                certificate = cryptofunctions.bytes_2_cert(trusted_cert)
                certificate_summary = cryptofunctions.cert_bytes_2_certSummary(trusted_cert)
                certificates_store[certificate_summary.fingerprint] = certificate[0]
                trusted_cert_summaries.append(certificate_summary)

            trusted_crl_bytes = result_trustlist['trusted_crls']
            trusted_crls = []
            for trusted_crl in trusted_crl_bytes:
                crl = cryptofunctions.crl_2_crlSummary(trusted_crl)
                trusted_crls.append(crl)
            
            issuer_cert_bytes = result_trustlist['issuers']
            issuer_cert_summaries = []
            for issuer_cert in issuer_cert_bytes:
                certificate = cryptofunctions.bytes_2_cert(issuer_cert)
                certificate_summary = cryptofunctions.cert_bytes_2_certSummary(issuer_cert)
                certificates_store[certificate_summary.fingerprint] = certificate[0]
                issuer_cert_summaries.append(certificate_summary)

            issuer_crl_bytes = result_trustlist['issuer_crls']
            issuer_crls = []
            for issuer_crl in issuer_crl_bytes:
                crl = cryptofunctions.crl_2_crlSummary(issuer_crl)
                issuer_crls.append(crl)

            
            trustlists_store[structures.uaNodeId_2_nodeid(cert_group_node).id] = trustlist.TrustList(
                    group_name,
                    trusted_cert_summaries,
                    trusted_crls,
                    issuer_cert_summaries,
                    issuer_crls
                )

            '''
            group_store[structures.uaNodeId_2_nodeid(cert_group_node).id] = certificateGroup.CertificateGroup(
                
            )
            '''
            
            apps = cert_group_detail.Applications
            group_apps = []

            for a in apps:
                group_apps.append(structures.uaNodeId_2_nodeid(a))

            group = {"nodeId": structures.uaNodeId_2_nodeid(cert_group_node),
                     "group_name": group_name,
                      "applications": group_apps
                     }
            groups.append(group)
            print(group["group_name"])
        
        return {
            "groups": groups
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"groups": None, "error": str(e)}


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
