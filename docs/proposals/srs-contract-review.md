# Usulan kontrak SRS untuk review

Status: **16 heading dan penggunaan nama SRS untuk file system requirements disetujui oleh pengguna pada 2026-11-23.** Aturan field dan format tabel disetujui pada 2026-11-24; template dan validator SRS v1 telah dibuat. Tidak ada perubahan pada dokumen proyek.

## Tujuan dan posisi dokumen

SRS (Software Requirements Specification) menjelaskan **apa yang harus dilakukan sistem dan kualitas apa yang harus dipenuhinya**, dalam bentuk yang dapat diverifikasi. BRD mencatat kebutuhan bisnis; PRD menjelaskan kebutuhan produk; SAD dan ADR menjelaskan rancangan serta keputusan teknis. SRS dapat merujuk ke keputusan arsitektur yang sudah ada tanpa menganggap rancangan itu sebagai requirement baru.

Repository saat ini memakai nama file `docs/01-requirements/system-requirements.md` dan dokumentasi menyebut SRD. Keputusan: gunakan **SRS** sebagai nama standar untuk dokumen system requirements tersebut, tetap pertahankan path lama. Ini tidak menyatakan bahwa semua dokumen bernama SRD otomatis sesuai dengan standar SRS baru.

## 16 bagian yang disetujui — nama dan urutan

| No. | Heading yang diusulkan | Isi yang diharapkan |
| --- | --- | --- |
| 1 | Document Information | Judul, versi dokumen, status, pemilik dan tanggal. |
| 2 | Introduction | Tujuan, ruang lingkup, definisi dan referensi sumber. |
| 3 | System Overview | Ringkasan sistem dan layanan yang disediakan. |
| 4 | System Context & Boundaries | Batas sistem, pihak dan sistem eksternal yang berinteraksi. |
| 5 | Actors & Roles | Aktor, peran dan tanggung jawab yang relevan. |
| 6 | Functional Requirements | Perilaku sistem, kondisi dan kriteria verifikasi per requirement. |
| 7 | Non-Functional Requirements | Kualitas sistem dengan ukuran dan kondisi uji jika dapat ditetapkan. |
| 8 | Business Rules & Constraints | Aturan bisnis dan batasan yang berlaku beserta sumber; tautkan ke dokumen sumber untuk menghindari duplikasi. |
| 9 | Data Requirements | Data yang diperlukan, aturan dan kebutuhan perlindungan yang berlaku. |
| 10 | External Interface Requirements | Kebutuhan antarmuka dengan pengguna, sistem atau layanan eksternal. |
| 11 | State & Workflow Specifications | Keadaan dan transisi atau alur yang relevan. |
| 12 | Error & Exception Handling | Respons yang diharapkan ketika terjadi kegagalan atau pengecualian. |
| 13 | Security & Access Requirements | Kebutuhan keamanan, akses dan privasi yang relevan dengan risiko. |
| 14 | Assumptions & Dependencies | Asumsi dan ketergantungan, dipisahkan dari fakta terverifikasi. |
| 15 | Verification & Acceptance Criteria | Metode verifikasi dan kriteria penerimaan yang berlaku. |
| 16 | Traceability Matrix | Hubungan sumber, requirement sistem, rancangan dan verifikasi yang diketahui. |

Usulan format: 16 heading tingkat dua (`##`) menggunakan nama dan urutan di atas. Jika bagian tidak berlaku, tulis `Not applicable` dan alasannya; jika informasi belum diketahui, tulis `TBD`. `TBD` bukan bukti selesai atau persetujuan. Penilaian relevansi tetap memerlukan review; validator tidak dapat membuktikannya hanya dari teks.

## Usulan aturan requirement

