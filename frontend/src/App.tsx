import axios from "axios";
import { useEffect, useState } from "react";

interface Application {
  ApplicationUri: string,
  ApplicationName: string;
}

function App() {
  const [applications, setApplications] = useState<Application[]>([]);

  useEffect(() => {
    axios.get("http://localhost:8000/opcuaconnect")
      .then(res => {

        console.log(res.data);

        const apps: Application[] = res.data.map((item: any) => ({
          ApplicationUri: item[0],
          ApplicationName: item[1]
        }));

        setApplications(apps);
      })
      .catch(err => {
        console.error("Error fetching applications:", err);
      });
  }, []);

  return (
    <div style={{padding:"20px"}}>
    <h1 style={{
      position: "fixed",
      top: 0,
      left: 0,
      width: "100%",
      backgroundColor: "#fff",
      padding: "20px",
      zIndex: 1000,
      boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
    }}>
    Trustviewer
    </h1>
      <ul>
        {applications.map((app, index) => (
          <li key={index}>
            <strong>{app.ApplicationName}</strong> — {app.ApplicationUri}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
