import axios from "axios";
import { useEffect, useState } from "react";

interface Application {
  ApplicationUri: string,
  ApplicationName: string;
}

function App() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    axios.get("http://localhost:8000/opcuaconnect")
      .then(res => {
        console.log(res.data);
        setData(res.data);
      })
      .catch(err => {
        console.error(err);
      });
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>Trustviewer</h1>

      <pre>
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}

export default App;
