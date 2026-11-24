# Usulan standar ADR untuk review

Status: **Delapan heading dan penggunaan indeks atau ADR terpisah disetujui pengguna.** Aturan field dan status disetujui; template dan validator ADR v1 tersedia. Pemeriksaan lintas dokumen dan penerapan profil belum ditegakkan.

## Tujuan dan posisi

ADR mencatat **satu keputusan arsitektur yang signifikan**, konteksnya, pilihan yang dipertimbangkan, alasan, trade-off dan konsekuensinya. SAD memberikan gambaran arsitektur dan dapat menunjuk ke ADR, sehingga keputusan tidak perlu diduplikasi dalam beberapa dokumen.

Repository sudah memiliki `docs/02-architecture/decisions.md` sebagai dokumen keputusan untuk profil Standard dan Business Critical, serta contoh ADR terpisah di `docs/adr/`. Keputusan: izinkan dokumen indeks yang menunjuk ke ADR terpisah atau kumpulan ADR yang terhubung, tanpa memindahkan atau menimpa dokumen yang sudah ada. Profil Lean tetap mengikuti ketentuan arsitektur ringkas existing; penerapan dan kedalaman ADR tetap proporsional dengan risiko dan signifikansi keputusan.

## Delapan bagian yang disetujui — nama dan urutan

| No. | Heading | Isi yang diharapkan |
| --- | --- | --- |
| 1 | Metadata & Status | ID, judul, status keputusan, pemilik, tanggal dan rujukan persetujuan yang tersedia. |
| 2 | Context | Masalah, batasan dan keadaan yang mendorong keputusan. |
| 3 | Decision Drivers | Kebutuhan, atribut kualitas, risiko dan pertimbangan yang memengaruhi pilihan. |
| 4 | Considered Options | Pilihan yang sungguh dipertimbangkan; jangan mengarang alternatif. |
| 5 | Decision | Keputusan yang dipilih atau usulan yang masih menunggu keputusan. |
| 6 | Rationale & Trade-offs | Alasan pilihan serta manfaat, kelemahan dan kompromi. |
| 7 | Consequences | Dampak, risiko, tindak lanjut dan hal yang masih belum diketahui. |
| 8 | Related Requirements & References | Tautan ke requirement, SAD, ADR terkait, sumber dan bukti yang relevan. |

Usulan format: gunakan delapan heading tingkat dua (`##`) dengan nama dan urutan tersebut saat membuat ADR baru. `TBD` menunjukkan informasi yang belum diketahui dan tidak berarti keputusan telah disetujui. Jika suatu bagian tidak berlaku, catat `Not applicable` beserta alasan; relevansinya tetap memerlukan review manusia.

## Ketentuan yang perlu ditetapkan pada review berikutnya

- **ID:** pertahankan format ID keputusan yang sudah digunakan proyek; `ADR-001` menjadi default bila belum ada format. Jangan mengganti ID atau tautan lama secara otomatis.
- **Status keputusan:** SAD saat ini menggunakan `Proposed`, `Accepted`, `Superseded`, dan `TBD`. Status ADR perlu disepakati dengan mempertimbangkan kemungkinan keputusan ditolak atau digantikan. Status keputusan tidak sama dengan status dokumen; label `Accepted` sendiri bukan bukti approval manusia.
- **Hubungan antarversi:** bila keputusan digantikan, tautkan ADR lama dan baru tanpa menghapus riwayat. Siapa yang berwenang menerima keputusan dan bagaimana bukti approval disimpan perlu ditentukan oleh proyek.
- **Validasi:** pemeriksaan deterministik dapat memeriksa heading, metadata, format ID, nilai status dan referensi yang didukung. Kecukupan alternatif, trade-off, keamanan, otoritas sumber dan approval tetap memerlukan review manusia.
- **Kompatibilitas:** contoh `docs/adr/ADR-001-route-capability-binding.md` memiliki format lebih ringkas. Tidak boleh dinyatakan salah atau ditulis ulang secara otomatis hanya karena standar baru diusulkan; proses adopsi existing perlu diputuskan sebelum enforcement.

## Keputusan untuk owner

1. Delapan heading dan penggunaan indeks atau ADR terpisah telah disetujui pengguna.
2. [Aturan rinci](adr-detail-rules.md) telah disetujui; template dan validator ADR v1 tersedia.
