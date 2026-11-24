# SAD ringkas dan pemeriksaan referensi — keputusan dan usulan rinci

Status: **Arah dan detail disetujui pengguna.** SAD v2 implements mode selection and staged local checks; semantic review, unsupported references and quality gates remain separate.

## Keputusan yang disetujui

- **1B — Penerapan fleksibel:** Lean menggunakan arsitektur ringkas; Standard dapat menggunakan SAD ringkas atau lengkap berdasarkan keputusan pemilik proyek; Business Critical menggunakan SAD lengkap 18 bagian.
- **2B — Pemeriksaan bertahap:** periksa tautan file lokal dan keberadaan ID terhadap dokumen sumber yang dipilih secara eksplisit ketika didukung. Sumber yang tidak dapat diperiksa dilaporkan `NOT VERIFIED`.

Keputusan ini tidak mengubah kewajiban keamanan, dokumentasi, quality gate atau approval lain yang sudah berlaku untuk masing-masing profil. SAD v2 memeriksa mode profil dan referensi yang didukung; SAD v1 tetap tersedia untuk pemeriksaan struktur lengkap.

## Usulan kriteria SAD ringkas

Gunakan file existing `docs/02-architecture/architecture.md` dengan bagian berikut, memakai heading yang sudah disetujui untuk SAD lengkap:

1. `Document Information` — judul, versi, status, pemilik dan tanggal.
2. `Architecture Goals & Drivers` — kebutuhan utama, batasan dan tautan ke sumber yang tersedia.
3. `System Context` — batas sistem, pengguna atau aktor, serta sistem eksternal yang relevan.
4. `High-Level Architecture` — komponen utama, tanggung jawab dan hubungan atau alur penting.
5. `Security Architecture` — aset, batas kepercayaan, akses dan kontrol yang relevan dengan risiko; tautkan review keamanan atau threat model bila ada.
6. `Architecture Decisions & Trade-offs` — keputusan penting, alasan, alternatif atau tautan ADR.
7. `Risks & Technical Debt` — risiko dan hal yang belum diketahui, termasuk pemilik atau tindak lanjut bila diketahui.
8. `Architecture Validation & Traceability` — sumber requirement, metode verifikasi, bukti yang ada dan gap yang belum diselesaikan.

Tuliskan `TBD` jika belum diketahui, atau `Not applicable — alasan` jika bagian tidak relevan. Pemilik dan reviewer menilai apakah alasan, keamanan, operasi, pemulihan dan bukti memadai. Bagian ringkas tidak menggantikan kewajiban runbook, rollback, security review, atau approval profil yang sudah ada. Usulan ini menggunakan teks atau tautan yang ringkas; kewajiban tabel SAD lengkap tidak otomatis diterapkan pada SAD ringkas.

### Pemilihan untuk Standard

Usulan: pemilik merekam pilihan `concise` atau `full` dalam konfigurasi project yang versioned; jika belum ada pilihan, hasil audit `REVIEW_REQUIRED`, bukan otomatis memilih mode atau menyatakan proyek lolos. Letak dan skema field tersebut memerlukan perubahan yang kompatibel dengan manifest v1 dan pengujian migrasi. Proyek Business Critical tidak menjadi siap rilis hanya karena SAD lengkap.

## Usulan pemeriksaan bertahap

| Situasi | Hasil usulan | Penjelasan |
| --- | --- | --- |
| Tautan relatif ke file lokal yang berada dalam root project, dan file ada | `CHECKED_FILE_EXISTS` | Hanya keberadaan file, bukan isi, otoritas atau persetujuannya. |
| Tautan relatif ke file lokal yang secara eksplisit perlu diperiksa dan file tidak ada | `ERROR` | Berikan lokasi tautan dan path agar dapat diperbaiki. |
| ID requirement atau ADR, dengan sumber dan format yang dipilih secara eksplisit dan didukung | `CHECKED_ID_EXISTS` atau `ERROR` jika tidak ditemukan | Keberadaan ID tidak membuktikan hubungan semantik, kelengkapan atau approval. |
| Sumber eksternal, URL, format atau jenis referensi yang belum didukung, sumber belum dipilih, atau anchor belum diperiksa | `NOT VERIFIED` / `WARN` | Jangan menganggap sumber valid atau tidak valid tanpa bukti. |
| File sumber yang dipilih tidak dapat dibaca atau memiliki format tidak didukung | `NOT VERIFIED` dan kegagalan pemeriksaan yang diminta | Jangan mengubahnya menjadi PASS; laporkan error yang dapat ditindaklanjuti. |
| Path keluar dari root project atau melewati symlink ke luar root | `ERROR` | Jangan membaca target di luar cakupan pemeriksaan lokal yang dipilih. |
| `TBD` atau data yang belum tersedia | `WARN` | Bukan bukti selesai, lolos gate atau approval. |

Usulan cakupan awal: tautan Markdown relatif ke file lokal; URL eksternal, anchor, tautan dalam code fence, dan tautan dinamis tidak diverifikasi dan harus dilaporkan sesuai konteks. Path project dan dokumen sumber ditentukan secara eksplisit. Jangan mengeksekusi konten sumber. Format daftar ID, jenis dokumen sumber, dan cara menandai mana referensi yang wajib dicek harus ditetapkan dalam kontrak machine-readable sebelum implementasi. Ini belum merupakan jaminan bahwa semua sintaks Markdown dapat diparse.

## Keputusan lanjutan

Delapan bagian, pilihan Standard dan cakupan awal pemeriksaan telah disetujui. Format referensi kompleks dan sumber selain BR/PR tetap perlu review lanjutan.

Setelah detail disetujui: buat kontrak versi baru dan konfigurasi yang kompatibel, implementasikan pemeriksaan secara bertahap, serta uji proyek temporary, link yang rusak, path di luar root, sumber yang belum dipilih, versi sebelumnya, dan profil existing. Simpan hasil teknis, review semantik, dan persetujuan manusia secara terpisah.
