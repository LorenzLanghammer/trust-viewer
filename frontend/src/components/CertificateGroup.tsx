import { useState } from "react";
import { CertificateList } from "./CertificateList";
import { CrlList } from "./CrlList";
import axios from "axios";

export function CertificateGroup({
  selectedGroup,
  setSelectedGroup,
  setSelectedCert,
  setSelectedCrl
}: {
  selectedGroup: any;
  setSelectedGroup: (cert: any | null) => void;
  setSelectedCert: (cert: any | null) => void;
  setSelectedCrl: (crl: any | null) => void;
}) {
  if (!selectedGroup) return null;
  return (
    <>
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
                {selectedGroup.groupName}
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
    </>
  )
}