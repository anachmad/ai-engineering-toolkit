# SAD standard v1

Apply the approved headings and table contracts in `standards/sad-v1.json` when a full SAD is applicable. Profile-specific enforcement has not been decided. Preserve existing project artifacts and IDs; do not invent requirements, technical decisions, controls, evidence or approval.

## Document Information

Judul, versi dokumen, status, pemilik dan tanggal.

## Architecture Executive Summary

Ikhtisar sistem dan keputusan arsitektur utama.

## Architecture Goals & Drivers

Kebutuhan, atribut kualitas dan batasan yang mendorong rancangan; rujuk requirement sumber.

## System Context

Batas sistem, aktor, sistem eksternal dan hubungan utama.

## Architecture Principles

Prinsip yang dipakai dan alasan atau sumbernya.

## Technology Stack

Teknologi yang diketahui atau diusulkan, status keputusan dan batas penerapannya.

## High-Level Architecture

Gambaran komponen dan aliran utama; sertakan diagram bila membantu.

## Application & Component Design

Tanggung jawab komponen dan hubungan antarkomponen.

## Data Architecture

Aliran, penyimpanan, kepemilikan, sensitivitas dan retensi data yang relevan.

## Integration Architecture

Integrasi, antarmuka, batas kepercayaan dan kegagalan yang relevan.

## Security Architecture

Kontrol dan trust boundary sesuai risiko; tautkan threat model dan security review jika ada.

## Infrastructure & Deployment

Lingkungan, dependensi dan rancangan deployment yang diketahui.

## Reliability & Availability

Kebutuhan keandalan, pemulihan, backup dan asumsi kegagalan yang berlaku.

## Performance & Scalability

Driver kinerja, kapasitas dan strategi skala; target yang belum diketahui ditulis TBD.

## Observability & Operations

Monitoring, logging, alert dan kepemilikan operasional; tautkan runbook yang relevan.

## Architecture Decisions & Trade-offs

Keputusan, alternatif, alasan dan konsekuensi; tautkan ADR untuk keputusan signifikan.

## Risks & Technical Debt

Risiko, dampak, pemilik dan utang teknis yang diketahui; tandai hal yang belum diputuskan.

## Architecture Validation & Traceability

Hubungan requirement → keputusan/kontrol → metode verifikasi dan bukti yang tersedia.

## Review and evidence

Decision statuses are Proposed, Accepted, Superseded and TBD. Accepted is a self-reported claim, not proof of human authorization. Use TBD when unknown. A section that is not applicable must state `Not applicable — reason`; its relevance is subject to human review. Link existing requirements, ADRs, security reviews and runbooks without duplicating them. Sources and meaning, diagram consistency, security adequacy, test execution and approval require human review. SAD v2 selects the approved profile mode and checks supported local references when explicitly configured; it does not verify all references or authorize releases.
