import { useState } from "react";

export function Crl({
  selectedCrl,
  setSelectedCrl
}: {
  selectedCrl: any;
  setSelectedCrl: (cert: any | null) => void;
}) {

  if (!selectedCrl) return null;
  return (
    <>
        <div
        onClick={() => setSelectedCrl(null)}
        style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100vw",
            height: "100vh",
            background: "rgba(0,0,0,0.45)",
            zIndex: 2500
        }}
        />

        <div
        style={{
            position: "fixed",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            background: "white",
            padding: "24px",
            borderRadius: "14px",
            boxShadow: "0 8px 30px rgba(0,0,0,0.25)",
            width: "300px",
            maxHeight: "80vh",
            overflowY: "auto",
            zIndex: 3000
        }}
        >


        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "20px"
          }}
        >
          <h2
            style={{
              margin: 0,
              fontSize: "24px"
            }}
          >
            CRL
          </h2>

          <button
            onClick={() => setSelectedCrl(null)}
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

       <div style={{ marginBottom: "16px" }}>
        <strong>Revoked Certificates</strong>

        {selectedCrl.revoked.map((item: any, index: number) => (
          <div
            key={index}
            style={{
              padding: "8px",
              marginTop: "4px",
              background: "#f5f5f5",
              borderRadius: "6px"
            }}
          >
            {item}
          </div>
        ))}
      </div>
    <div>

    
    </div>
    </div>
    </>
  )
}