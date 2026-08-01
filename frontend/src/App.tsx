import axios from "axios";
import { useEffect, useState } from "react";
import { Graph } from "./components/Graph"
import { Certificate } from "./components/Certificate";
import { ApplicationState, GroupState } from "./types/graph";
import { Crl } from "./components/Crl";
import { Application } from "./components/Application";
import { CertificateGroup } from "./components/CertificateGroup";

function App() {

  const [data, setData] = useState<any>(null);
  const [domainsState, setDomainsState] = useState<number[][]>([])
  const [groupsState, setGroupsState] = useState<GroupState[]>([])
  const [applicationState, setApplicationState] = useState<Record<number, string>>({})


  const [selectedApp, setSelectedApp] = useState<any>(null)
  const [selectedGroup, setSelectedGroup] = useState<any>(null)
  const [selectedCert, setSelectedCert] = useState<any>(null)
  const [selectedCrl, setSelectedCrl] = useState<any>(null)

  const [showDomainHulls, setShowDomainHulls] = useState(false)
  const [showGroupHulls, setShowGroupHulls] = useState(false)
  
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

      
      <Application 
        selectedApp={selectedApp}
        setSelectedApp={setSelectedApp}
        setSelectedCert={setSelectedCert}
      />
      
      <Certificate
        selectedCert={selectedCert}
        setSelectedCert={setSelectedCert}
      />

      <Crl
        selectedCrl={selectedCrl}
        setSelectedCrl={setSelectedCrl}
      />

      <CertificateGroup
        selectedGroup={selectedGroup}
        setSelectedGroup={setSelectedGroup}
        setSelectedCert={setSelectedCert}
        setSelectedCrl={setSelectedCrl}
      />
      
      
    </div>
  );
}

export default App;