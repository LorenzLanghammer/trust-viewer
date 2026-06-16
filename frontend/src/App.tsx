import axios from "axios";
import { useEffect, useState } from "react";
import { Graph } from "./components/Graph"
import { CertificateList } from "./components/CertificateList";
import { Certificate } from "./components/Certificate";
import { ApplicationState, GroupState } from "./types/graph";
import { CrlList } from "./components/CrlList";
import { Crl } from "./components/Crl";

function App() {

  const [data, setData] = useState<any>(null);
  const [domainsState, setDomainsState] = useState<number[][]>([])
  const [groupsState, setGroupsState] = useState<GroupState[]>([])
  const [applicationState, setApplicationState] = useState<Record<number, string>>({})


  const [selectedApp, setSelectedApp] = useState<any>(null)
  const [selectedGroup, setSelectedGroup] = useState<any>(null)
  const [selectedCert, setSelectedCert] = useState<any>(null)
  const [selectedCrl, setSelectedCrl] = useState<any>(null)

  const [showDomainHulls, setShowDomainHulls] = useState(true)
  const [showGroupHulls, setShowGroupHulls] = useState(true)
  
  useEffect(() => {
    axios.get("http://localhost:8000/opcuaconnect")
      .then(res => {
        setData(res.data);
        const computed: number[][] = []
        for (let domain = 0; domain < res.data['domains'].length; domain++) {
          const domainArray = res.data['domains'][domain]
          const ids = domainArray.map((n: any) => Number(n.id)) as number[]
          computed.push(ids)
        }
        setDomainsState(computed)
        setApplicationState(res.data['names'])
      })
      .catch(err => {
        console.error(err);
      });
  }, []);

  useEffect(() => {
    axios.get("http://localhost:8000/getCertificateGroups")
      .then(res => {
        const computed: GroupState[] = []
        for (let group = 0; group < res.data['groups'].length; group++) {
          const groupArray = res.data['groups'][group]['applications']
          const groupId = res.data['groups'][group]['nodeId'].id
          const group_name = res.data['groups'][group]['group_name']
          const ids = groupArray.map((n: any) => Number(n.id)) as number[]
          computed.push({"applicationIds": ids, "groupId": groupId, "group_name": group_name})
        }
        console.log(computed)
        setGroupsState(computed)
      })
      .catch(err => {
        console.error(err);
      });
  }, []);

  return (

    <div style={{ paddingTop: "10px" }}>
      <div style={{ position: "absolute", top: 20, left: 20 }}>
        <label>
          <input
            type="checkbox"
            checked={showDomainHulls}
            onChange={(e) => setShowDomainHulls(e.target.checked)}
          />
          Domain View
        </label>

        <label style={{ marginLeft: "15px" }}>
          <input
            type="checkbox"
            checked={showGroupHulls}
            onChange={(e) => setShowGroupHulls(e.target.checked)}
          />
          Certificate Group View
        </label>
      </div>
      {domainsState.length > 0 ? (
        <Graph
          domains={domainsState}
          groups={groupsState}
          applications={applicationState}
          onNodeClick={(id) => {
            axios.get(`http://localhost:8000/getapplication/${id}`)
              .then(res => {
                setSelectedApp(res.data)
              }
              )
          }}
          onGroupClick={(groupId) => {
            axios.get(`http://localhost:8000/trustlist/${groupId}`)
              .then(res => {
                setSelectedGroup(res.data)
                console.log("lists")
                console.log(res.data)
              })
          }}
          showDomainHulls={showDomainHulls}
          showGroupHulls={showGroupHulls}
        />
      ) : (
        <div style={{ paddingTop: 120 }}>Lade Graph…</div>
      )}

      {selectedApp && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.35)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 2000
          }}
          onClick={() => setSelectedApp(null)}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              width: "500px",
              background: "white",
              borderRadius: "16px",
              padding: "28px",
              boxShadow: "0 20px 60px rgba(0,0,0,0.25)",
              fontFamily: "Arial, sans-serif"
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "24px"
              }}
            >
              <h2
                style={{
                  margin: 0,
                  fontSize: "28px"
                }}
              >
                {selectedApp.name || "Unnamed Application"}
              </h2>

              <button
                onClick={() => setSelectedApp(null)}
                style={{
                  border: "none",
                  color: "#ea1313",
                  borderRadius: "8px",
                  padding: "8px 12px",
                  cursor: "pointer",
                  background: "rgba(224, 221, 221, 0.08)",

                }}
              >
                ✕
              </button>
            </div>

            <div style={{ display: "grid", gap: "18px" }}>

              <div>
                <div
                  style={{
                    fontWeight: 700,
                    marginBottom: "6px",
                    color: "#666"
                  }}
                >
                  NodeId
                </div>

                <div
                  style={{
                    background: "#f5f5f5",
                    borderRadius: "10px",
                    padding: "12px",
                    fontFamily: "monospace"
                  }}
                >
                  <div>
                    Namespace: {selectedApp.node_id.namespace}
                  </div>

                  <div>
                    Id: {selectedApp.node_id.id}
                  </div>
                </div>
              </div>

              <div>
                <div
                  style={{
                    fontWeight: 700,
                    marginBottom: "6px",
                    color: "#666"
                  }}
                >
                  Application URI
                </div>

                <div
                  style={{
                    background: "#f5f5f5",
                    borderRadius: "10px",
                    padding: "12px",
                    fontFamily: "monospace",
                    overflowWrap: "break-word"
                  }}
                >
                  {selectedApp.applicationuri}
                </div>
              </div>


              <div>
                <div
                  style={{
                    fontWeight: 700,
                    marginBottom: "6px",
                    color: "#666"
                  }}
                >
                  Discovery URL
                </div>

                <div
                  style={{
                    background: "#f5f5f5",
                    borderRadius: "10px",
                    padding: "12px",
                    fontFamily: "monospace",
                    overflowWrap: "break-word"
                  }}
                >
                  {selectedApp.discoveryurls}
                </div>
              </div>

              <div style={{ marginTop: "5px" }}>
                <CertificateList
                  title="Issued Certificates"
                  certificates={
                    selectedApp?.issued_certs_summaries || []
                  }
                  onCertificateClick={(cert) => {
                    axios
                      .get(
                        `http://localhost:8000/getcertificate/${cert.fingerprint}`
                      )
                      .then(res => {
                        console.log(res.data)
                        setSelectedCert(res.data)
                      })
                  }}
                />
              </div>

            </div>
          </div>

          <div style={{ marginTop: "20px" }}>

          </div>
        </div>
      )}

      <Certificate
        selectedCert={selectedCert}
        setSelectedCert={setSelectedCert}
      />

      <Crl
        selectedCrl={selectedCrl}
        setSelectedCrl={setSelectedCrl}
      />

      {selectedGroup && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100vw",
            height: "100vh",
            backgroundColor: "rgba(0,0,0,0.35)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 2000
          }}
          onClick={() => setSelectedGroup(null)} // click outside closes
        >

          <div
            style={{
              background: "white",
              borderRadius: "8px",
              padding: "20px",
              minWidth: "300px",
              boxShadow: "0 10px 30px rgba(223, 209, 209, 0.3)"
            }}
            onClick={(e) => e.stopPropagation()} // prevent closing when clicking inside
          >

            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "24px"
              }}
            >
              <h2
                style={{
                  margin: 0,
                  fontSize: "28px"
                }}
              >
                {selectedGroup.name || "Certificate Group"}
              </h2>

              <button
                onClick={() => setSelectedGroup(null)}
                style={{
                  border: "none",
                  color: "#ea1313",
                  borderRadius: "8px",
                  padding: "8px 12px",
                  cursor: "pointer",
                  background: "rgba(224,221,221,0.08)"
                }}
              >
                ✕
              </button>
            </div>
                        
            <div style={{ marginTop: "5px" }}>
              <CertificateList
                title="Trusted Certificates"
                certificates={
                  selectedGroup?.trustedCertificates || []
                }
                onCertificateClick={(cert) => {
                  axios
                    .get(
                      `http://localhost:8000/getcertificate/${cert.fingerprint}`
                    )
                    .then(res => {
                      setSelectedCert(res.data)
                    })
                }}
              />
            </div>

            <div style={{ marginTop: "5px" }}>
              <CertificateList
                title="Issuer Certificates"
                certificates={
                  selectedGroup?.issuerCertificates || []
                }
                onCertificateClick={(cert) => {
                  axios
                    .get(
                      `http://localhost:8000/getcertificate/${cert.fingerprint}`
                    )
                    .then(res => {
                      setSelectedCert(res.data)
                    })
                }}
              />
            </div>

            <div style={{ marginTop: "5px" }}>
              <CrlList
                title="Trusted CRLs"
                crls={
                  selectedGroup?.trustedCrls || []
                }
                onCrlClick={(crl) => {
                  setSelectedCrl(crl)
                }}
              />
            </div>

            <div style={{ marginTop: "5px" }}>
              <CrlList
                title="Issuer CRLs"
                crls={
                  selectedGroup?.issuerCrls || []
                }
                onCrlClick={(crl) => {
                  setSelectedCrl(crl)
                }}
              />
            </div>
            
          </div>
        </div>
      )}
    </div>
  );
}

export default App;