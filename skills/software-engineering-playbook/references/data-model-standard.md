# Data Model Specification standard v1

Use the nine approved headings and table contracts in `standards/data-model-v1.json` when this optional artifact is applicable. Preserve existing names and IDs. Do not invent data, targets, controls, evidence or approval.

## Metadata

Judul, versi, status, pemilik dan tanggal.

## Scope

Batas model, sistem atau domain yang dicakup dan pengecualian yang diketahui.

## Data Domain & Ownership

Domain data, pemilik atau penanggung jawab dan sumber yang berwenang.

## Entity Catalog

Entitas atau objek data yang relevan, tujuan dan identitasnya.

## Relationships & Cardinality

Hubungan antarentitas, kardinalitas dan batasan yang diketahui.

## Field Dictionary

Atribut yang relevan, definisi, tipe atau format, kewajiban dan sumbernya.

## Constraints & Integrity

Aturan integritas, validasi, keunikan dan konsistensi yang relevan.

## Migration & Retention

Kebutuhan perubahan skema, migrasi, retensi dan penghapusan yang diketahui.

## Validation & References

Cara memeriksa model, hubungan ke requirement dan referensi sumber atau evidence.

## Validation limits

Field names and entity names are matched exactly, including case, within this document; case-only collisions are warnings for owner review. A missing local entity is an error only when the entity catalog has no TBD placeholder; otherwise it is unverified. Prefix an intentionally external entity reference with `external:` and a source identifier; external entities remain unverified. Required accepts Yes, No or TBD. Sensitivity must follow the project policy; the validator does not assess or infer it. Source authority, database/schema reality, semantic quality, security, migrations, evidence and human approval are not independently verified.
