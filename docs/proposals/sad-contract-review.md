# Usulan kontrak SAD untuk review

Status: **18 heading dan lokasi SAD disetujui oleh pengguna.** Aturan rinci dan format tabel disetujui; template dan validator SAD v1 tersedia. Penerapan berdasarkan profil dan pemeriksaan referensi belum ditegakkan.

## Tujuan dan posisi

SAD (Software Architecture Document) menjelaskan bagaimana sistem dirancang untuk memenuhi kebutuhan dan batasan yang berlaku. SRS mencatat apa yang dibutuhkan; SAD menjelaskan struktur, aliran, keputusan dan trade-off arsitektur. SAD harus menunjuk ke requirement, ADR, threat model dan runbook yang relevan tanpa menyalin isinya secara tidak perlu.

Repository sudah menggunakan `docs/02-architecture/architecture.md`. Keputusan: gunakan file tersebut sebagai lokasi SAD, tanpa memindahkan atau menimpa dokumen yang sudah ada. Profil Lean tetap dapat menggunakan arsitektur ringkas sesuai standar existing; keberadaan standar SAD tidak otomatis mewajibkan file terpisah atau mengubah quality gate profil.

## 18 bagian yang disetujui — nama dan urutan

| No. | Heading | Isi yang diharapkan |
| --- | --- | --- |
| 1 | Document Information | Judul, versi dokumen, status, pemilik dan tanggal. |
| 2 | Architecture Executive Summary | Ikhtisar sistem dan keputusan arsitektur utama. |
| 3 | Architecture Goals & Drivers | Kebutuhan, atribut kualitas dan batasan yang mendorong rancangan; rujuk requirement sumber. |
| 4 | System Context | Batas sistem, aktor, sistem eksternal dan hubungan utama. |
| 5 | Architecture Principles | Prinsip yang dipakai dan alasan atau sumbernya. |
| 6 | Technology Stack | Teknologi yang diketahui atau diusulkan, status keputusan dan batas penerapannya. |
| 7 | High-Level Architecture | Gambaran komponen dan aliran utama; sertakan diagram bila membantu. |
| 8 | Application & Component Design | Tanggung jawab komponen dan hubungan antarkomponen. |
| 9 | Data Architecture | Aliran, penyimpanan, kepemilikan, sensitivitas dan retensi data yang relevan. |
| 10 | Integration Architecture | Integrasi, antarmuka, batas kepercayaan dan kegagalan yang relevan. |
| 11 | Security Architecture | Kontrol dan trust boundary sesuai risiko; tautkan threat model dan security review jika ada. |
| 12 | Infrastructure & Deployment | Lingkungan, dependensi dan rancangan deployment yang diketahui. |
| 13 | Reliability & Availability | Kebutuhan keandalan, pemulihan, backup dan asumsi kegagalan yang berlaku. |
| 14 | Performance & Scalability | Driver kinerja, kapasitas dan strategi skala; target yang belum diketahui ditulis TBD. |
| 15 | Observability & Operations | Monitoring, logging, alert dan kepemilikan operasional; tautkan runbook yang relevan. |
| 16 | Architecture Decisions & Trade-offs | Keputusan, alternatif, alasan dan konsekuensi; tautkan ADR untuk keputusan signifikan. |
| 17 | Risks & Technical Debt | Risiko, dampak, pemilik dan utang teknis yang diketahui; tandai hal yang belum diputuskan. |
| 18 | Architecture Validation & Traceability | Hubungan requirement → keputusan/kontrol → metode verifikasi dan bukti yang tersedia. |

Usulan format: gunakan heading tingkat dua (`##`) dengan nama dan urutan di atas saat SAD lengkap diperlukan. Jika bagian tidak berlaku, tulis `Not applicable` dan alasan; jika belum diketahui, gunakan `TBD`. Penentuan relevansi dan kecukupan tetap memerlukan review manusia.

## Usulan aturan mutu

- Rujuk FR/NFR atau sumber lain yang relevan dan berwenang; pertahankan format ID proyek yang sudah ada. Jangan membuat hubungan atau target yang tidak tercantum dalam sumber.
- Jelaskan alasan dan trade-off keputusan signifikan; tautkan ADR yang ada. Status keputusan yang masih diusulkan tidak boleh ditampilkan sebagai keputusan yang disetujui.
- Pastikan diagram sesuai dengan deskripsi dan berikan tanggal/versi atau konteks yang memadai. Konsistensi makna diagram memerlukan review manusia.
- Perlakukan keamanan, privasi, deployment, backup, pemulihan dan operasi sesuai risiko dan permukaan sistem yang benar-benar relevan. `TBD` bukan bukti kontrol tersedia atau telah diuji.
- Pisahkan kondisi yang terverifikasi, asumsi, pertanyaan terbuka, risiko dan keputusan. Jangan mengarang teknologi yang dipakai, target kinerja, bukti uji atau approval.
- Referensi ke SRS, ADR, threat model dan runbook cukup bila dokumen tersebut dapat ditemukan dan diperiksa. Format tabel/ID serta perilaku link rusak memerlukan review aturan rinci.

## Validasi yang dapat dipertimbangkan

Validator dapat memeriksa heading, urutan, metadata dan struktur referensi yang telah didefinisikan. Kecocokan arsitektur terhadap requirement, kecukupan kontrol, validitas diagram, trade-off, hasil pengujian dan persetujuan tetap memerlukan review semantik atau manusia. Validator SAD v1 tersedia untuk pemeriksaan struktur dan field; penerapan profil dan pemeriksaan referensi belum ditegakkan.

## Keputusan untuk owner

1. Heading dan lokasi telah disetujui pengguna; profil Lean tetap sesuai standar existing.
2. [Aturan rinci SAD](sad-detail-rules.md) telah disetujui; penerapan profil dan pemeriksaan link tetap membutuhkan keputusan tersendiri.
