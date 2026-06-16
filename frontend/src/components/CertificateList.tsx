import axios from "axios"

interface CertificateSummary {
  subject: string
  issuer: string
  fingerprint: string
}

export function CertificateList({
  certificates,
  title = "Certificates",
  onCertificateClick
}: {
  certificates: CertificateSummary[]
  title?: string
  onCertificateClick?: (certificate: any) => void
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
          {certificates.map((cert, index) => (
            <div
              key={cert.fingerprint}
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
                if (onCertificateClick) {
                  onCertificateClick(cert)
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
                Certificate
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
                <strong>Subject:</strong>{" "}
                {cert.subject}
              </div>

              <div
                style={{
                  fontSize: "12px",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis"
                }}
              >
                <strong>Issuer:</strong>{" "}
                {cert.issuer}
              </div>
            </div>
          ))}
        </div>
      </details>
    </div>
  )
}