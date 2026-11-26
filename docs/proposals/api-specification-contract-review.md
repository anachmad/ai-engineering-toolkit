> Keputusan: disetujui oleh pemilik proyek; standar dan aturan rinci diimplementasikan sebagai API v1.

# Usulan standar API Specification untuk review

Status: **Struktur dan aturan rinci disetujui; template dan validator API v1 tersedia.** Isi berikut mempertahankan catatan proposal untuk jejak keputusan.

## Tujuan dan posisi

API Specification menjelaskan kontrak antarmuka yang dibutuhkan konsumen dan penyedia API: operasi, input/output, autentikasi, kesalahan, kompatibilitas, batas dan cara memverifikasinya. Dokumen harus membedakan kontrak yang disetujui, usulan dan perilaku sistem yang sudah diverifikasi.

SRS menjelaskan kebutuhan antarmuka; SAD memberi konteks integrasi dan keputusan arsitektur. API Specification memberikan detail kontrak yang relevan dan merujuk ke sumber tersebut tanpa menyalin informasi yang tidak perlu.

Jika proyek telah memiliki kontrak machine-readable seperti OpenAPI, usulan: dokumen Markdown menjadi panduan dan indeks yang **menautkan ke kontrak berwenang dan versinya**, bukan membuat salinan endpoint dan schema yang bersaing. Jika sumber tidak cocok, catat konflik untuk review; jangan menetapkan mana yang benar tanpa keputusan pemilik. OpenAPI digunakan bila sesuai, bukan diwajibkan untuk semua jenis API.

## Sembilan bagian yang disetujui — nama dan urutan

| No. | Heading | Isi yang diharapkan |
| --- | --- | --- |
| 1 | Metadata | Judul, versi dokumen, status, pemilik dan tanggal. |
| 2 | Overview | Tujuan, cakupan, konsumen dan sumber kontrak yang relevan. |
| 3 | Authentication & Authorization | Persyaratan autentikasi dan otorisasi yang berlaku, serta sumber kebijakan terkait. |
| 4 | Endpoint Catalog | Daftar operasi atau tautan ke katalog kontrak berwenang; bedakan versi dan statusnya. |
| 5 | Request/Response Contracts | Struktur input/output, schema dan contoh sintetis, atau tautan langsung ke kontrak berwenang. |
| 6 | Error Handling | Format dan perilaku kesalahan yang diketahui; tautkan definisi berwenang bila sudah tersedia. |
| 7 | Versioning & Compatibility | Kebijakan versi, perubahan kompatibel/tidak kompatibel dan penghentian bila sudah diputuskan. |
| 8 | Security & Limits | Perlindungan dan batas yang relevan dengan permukaan serta risiko API; nilai yang belum diketahui tetap TBD. |
| 9 | Testing & References | Hubungan ke requirement, metode pengujian, bukti yang tersedia dan referensi kontrak. |

Usulan format: ketika dokumen API terpisah digunakan, sembilan heading tingkat dua (`##`) dipertahankan sesuai nama dan urutan di atas. Jika bagian tidak berlaku, tulis `Not applicable — alasan`; jika informasi belum diketahui, gunakan `TBD`. Alasan, makna dan kelengkapan tetap memerlukan review manusia.

## Prinsip penerapan

- **Applicability:** API Specification terpisah tidak otomatis wajib untuk semua proyek; kebutuhan dokumen dan kedalamannya mengikuti permukaan API, risiko dan governance yang berlaku.
- **Lokasi:** jika dibutuhkan sebagai file terpisah, usulan `docs/02-architecture/api-specification.md`. Pertahankan lokasi file kontrak machine-readable yang sudah digunakan proyek; tidak ada migrasi otomatis.
- **Sumber berwenang:** cantumkan path atau tautan, versi dan status kontrak yang menjadi acuan. Validator tidak boleh menganggap setiap file referensi sebagai benar atau disetujui.
- **Keamanan:** deskripsikan kontrol yang relevan dengan risiko aktual; jangan membuat endpoint, izin, nilai limit, bukti security test atau klaim implementasi yang tidak ada di sumber.
- **Contoh dan data:** gunakan contoh sintetis yang ditandai; jangan menaruh credential, token atau data produksi dalam dokumen.
- **Perubahan:** perubahan kontrak harus dinilai dampaknya pada konsumen dan kompatibilitas; mekanisme approval tetap mengikuti standar project.

## Batas validasi awal yang diusulkan

Pemeriksaan deterministik dapat memeriksa heading, urutan, metadata, tabel atau referensi yang sudah ditentukan pada kontrak. Ketersediaan file OpenAPI tidak membuktikan isinya valid atau sesuai implementasi. Pemeriksaan sintaks/semantik OpenAPI, pengujian endpoint, keamanan, kompatibilitas nyata dan approval manusia memerlukan mekanisme dan evidence terpisah; jangan mengklaimnya sampai benar-benar dijalankan.

## Keputusan untuk owner

1. Struktur, lokasi rekomendasi dan pendekatan OpenAPI telah disetujui pengguna.
2. Tinjau [aturan rinci](api-specification-detail-rules.md) sebelum mengaktifkan template atau validator.

Setelah struktur disetujui, metadata, format tabel, aturan sumber berwenang, dan batas validasi perlu direview terpisah sebelum template atau validator diaktifkan.