| Field | Usulan |
| --- | --- |
| ID | Pertahankan format yang sudah digunakan proyek untuk jenis requirement yang sama. Jika belum ada format, gunakan `FR-001` untuk fungsional dan `NFR-001` untuk nonfungsional. ID stabil dan tidak digunakan ulang. |
| Description | Satu kebutuhan yang jelas dan dapat diverifikasi. Bedakan perilaku/kualitas yang diwajibkan dari keputusan desain. |
| Source | Referensi ke product requirement atau sumber lain yang berwenang. Jangan mengarang sumber; `TBD` jika belum diketahui. |
| Priority | Usulan `Must`, `Should`, `Could`, atau `TBD` untuk proyek tanpa konvensi prioritas yang disepakati. Prioritas existing tidak dipetakan otomatis. |
| Preconditions | Kondisi awal yang diperlukan, jika relevan; gunakan `Not applicable` dengan alasan jika tidak berlaku, atau `TBD` jika belum diketahui. |
| Expected behavior / criterion | Perilaku dan hasil teramati untuk FR; ukuran, satuan, kondisi pengukuran dan ambang untuk NFR bila dapat ditentukan. Tidak membuat target fiktif. |
| Failure conditions | Respons yang diperlukan ketika terjadi kegagalan, jika relevan. |
| Verification method | Cara memeriksa, misalnya test, inspection, analysis atau demonstration, sesuai kebutuhan. Ini adalah rencana, bukan bukti pengujian sudah dilakukan. |
| Status | Usulan `Draft`, `In review`, `Approved`, `Deferred`, atau `TBD`. Nilai `Approved` saja bukan bukti identitas atau wewenang pemberi persetujuan. Status requirement terpisah dari status dokumen. |

Kebutuhan yang belum lengkap dapat dicatat sebagai draft dengan `TBD` dan harus dilaporkan. Usulan ini belum menetapkan apakah setiap field di atas menjadi kolom tabel wajib atau apakah sebagian dapat dirujuk ke bagian lain; hal itu perlu disetujui sebelum implementasi validator.

## Contoh ilustratif — bukan requirement proyek

| ID | Description | Source | Expected behavior / criterion | Verification method | Status |
| --- | --- | --- | --- | --- | --- |
| FR-001 | Sistem memungkinkan pengguna mengirim permintaan. | PR-001 | Permintaan yang valid menghasilkan konfirmasi kepada pengguna. | Test | Draft |
| NFR-001 | Waktu respons untuk pengiriman permintaan memenuhi target yang disetujui. | PR-001 | Target dan kondisi pengukuran: TBD. | Test | Draft |

ID sumber dan perilaku di atas hanya ilustrasi. Sumber `PR-001`, target, hasil pengujian dan persetujuan belum diverifikasi. Untuk NFR, reviewer perlu menetapkan ambang dan kondisi nyata sebelum menjadikannya kriteria penerimaan yang lengkap.

## Usulan validasi dan batasnya

- **Deterministik:** heading, urutan, metadata, field wajib yang disepakati, format/duplikasi ID, nilai enum, dan referensi yang dapat ditemukan pada sumber yang dipilih. `TBD` dilaporkan sebagai belum lengkap. Ketentuan error versus warning perlu ditetapkan per field sebelum implementasi.
- **Review semantik:** kejelasan, kelengkapan, konsistensi, testability, relevansi keamanan, dan keselarasan dengan sumber. Keberadaan ID tidak membuktikan hubungan tersebut benar secara makna.
- **Persetujuan manusia:** keputusan owner/reviewer dan bukti terpisah; status atau hasil validator tidak membuktikan otorisasi.
- **Traceability:** hubungan ke PRD atau sumber lain yang berwenang, lalu desain dan verifikasi jika relevan. Validator SRS dapat memeriksa keberadaan ID pada satu PRD kanonis yang dipilih, tetapi tidak memverifikasi otoritas atau kesesuaian makna. Pemeriksaan PRD ke BRD yang ada hanya memeriksa keberadaan ID dalam BRD yang dipilih.
- **Profil:** Lean dapat menggabungkan requirements sesuai standar saat ini; Standard dan Business Critical mengikuti kebutuhan artefak dan gate existing. Jangan otomatis menambahkan dokumen wajib atau mengurangi kontrol keamanan.

## Keputusan untuk owner

1. Struktur 16 heading dan penggunaan nama SRS dengan path lama telah disetujui pada 2026-11-23.
2. [Aturan detail dan format tabel](srs-requirement-fields.md) disetujui pada 2026-11-24.
