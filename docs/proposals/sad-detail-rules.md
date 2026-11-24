# Usulan aturan rinci SAD untuk review

Status: **Struktur dan aturan field disetujui pengguna.** Template dan validator SAD v1 tersedia; penerapan berdasarkan profil dan pemeriksaan referensi tetap belum ditegakkan.

## Aturan umum yang diusulkan

- Cantumkan judul, versi dokumen, status, pemilik, dan tanggal pada Document Information. Status dokumen mengikuti standar dokumentasi kanonis project.
- Gunakan 18 heading yang disetujui sesuai [review SAD](sad-contract-review.md). Jika sebuah bagian tidak berlaku, tulis `Not applicable` beserta alasan; jika belum diketahui, tulis `TBD`.
- Dokumentasikan sistem yang diketahui dan bedakan dari usulan, asumsi, risiko, pertanyaan terbuka dan keputusan. Jangan mengarang stack, hasil tes, target, mitigasi atau persetujuan.
- Hubungkan arsitektur ke requirement, ADR, threat model, security review dan runbook yang relevan. Gunakan tautan, hindari salinan yang mudah tidak sinkron.
- Pertahankan format ID yang sudah digunakan project; gunakan ID standar hanya bila project belum memiliki format yang sesuai. Jangan mengubah ID secara otomatis.
- Untuk Lean, struktur dan kedalaman penerapan perlu mengikuti profil yang sudah disetujui; tidak otomatis menambah dokumen atau gate wajib.

## Tabel yang diusulkan

Tabel berikut adalah format SAD lengkap yang disetujui. Setiap baris `TBD` merupakan placeholder, bukan keputusan, kebutuhan atau bukti.

### Architecture Goals & Drivers

| Source ID / reference | Driver or constraint | Architecture implication | Status / evidence |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

Tuliskan sumber requirement atau sumber lain yang berwenang, kebutuhan yang mendorong rancangan, dan implikasi yang diketahui. Target yang belum diputuskan tetap `TBD`.

### Architecture Decisions & Trade-offs

| Decision / ADR reference | Context | Decision or proposal | Alternatives and trade-offs | Status |
| --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD |

Gunakan ADR untuk keputusan signifikan dan rujuk lokasinya. Usulan nilai status untuk review: `Proposed`, `Accepted`, `Superseded`, atau `TBD`. Status `Accepted` adalah klaim yang membutuhkan bukti review/approval; validator tidak mengautentikasi pemberi persetujuan.

### Risks & Technical Debt

| Risk / debt | Impact | Owner | Mitigation or next step | Status |
| --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD |

Jelaskan dampak, pemilik dan langkah berikutnya berdasarkan informasi yang diketahui. Risiko yang belum dinilai tetap terbuka; jangan menyimpulkan bahwa risiko sudah tertangani hanya karena ada mitigasi yang direncanakan.

### Architecture Validation & Traceability

| Requirement / source | Architecture decision or control | Verification method | Evidence / status |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

Metode verifikasi adalah rencana, bukan bukti eksekusi. Jika bukti belum ada, catat `TBD` atau status yang sesuai; hubungan antar-ID yang belum diverifikasi harus tetap terlihat.

## Contoh ilustratif — bukan arsitektur proyek

| Decision / ADR reference | Context | Decision or proposal | Alternatives and trade-offs | Status |
| --- | --- | --- | --- | --- |
| ADR-001 | Pemilik membutuhkan catatan perubahan. | Usulan: simpan riwayat keputusan. | Opsi dan trade-off: TBD. | Proposed |

`ADR-001` dan isinya hanya ilustrasi; contoh ini tidak membuktikan ADR tersebut ada atau telah disetujui.

## Usulan hasil validasi

| Pemeriksaan | Hasil usulan | Batas |
| --- | --- | --- |
| Heading, urutan, metadata atau tabel wajib hilang; baris rusak atau sel kosong | ERROR | Struktur lengkap hanya diterapkan sesuai kontrak dan profil yang disepakati. |
| `TBD` atau informasi yang belum diverifikasi | WARN | Tidak menyatakan dokumen selesai, evidence tersedia, atau release siap. |
| `Not applicable` tanpa alasan | ERROR | Alasan relevansi tetap memerlukan review manusia. |
| Status keputusan di luar nilai yang disetujui | ERROR | Status valid saja tidak membuktikan approval. |
| Referensi yang dapat dicek tidak ditemukan | ERROR | Hanya bila sumber dan format pemeriksaan dipilih secara eksplisit; lainnya NOT VERIFIED. |
| Kecocokan diagram, mutu trade-off, kelengkapan kontrol, pengujian dan approval | Review manusia / NOT VERIFIED | Pemeriksaan struktur atau keberadaan ID tidak membuktikan makna, keamanan atau persetujuan. |

Validator SAD v1 tersedia secara eksplisit; aturan penerapan Lean/Standard/Business Critical dan format pemeriksaan link masih perlu diputuskan sebelum enforcement otomatis.

## Catatan persetujuan

Pengguna menyetujui tabel, nilai status dan aturan validasi. Penerapan profil dan pemeriksaan link tetap membutuhkan keputusan tersendiri.

Setelah disetujui, buat standar, template, contoh dan validator secara bertahap dengan pengujian serta pelestarian file existing. Jangan menambahkan gate atau requirement proyek baru tanpa keputusan yang relevan.
