# Usulan standar Data Model Specification untuk review

Status: **Sembilan heading dan lokasi yang direkomendasikan disetujui pengguna.** Field dan aturan validasi disetujui; template dan validator v1 tersedia untuk penggunaan opsional.

## Tujuan dan posisi

Data Model Specification menjelaskan struktur data yang digunakan sistem: domain dan pemiliknya, entitas, hubungan, atribut, aturan integritas serta kebutuhan migrasi dan retensi yang diketahui. Dokumen ini membantu tim menilai konsistensi rancangan dan dampak perubahan data.

SRS mencatat kebutuhan data; bagian Data Architecture pada SAD memberi gambaran arsitektur; Data Model Specification memberikan detail model yang relevan. Rujuk sumber yang ada seperti skema database, migrasi atau kontrak data tanpa membuat salinan yang dapat bertentangan. Jika model menjelaskan rancangan usulan, beri status usulan; jangan menyatakannya sebagai kondisi sistem yang sudah berjalan tanpa bukti.

## Sembilan bagian yang disetujui — nama dan urutan

| No. | Heading | Isi yang diharapkan |
| --- | --- | --- |
| 1 | Metadata | Judul, versi, status, pemilik dan tanggal. |
| 2 | Scope | Batas model, sistem atau domain yang dicakup dan pengecualian yang diketahui. |
| 3 | Data Domain & Ownership | Domain data, pemilik atau penanggung jawab dan sumber yang berwenang. |
| 4 | Entity Catalog | Entitas atau objek data yang relevan, tujuan dan identitasnya. |
| 5 | Relationships & Cardinality | Hubungan antarentitas, kardinalitas dan batasan yang diketahui. |
| 6 | Field Dictionary | Atribut yang relevan, definisi, tipe atau format, kewajiban dan sumbernya. |
| 7 | Constraints & Integrity | Aturan integritas, validasi, keunikan dan konsistensi yang relevan. |
| 8 | Migration & Retention | Kebutuhan perubahan skema, migrasi, retensi dan penghapusan yang diketahui. |
| 9 | Validation & References | Cara memeriksa model, hubungan ke requirement dan referensi sumber atau evidence. |

Usulan format: gunakan sembilan heading tingkat dua (`##`) dengan nama dan urutan di atas ketika dokumen lengkap diperlukan. Gunakan `TBD` untuk informasi yang belum diketahui. Jika suatu bagian tidak berlaku, catat `Not applicable` beserta alasan; relevansinya tetap memerlukan review manusia.

## Usulan prinsip penerapan

- **Ketersediaan artefak:** struktur dan kewajiban membuat dokumen adalah dua keputusan berbeda. Dokumen terpisah tidak otomatis diwajibkan untuk semua proyek atau profil; model sederhana dapat dirujuk dari dokumen yang sudah ada jika sesuai governance proyek.
- **Lokasi:** bila dibutuhkan sebagai file terpisah, usulan lokasi `docs/02-architecture/data-model.md`. File existing dipertahankan; perubahan ini tidak otomatis mengubah profil, scaffold atau dokumen project.
- **Keamanan dan privasi:** identifikasi sensitivitas dan kepemilikan data bila diketahui; minimisasi contoh data dan jangan mencantumkan data pribadi nyata, secret, atau nilai produksi. Retensi dan kontrol tidak boleh dinyatakan sudah diterapkan tanpa evidence.
- **Sumber kebenaran:** rujuk model atau skema yang otoritatif beserta versi/statusnya. Jika dokumen dan skema bertentangan, laporkan perbedaan untuk review; jangan memilih salah satu sebagai benar tanpa dasar.
- **ID dan traceability:** pertahankan konvensi ID yang sudah ada. Kebutuhan ID entitas, format tabel, dan hubungan ke requirement memerlukan review rinci sebelum validator diterapkan.
- **Bukti:** keputusan retensi, tipe field, cardinality, aturan integrity dan hasil migrasi yang belum dipastikan tetap `TBD` atau ditandai usulan. Jangan mengarang data, aturan bisnis, target, approval atau hasil tes.

## Batas validasi yang diusulkan

Validator dapat memeriksa heading, metadata, tabel dan referensi yang sudah didefinisikan; pemeriksaan terhadap database atau skema aktual membutuhkan sumber serta metode yang dipilih dan diuji secara terpisah. Hasil pemeriksaan struktur tidak membuktikan model cocok dengan database, aman, disetujui atau siap digunakan. Semantic review dan approval manusia tetap terpisah.

## Keputusan untuk owner

1. Struktur dan lokasi yang direkomendasikan telah disetujui pengguna; dokumen terpisah tidak otomatis diwajibkan.
2. [Aturan rinci](data-model-detail-rules.md) telah disetujui; penerapan berdasarkan profil tetap diputuskan proyek.
