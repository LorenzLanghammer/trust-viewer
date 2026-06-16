import axios from "axios"

interface CrlSummary {
    issuer: string,
    revoked: number[]
}

export function CrlList({
  crls,
  title = "CRLs",
  onCrlClick
}: {
  crls: CrlSummary[]
  title?: string
  onCrlClick?: (crl: any) => void
}) {
  return (
    <div style={{ marginTop: "20px" }}>
      <details>
        <summary
          style={{
            fontWeight: 700,
            color: "#666",
            cursor: "pointer",
            padding: "8px 0"
          }}
        >
          {title}
        </summary>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "10px",
            marginTop: "12px"
          }}
        >
          {crls.map((crl, index) => (
            <div
              style={{
                width: "80px",
                padding: "10px",
                background: "#f8f8f8",
                borderRadius: "10px",
                border: "1px solid #ddd",
                cursor: "pointer",
                transition: "0.2s",
                overflow: "hidden"
              }}
              onClick={() => {
                if (onCrlClick) {
                  onCrlClick(crl)
                } else {
                  console.log("could not get certificate")
                }
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform =
                  "translateY(-2px)"
                e.currentTarget.style.boxShadow =
                  "0 4px 12px rgba(0,0,0,0.15)"
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = ""
                e.currentTarget.style.boxShadow = ""
              }}
            >
              <div
                style={{
                  fontWeight: 600,
                  marginBottom: "6px",
                  fontSize: "14px"
                }}
              >
                CRL
              </div>

              <div
                style={{
                  fontSize: "12px",
                  marginBottom: "4px",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis"
                }}
              >
                <strong>issuer:</strong>{" "}
                {crl.issuer}
              </div>
            </div>
          ))}
        </div>
      </details>
    </div>
  )
}