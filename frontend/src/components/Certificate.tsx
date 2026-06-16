import { useState } from "react";

export function Certificate({
  selectedCert,
  setSelectedCert
}: {
  selectedCert: any;
  setSelectedCert: (cert: any | null) => void;
}) {
  const [showFullKey, setShowFullKey] = useState(false);
  if (!selectedCert) return null;
  return (
    <>
        <div
        onClick={() => setSelectedCert(null)}
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
        <button
            onClick={() => setSelectedCert(null)}
            style={{
                position: "absolute",
                top: "12px",
                right: "12px",
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

        <div style={{marginBottom:"16px"}}>
            <strong>Serial Number</strong>
        <div>{selectedCert.serial}</div>
        </div>

        <div style={{marginBottom:"16px"}}>
            <strong>Name</strong>
        <div>{selectedCert.name}</div>
        </div>

        <div style={{marginBottom:"16px"}}>
            <strong>Issuer</strong>
        <div>{selectedCert.issuer}</div>
        </div>

        <div style={{marginBottom:"16px"}}>
            <strong>Not Before</strong>
        <div>{selectedCert.notbefore}</div>
        </div>

        <div style={{marginBottom:"16px"}}>
            <strong>Not After</strong>
        <div>{selectedCert.notafter}</div>
        </div>


        <div style={{ marginBottom: "16px" }}>
            <strong>Public Key</strong>
        <div
        onDoubleClick={() =>
            setShowFullKey(prev => !prev)
        }
        style={{
            fontSize: "11px",
            background: "#f5f5f5",
            padding: "10px",
            borderRadius: "8px",
            marginTop: "6px",
            cursor: "pointer",
            overflow: "hidden",
            border: "1px solid #ddd",

            ...(showFullKey
            ? {
                wordBreak: "break-all",
                maxHeight: "200px",
                overflowY: "auto"
                }
            : {
                whiteSpace: "nowrap",
                textOverflow: "ellipsis"
                })
        }}
        >
        {showFullKey
            ? selectedCert.key
            : selectedCert.key.slice(0, 50) + "..."}
        </div>

        <div
        style={{
            fontSize: "11px",
            color: "#888",
            marginTop: "4px"
        }}
        >
        </div>
    </div>

    <div>

    <details
        style={{
            marginTop: "20px"
        }}
        >
        <summary
            style={{
            fontWeight: 700,
            color: "#666",
            cursor: "pointer",
            padding: "8px 0"
            }}
        >
            Extensions ({selectedCert.extensions?.length || 0})
        </summary>

        <div
            style={{
            marginTop: "12px",
            display: "flex",
            flexDirection: "column",
            gap: "10px"
            }}
        >
            {selectedCert.extensions?.map((ext: any, index: number) => (
            <div
                key={index}
                style={{
                padding: "10px",
                background: "#f8f8f8",
                borderRadius: "10px",
                border: "1px solid #ddd"
                }}
            >
                <div
                style={{
                    fontWeight: 600,
                    marginBottom: "4px"
                }}
                >
                {ext.name}
                </div>

                <div
                style={{
                    fontSize: "13px",
                    color: "#555",
                    wordBreak: "break-word"
                }}
                >
                {ext.value}
                </div>
            </div>
            ))}
        </div>
        </details>
    </div>
    </div>
    </>
  )
}