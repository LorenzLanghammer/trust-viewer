import axios from "axios";
import { useEffect, useState } from "react";
import { Graph } from "./components/Graph"


interface Application {
  ApplicationUri: string,
  ApplicationName: string;
}

const nodes = [
      { id: 1653845693},
      { id: 1348232402},
      { id: 771637625}
    ]

    const links = [
      { source: 1653845693, target: 1348232402},
      { source: 1348232402, target: 771637625}
    ]

function App() {

  let num:number = 0; 
  let i:number; 

  const [data, setData] = useState<any>(null);
  const [domainsState, setDomainsState] = useState<number[][]>([])
  const [groupsState, setGroupsState] = useState<Array<Array<{namespace: number | null, id: number | string}>>>([])

  useEffect(() => {
    axios.get("http://localhost:8000/opcuaconnect")
      .then(res => {
        setData(res.data);
        const computed: number[][] = []
        for (let domain = 0; domain < res.data['domains'].length; domain++) {
          const domainArray = res.data['domains'][domain]
          // ids aus domainArray entnehmen (falls backend {namespace,id}) — keine Deduplication hier
          const ids = domainArray.map((n: any) => Number(n.id)) as number[]
          computed.push(ids)
        }
        setDomainsState(computed)
      })
      .catch(err => {
        console.error(err);
      });
  }, []);

  useEffect(() => {
    axios.get("http://localhost:8000/getCertificateGroups")
      .then(res => {
        // expected shape: { status: 'ok', groups: Array<Array<{namespace,id}>> }
        if (res.data && res.data.groups) {
          setGroupsState(res.data.groups)
        }
        console.log(res.data)
      })
      .catch(err => {
        console.error(err);
      });
  }, []);

  return (
    
    <div style={{ paddingTop: "10px" }}>
        <h1 style={{
          position: "fixed",
          top: 0,
          left: 0,
          padding: "10px 20px",
          backgroundColor: "white",
          zIndex: 1000
        }}>
          Trustviewer
        </h1>
          {domainsState.length > 0 ? (
            <Graph domains={domainsState} groups={groupsState} />
          ) : (
            <div style={{ paddingTop: 120 }}>Lade Graph…</div>
          )}
    </div>
  );
}

export default App;