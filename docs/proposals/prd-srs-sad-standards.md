# Usulan standar dokumen PRD, SRS, dan SAD

Status: **Usulan — belum disetujui**. Dokumen ini mengusulkan kerangka untuk ditinjau; bukan standar aktif dan tidak mengubah scaffold atau validator. Struktur dan aturan setiap jenis dokumen memerlukan persetujuan tersendiri. Konten proyek, target, dan bukti yang belum diketahui harus ditulis `TBD`, bukan direka.

## Cakupan dan urutan implementasi

1. **PRD** (`docs/01-requirements/product-requirements.md`): kebutuhan produk, pengguna, dan hasil yang diharapkan.
2. **SRS** (`docs/01-requirements/system-requirements.md`): perilaku sistem dan persyaratan yang dapat diverifikasi. Repo menggunakan nama file system requirements; penyamaan istilah SRS dan SRD belum diputuskan.
3. **SAD** (`docs/02-architecture/architecture.md`): rancangan dan keputusan arsitektur untuk memenuhi kebutuhan yang berlaku.

Dokumen lain seperti rencana, verifikasi, runbook dan threat model tidak termasuk usulan awal ini; cakupannya dapat diputuskan kemudian. Profil Lean saat ini menggunakan dokumen requirements gabungan, sementara Standard dan Business Critical juga menghasilkan PRD dan SRS terpisah; struktur profil tidak diubah oleh usulan ini.

## PRD — usulan bagian berurutan

1. Document Information — pemilik, versi, status dan tanggal.
2. Executive Summary — kebutuhan dan arah produk secara ringkas.
3. Product Context — konteks, sumber informasi dan hubungan dengan kebutuhan bisnis.
4. Problem and Opportunity — masalah pengguna dan peluang yang didukung bukti.
5. Product Goals and Success Metrics — sasaran produk, pengukuran, baseline dan sumber; gunakan TBD jika belum diketahui.
6. Users and Stakeholders — kelompok pengguna, stakeholder dan kebutuhan yang diketahui.
7. Scope — cakupan dan pengecualian.
8. User Journeys and Use Cases — alur dan kasus penggunaan yang relevan.
9. Product Requirements — kebutuhan produk ber-ID, prioritas, alasan dan hubungan ke BR yang berlaku.
10. Nonfunctional Expectations — ekspektasi kualitas produk yang diketahui, tanpa mengarang target.
11. Dependencies and Constraints — ketergantungan dan batasan yang diketahui.
12. Assumptions — asumsi dan cara memverifikasinya.
13. Risks and Open Questions — risiko dan pertanyaan yang memerlukan tindak lanjut.
14. Priorities and Phasing — prioritas dan tahapan yang diusulkan.
15. Acceptance and Release Readiness — kriteria penerimaan produk dan bukti yang diperlukan.
16. Decisions and Approvals — keputusan, pemilik, sumber dan status persetujuan.
17. Traceability — hubungan kebutuhan bisnis, kebutuhan produk, pengukuran dan verifikasi yang berlaku.

## SRS — usulan bagian berurutan

1. Document Information.
2. Purpose and Scope — tujuan, batas sistem dan sumber.
3. System Context — pengguna, sistem eksternal dan batas sistem.
4. Definitions and References.
5. Functional Requirements — perilaku sistem dengan ID stabil dan kriteria verifikasi.
6. Interfaces — antarmuka pengguna, sistem dan data yang berlaku.
7. Data Requirements — data dan aturan penanganan yang diketahui.
8. Nonfunctional Requirements — kebutuhan kualitas terukur atau TBD.
9. Security and Privacy Requirements — kebutuhan yang relevan dengan risiko.
10. Constraints and Dependencies.
11. Assumptions and Open Questions.
12. Verification and Acceptance — metode pengujian dan evidence yang diperlukan.
13. Decisions and Approvals.
14. Traceability — hubungan ke PRD, rancangan dan pengujian.

## SAD — usulan bagian berurutan

1. Document Information.
2. Purpose, Scope and References.
3. Architectural Drivers — kebutuhan dan batasan yang memengaruhi rancangan.
4. System Context and Trust Boundaries.
5. Architecture Overview — komponen dan tanggung jawab.
6. Component and Interface Design.
7. Data Flows and Storage.
8. Security and Privacy Architecture — kontrol yang relevan dan hubungan ke threat model.
9. Quality Attributes — kinerja, keandalan, aksesibilitas dan lainnya bila berlaku.
10. Deployment and Operations — topologi, monitoring, pemulihan dan batasan yang diketahui.
11. Dependencies and Constraints.
12. Architecture Decisions and Alternatives — tautan ke ADR, tidak menduplikasi keputusan.
13. Risks, Assumptions and Open Questions.
14. Verification and Evidence.
15. Traceability — hubungan kebutuhan, keputusan, kontrol dan pengujian.
16. Review and Approvals.

## Kontrak yang diusulkan untuk setiap jenis

Setelah kerangka jenis dokumen disetujui, buat standar bersama dan template Markdown, kontrak machine-readable berversi, contoh sintetis, validator deterministik, serta tes positif dan negatif. Pertahankan file existing saat scaffold berjalan dan gunakan `TBD` untuk informasi yang belum diketahui. Bedakan validasi otomatis, tinjauan semantik, dan persetujuan manusia. Aturan ID, format tabel, lintas-referensi dan tingkat kewajiban tiap bagian perlu ditetapkan secara eksplisit pada saat persetujuan masing-masing dokumen; jangan menganggap contoh ini sebagai aturan final.

Gunakan ulang mekanisme BRD dan arsitektur skill modular sejauh sesuai, dengan menghindari duplikasi logika; pastikan perubahan kompatibel dengan profil dan tidak memodifikasi standar dokumen lain. Ketersediaan adapter tidak dengan sendirinya membuktikan eksekusi end-to-end di kedua host.
