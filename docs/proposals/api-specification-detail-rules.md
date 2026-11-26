> Keputusan: disetujui oleh pemilik proyek; standar dan aturan rinci diimplementasikan sebagai API v1.

# Usulan aturan rinci API Specification

Status: **Disetujui dan diimplementasikan sebagai API v1.** Isi berikut mempertahankan catatan proposal untuk jejak keputusan.

## Metadata yang diusulkan

Bagian Metadata menggunakan tabel `Field | Value`:

| Field | Aturan usulan |
| --- | --- |
| Title | Nama dokumen atau API; `TBD` bila belum diketahui. |
| Version | Versi dokumen; dibedakan dari versi API dan versi kontrak. |
| Status | `draft`, `in-review`, `approved`, `deprecated`, atau `TBD`; status teks bukan bukti approval. |
| Owner | Orang atau peran yang bertanggung jawab; `TBD` bila belum diketahui. |
| Date | Tanggal versi dokumen bila diketahui, `YYYY-MM-DD` atau `TBD`. |
| Contract source | Path/tautan kontrak API berwenang jika ada; `TBD` bila belum ditentukan atau `Not applicable — alasan` bila memang tidak berlaku. |
| Contract version | Versi kontrak berwenang; `TBD` bila belum diketahui atau `Not applicable — alasan` bila tidak berlaku. |

## Isi dan tabel yang diusulkan

### Authentication & Authorization

Jelaskan kebutuhan akses secara ringkas atau tautkan ke kebijakan/kontrak yang berwenang. Jangan menampilkan token, password atau kredensial aktif.

### Endpoint Catalog

Pilih salah satu:

1. Tautkan ke **kontrak berwenang** dan versinya jika katalog operasi sudah terdefinisi di sana; atau
2. Jika katalog belum tersedia, gunakan tabel berikut:

| Operation | Purpose | Version / status | Source |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

Nama operasi dan ID existing tetap dipertahankan; jangan membuat ID baru tanpa kebutuhan atau mengganti kontrak yang sudah ada. `TBD` tidak dianggap operasi yang tersedia.

### Request/Response Contracts

Rujuk schema dan contoh pada kontrak berwenang bila tersedia. Jika tidak ada, deskripsikan input/output yang diketahui dan tandai bagian yang masih `TBD`. Gunakan contoh sintetis, bukan data produksi atau kredensial.

### Error Handling; Versioning & Compatibility; Security & Limits

Jelaskan aturan yang diketahui atau tautkan ke sumber yang relevan. Ambang, limit, jadwal penghentian dan kontrol yang belum diputuskan tetap `TBD`; jangan menyatakan sistem sudah memenuhi aturan tanpa bukti.

### Testing & References

| Requirement / source | Contract or operation | Verification method | Evidence / status |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

Metode yang direncanakan bukan bukti eksekusi. Sumber yang tidak diperiksa dan approval manusia tetap harus dinyatakan belum diverifikasi.

## Usulan validasi dan batas

| Kondisi | Hasil usulan | Batas |
| --- | --- | --- |
| Heading, urutan, metadata atau tabel yang wajib hilang; field kosong | ERROR | Tidak mewajibkan tabel Endpoint Catalog jika merujuk kontrak berwenang sesuai format yang disepakati. |
| Tanggal atau status dokumen tidak sesuai format | ERROR | Status `approved` saja bukan bukti approval manusia. |
| `TBD` | WARN | Draft belum lengkap, bukan hasil uji atau approval. |
| `Not applicable` tanpa alasan | ERROR | Kecukupan alasan tetap perlu review manusia. |
| Kontrak lokal yang secara eksplisit dipilih untuk diperiksa tidak ditemukan | ERROR | Keberadaan file bukan bukti kontrak valid atau sesuai implementasi. |
| URL, sumber lain atau format yang tidak diperiksa | WARN / NOT VERIFIED | Jangan menyatakan valid atau invalid tanpa bukti. |
| Sintaks OpenAPI, kesesuaian runtime, security test, kompatibilitas dan approval | NOT VERIFIED | Memerlukan alat dan evidence terpisah; tahap awal tidak menginstal dependency atau memanggil API. |

## Keputusan untuk review

1. Apakah tujuh metadata field di atas sesuai, termasuk pemisahan versi dokumen dan versi kontrak?
2. Apakah Endpoint Catalog boleh berupa tautan ke kontrak berwenang atau tabel lokal alternatif?
3. Apakah aturan ERROR/WARN/NOT VERIFIED dan pembatasan bahwa validitas OpenAPI belum diuji secara otomatis sesuai?

Setelah disetujui, format representasi tautan kontrak dan keamanan path perlu ditetapkan secara jelas dalam kontrak machine-readable sebelum validator diaktifkan. Jangan memaksakan migrasi proyek atau menjadikan dokumen terpisah wajib secara otomatis.
