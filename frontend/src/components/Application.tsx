import { useState } from "react";
import { CertificateList } from "./CertificateList";
import { Certificate } from "./Certificate";
import axios from "axios";


export function Application({
  selectedApp,
  setSelectedApp,
  setSelectedCert
}: {
  selectedApp: any;
  setSelectedApp: (cert: any | null) => void;
  setSelectedCert: (cert: any | null) => void;
}) {
  if (!selectedApp) return null;
  return (
    <>
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
    </>
  )
}