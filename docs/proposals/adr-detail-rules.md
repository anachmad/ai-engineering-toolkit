# Usulan aturan rinci ADR untuk review

Status: **Struktur dan aturan field disetujui pengguna.** Template dan validator ADR v1 tersedia; penerapan otomatis berdasarkan profil dan pemeriksaan ID lintas dokumen belum ditegakkan.

## Metadata yang diusulkan

| Field | Aturan usulan |
| --- | --- |
| ID | Wajib, stabil dan unik dalam scope proyek yang disepakati. Pertahankan format existing; gunakan `ADR-001` bila belum ada format. Jangan menggunakan kembali ID keputusan lama. |
| Title | Judul singkat yang menjelaskan keputusan. |
| Decision status | `Proposed`, `Accepted`, `Rejected`, `Superseded`, atau `TBD`. `Accepted` atau `Rejected` adalah catatan status, bukan bukti identitas atau kewenangan approver. |
| Document status | Mengikuti standar dokumentasi project: `draft`, `in-review`, `approved`, atau `deprecated`. Status ini terpisah dari status keputusan. |
| Decision owner | Orang atau peran yang bertanggung jawab; `TBD` jika belum diketahui. |
| Date | Tanggal keputusan jika diketahui; `TBD` jika belum ditetapkan. Gunakan `YYYY-MM-DD` jika tanggal diisi. |
| Approval / evidence | Referensi ke bukti review atau approval yang tersedia, atau `TBD`. Keberadaan teks/tautan bukan verifikasi independen. |
| Supersedes / superseded by | Referensi ADR terkait jika berlaku; `Not applicable — alasan` jika tidak berlaku, atau `TBD` jika belum diketahui. |

Usulan format: tabel `Field | Value` pada bagian **Metadata & Status**. Field wajib memuat nilai atau `TBD`. Aturan `Not applicable` di atas hanya berlaku untuk hubungan penggantian yang memang tidak berlaku; alasan dan status tetap ditinjau manusia.

## Isi yang diusulkan

- **Context:** jelaskan masalah dan batasan yang diketahui, disertai sumber jika ada.
- **Decision Drivers:** rujuk kebutuhan, risiko atau atribut kualitas yang relevan; gunakan ID proyek yang sudah ada.
- **Considered Options:** catat pilihan yang benar-benar dipertimbangkan. Jika belum diketahui, tulis `TBD`; jangan menciptakan alternatif demi mengisi template.
- **Decision:** jelaskan pilihan dan batasnya, serta tandai sebagai usulan bila belum diputuskan.
- **Rationale & Trade-offs:** catat alasan dan konsekuensi positif/negatif yang diketahui. `TBD` bila belum dianalisis.
- **Consequences:** catat dampak, risiko, tindak lanjut dan hal yang masih belum diketahui.
- **Related Requirements & References:** tautkan sumber dan dokumen terkait yang tersedia; tandai referensi yang belum diverifikasi.

## Contoh ilustratif — bukan keputusan proyek

| Field | Value |
| --- | --- |
| ID | ADR-001 |
| Title | Penyimpanan catatan keputusan |
| Decision status | Proposed |
| Document status | draft |
| Decision owner | TBD |
| Date | TBD |
| Approval / evidence | TBD |
| Supersedes / superseded by | Not applicable — belum ada keputusan sebelumnya yang diketahui |

Contoh ini hanya ilustrasi. Nomor dan alasan di atas tidak menyatakan keputusan tersebut benar-benar ada pada suatu proyek.

## Hasil validasi yang diusulkan

| Kondisi | Hasil | Batas |
| --- | --- | --- |
| Heading salah urutan/hilang, metadata wajib hilang, ID salah format, nilai status/tanggal tidak sesuai | ERROR | Format ID project existing harus dapat dikonfigurasi; jangan memaksa migrasi otomatis. |
| Field `TBD`, data atau referensi belum diverifikasi | WARN | Tidak berarti keputusan lengkap atau siap disetujui. |
| `Not applicable` tanpa alasan, atau dipakai pada field yang tidak diizinkan | ERROR | Kecukupan alasan tetap ditinjau manusia. |
| Referensi lokal yang secara eksplisit dipilih untuk diperiksa tidak ada | ERROR | Keberadaan file/ID tidak membuktikan isi, makna atau approval. |
| Sumber eksternal atau format yang tidak didukung | NOT VERIFIED / WARN | Jangan menganggap valid atau tidak valid tanpa bukti. |
| Keputusan, alternatif, trade-off, risiko keamanan dan approval | Review manusia / NOT VERIFIED | Validator deterministik tidak menentukan kualitas keputusan atau otoritas approver. |

Perilaku validator pada ADR lama dan penerapannya menurut profil harus disepakati tanpa otomatis mewajibkan migrasi atau menurunkan kontrol keamanan.

## Keputusan untuk review

1. Apakah metadata di atas dan pemisahan status dokumen vs keputusan sesuai?
2. Apakah pilihan status `Proposed`, `Accepted`, `Rejected`, `Superseded`, dan `TBD` sesuai?
3. Apakah pendekatan validasi dan pelestarian ADR existing sesuai?

Setelah disetujui, siapkan kontrak berversi, template, contoh sintetis dan validator beserta tes positif/negatif. Penerapan profil dan pemeriksaan lintas dokumen yang belum disetujui harus tetap dilaporkan sebagai belum ditegakkan.
