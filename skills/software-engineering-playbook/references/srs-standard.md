# SRS standard v1

The approved 16 headings, requirement fields, and quality rules are defined by `standards/srs-v1.json` and described below. Apply the template without fabricating requirements, sources, targets, evidence, or approval. Existing requirement IDs retain their project format.

## Document Information

Judul, versi dokumen, status, pemilik dan tanggal.

## Introduction

Tujuan, ruang lingkup, definisi dan referensi sumber.

## System Overview

Ringkasan sistem dan layanan yang disediakan.

## System Context & Boundaries

Batas sistem, pihak dan sistem eksternal yang berinteraksi.

## Actors & Roles

Aktor, peran dan tanggung jawab yang relevan.

## Functional Requirements

Perilaku sistem, kondisi dan kriteria verifikasi per requirement.

## Non-Functional Requirements

Kualitas sistem dengan ukuran dan kondisi uji jika dapat ditetapkan.

## Business Rules & Constraints

Aturan bisnis dan batasan yang berlaku beserta sumber; tautkan ke dokumen sumber untuk menghindari duplikasi.

## Data Requirements

Data yang diperlukan, aturan dan kebutuhan perlindungan yang berlaku.

## External Interface Requirements

Kebutuhan antarmuka dengan pengguna, sistem atau layanan eksternal.

## State & Workflow Specifications

Keadaan dan transisi atau alur yang relevan.

## Error & Exception Handling

Respons yang diharapkan ketika terjadi kegagalan atau pengecualian.

## Security & Access Requirements

Kebutuhan keamanan, akses dan privasi yang relevan dengan risiko.

## Assumptions & Dependencies

Asumsi dan ketergantungan, dipisahkan dari fakta terverifikasi.

## Verification & Acceptance Criteria

Metode verifikasi dan kriteria penerimaan yang berlaku.

## Traceability Matrix

Hubungan sumber, requirement sistem, rancangan dan verifikasi yang diketahui.

## Requirement rules

The Functional Requirements and Non-Functional Requirements sections each contain the nine-column table in the template. IDs are stable and unique; FR-001 and NFR-001 are defaults when no project format exists. Source identifies product requirements or other owner-authorized sources. Priority defaults to Must, Should, Could or TBD; select an explicit project list when existing conventions differ. Preconditions and failure conditions may contain `N/A — reason`; other fields require content or TBD. Verification method is Test, Inspection, Analysis, Demonstration or TBD. Status is Draft, In review, Approved, Deferred or TBD.

TBD is incomplete, not evidence. NFR thresholds, units and test conditions need human review. The validator checks structure, fields and IDs but does not assess meaning, authenticate approval, or prove a test was run. Refer to the documentation validation guide for current support and limitations.
