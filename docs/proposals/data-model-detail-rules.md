# Usulan aturan rinci Data Model Specification

Status: **Struktur dan aturan field disetujui pengguna.** Validator v1 menggunakan perbandingan nama persis; perbedaan kapitalisasi diperingatkan. Referensi entitas eksternal memakai prefix `external:` dan tetap tidak terverifikasi. Penerapan berdasarkan profil tidak ditegakkan.

## Aturan umum yang diusulkan

- Bagian **Metadata** memakai tabel `Field | Value` dengan Title, Version, Status, Owner dan Date. Status dokumen mengikuti standar project: `draft`, `in-review`, `approved`, atau `deprecated`.
- Gunakan `TBD` untuk hal yang belum diketahui; gunakan `Not applicable — alasan` jika bagian tidak berlaku. Informasi `TBD` bukan bukti bahwa model lengkap, database sudah sesuai, atau keputusan disetujui.
- Catat sumber dan versi model atau skema yang berwenang. Bedakan rancangan usulan, kondisi terverifikasi dan asumsi. Jangan otomatis menganggap dokumen atau database benar ketika keduanya berbeda.
- Pertahankan nama dan ID entitas yang sudah digunakan project. Tidak ada ID baru yang diwajibkan oleh usulan ini; bila proyek belum memiliki ID, penamaan yang dipakai harus disepakati sebelum diberlakukan.
- Jangan memasukkan data pribadi nyata, kredensial atau contoh produksi. Jika contoh diperlukan, gunakan data sintetis yang jelas ditandai.

## Tabel yang diusulkan

### Data Domain & Ownership

| Domain | Description | Owner | Authoritative source / version |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

### Entity Catalog

| Entity | Description | Domain | Identifier / key | Source |
| --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD |

### Relationships & Cardinality

| From entity | Relationship | To entity | Cardinality | Source / notes |
| --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD |

Cardinality harus dijelaskan sesuai model dan sumber; daftar nilai baku belum dipaksakan, karena notasi project dapat berbeda. Perbedaan model yang belum diselesaikan ditandai `TBD` atau sebagai pertanyaan terbuka.

### Field Dictionary

| Entity | Field | Description | Type / format | Required | Sensitivity | Source |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD |

`Required` diusulkan menggunakan `Yes`, `No`, atau `TBD`. Klasifikasi `Sensitivity` mengikuti kebijakan data project yang berlaku; jika belum ditentukan, gunakan `TBD`, bukan menebak atau membuat klasifikasi baru.

### Constraints & Integrity

| Entity / field | Constraint / rule | Source | Verification |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

### Migration & Retention

| Data / change | Migration or retention need | Owner | Status / evidence |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

Metode atau rencana bukan bukti bahwa migrasi, backup, penghapusan atau uji pemulihan sudah berhasil.

### Validation & References

| Requirement / source | Model element | Verification method | Evidence / status |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

## Contoh ilustratif — bukan model project nyata

| Entity | Field | Description | Type / format | Required | Sensitivity | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Request | request_id | Identitas permintaan. | TBD | Yes | TBD | TBD |

Contoh ini hanya memperlihatkan bentuk tabel; tipe data, klasifikasi dan sumber belum diputuskan.

## Validasi yang diusulkan

| Kondisi | Hasil | Batas |
| --- | --- | --- |
| Heading, urutan, metadata, tabel wajib, atau field kosong tidak sesuai | ERROR | Berlaku ketika dokumen terpisah dipilih untuk menggunakan kontrak ini. |
| Nama entitas duplikat, atau kombinasi entitas–field duplikat | ERROR | Normalisasi huruf besar/kecil dan lingkup keunikan perlu disepakati sebelum implementasi. |
| Hubungan atau field merujuk ke entitas yang tidak ditemukan di Entity Catalog | ERROR jika tabel lokal sudah cukup untuk diperiksa | Referensi ke model eksternal atau bagian yang belum tersedia harus ditandai dan ditinjau, bukan otomatis dianggap valid. |
| `Required` bukan `Yes`, `No`, atau `TBD` | ERROR | `TBD` berarti belum lengkap. |
| Field `TBD`, sensitivitas atau sumber tidak diverifikasi | WARN / NOT VERIFIED | Jangan membuat label sensitivitas atau menyatakan compliance. |
| `Not applicable` tanpa alasan | ERROR | Kecukupan alasan memerlukan review manusia. |
| Database/skema aktual, makna, kontrol privasi, migrasi, retensi dan approval | NOT VERIFIED / review manusia | Tidak ada koneksi database atau inspeksi skema otomatis dalam tahap awal yang diusulkan. |

Detail seperti format referensi eksternal, cakupan pemeriksaan link, format tanggal metadata, dan normalisasi nama masih perlu disetujui sebelum aturan tersebut ditegakkan. Penerapan berdasarkan profil tetap terpisah dari struktur dokumen.

## Keputusan untuk review

1. Apakah tabel dan kolom di atas sesuai, atau perlu diringkas/ditambah?
2. Apakah `Required` menggunakan `Yes`, `No`, `TBD` dan sensitivitas mengikuti kebijakan proyek?
3. Apakah pemeriksaan entity/field duplikat dan referensi lokal sesuai, dengan kasus eksternal atau belum tersedia tetap terlihat sebagai belum diverifikasi?

Setelah disetujui, susun kontrak berversi, template, contoh sintetis dan validator bertahap; uji contoh valid/tidak valid tanpa menimpa dokumen existing.
