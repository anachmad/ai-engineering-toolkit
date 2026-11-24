# Usulan aturan field SRS

Status: **Aturan field dan tabel disetujui oleh pengguna pada 2026-11-24.** Validator SRS v1 dan konfigurasi ID/prioritas tersedia. Pemeriksaan lintas dokumen terbatas pada keberadaan ID dalam satu tabel PRD yang dipilih; lihat panduan validasi untuk keterbatasan.

## Usulan tabel requirement

Gunakan dua tabel terpisah pada bagian **Functional Requirements** dan **Non-Functional Requirements**, dengan kolom yang sama agar mudah dibaca dan divalidasi:

| ID | Description | Source | Priority | Preconditions | Expected behavior / criterion | Failure conditions | Verification method | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

| Field | Usulan aturan |
| --- | --- |
| ID | Wajib unik dalam dokumen dan stabil; pertahankan format existing untuk jenis requirement terkait. Jika belum ada, gunakan `FR-001` untuk fungsi atau `NFR-001` untuk kualitas. Jangan gunakan ulang ID yang telah dipensiunkan. |
| Description | Jelaskan satu kebutuhan sistem yang jelas dan dapat diperiksa. |
| Source | Cantumkan ID product requirement atau sumber lain yang diakui pemilik proyek; beberapa sumber dipisah koma. `TBD` jika belum diketahui. Kewenangan sumber perlu review manusia. |
| Priority | Gunakan `Must`, `Should`, `Could`, atau `TBD` jika belum ada konvensi prioritas proyek. Pertahankan konvensi existing; pemetaan ke nilai ini tidak otomatis. Format konfigurasi prioritas proyek memerlukan desain tersendiri. |
| Preconditions | Kondisi sebelum perilaku berlaku. Gunakan `N/A` dengan alasan pada field yang sama jika memang tidak relevan, atau `TBD` jika belum diketahui. |
| Expected behavior / criterion | FR: hasil yang teramati. NFR: ukuran, satuan, kondisi pengukuran, dan ambang bila dapat ditentukan. Gunakan `TBD` untuk unsur yang belum diketahui; jangan mengarang target. |
| Failure conditions | Respons saat gagal jika relevan; gunakan `N/A` dengan alasan jika tidak berlaku atau `TBD` jika belum diketahui. |
| Verification method | Metode yang direncanakan: `Test`, `Inspection`, `Analysis`, `Demonstration`, atau `TBD`. Metode bukan bukti pelaksanaan. |
| Status | `Draft`, `In review`, `Approved`, `Deferred`, atau `TBD`. `Approved` adalah klaim yang tetap membutuhkan bukti persetujuan manusia. Status requirement berbeda dari status dokumen. |

`N/A` tidak boleh dipakai untuk menghilangkan ID, deskripsi, sumber, hasil/kriteria, metode verifikasi, atau status. Apabila sebuah kolom membutuhkan penjelasan panjang, usulan: isi sel dengan tautan atau referensi ke bagian SRS terkait, dengan ketentuan tetap dapat ditelusuri oleh reviewer. Pemeriksaan otomatis terhadap isi dokumen yang ditautkan belum ditentukan.

## Contoh ilustratif

Bukan requirement Filio atau proyek nyata; ID sumber dan hasil tes di bawah belum diverifikasi.

| ID | Description | Source | Priority | Preconditions | Expected behavior / criterion | Failure conditions | Verification method | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FR-001 | Sistem memungkinkan pengguna mengirim permintaan. | PR-001 | Must | Pengguna telah masuk. | Permintaan valid menghasilkan konfirmasi. | Jika data wajib hilang, sistem meminta pengguna melengkapinya. | Test | Draft |
| NFR-001 | Sistem memenuhi target waktu respons pengiriman. | PR-001 | TBD | Kondisi uji: TBD. | Ambang, satuan dan metode pengukuran: TBD. | N/A — tidak ada respons khusus yang telah ditetapkan. | Test | Draft |

Contoh NFR di atas belum lengkap: target, kondisi, prioritas, dan alasan tidak adanya respons khusus harus diputuskan pemilik; jangan menganggap contoh sebagai target atau pengecualian yang disetujui.

## Usulan hasil validasi

| Situasi | Hasil yang diusulkan | Batas |
| --- | --- | --- |
| Bagian atau tabel wajib hilang, urutan salah, kolom hilang, baris rusak, atau sel kosong | ERROR | Berlaku pada kontrak yang telah disetujui; isi yang belum diketahui ditulis `TBD`, bukan dibiarkan kosong. |
| ID salah format atau duplikat | ERROR | Gunakan format proyek yang dipilih secara eksplisit; format lain jangan ditebak. |
| Priority, verification method atau status di luar nilai yang berlaku | ERROR | Konvensi existing perlu dikonfigurasi dulu, bukan diubah otomatis. |
| Sel berisi `TBD`, termasuk baris template | WARN | Menandakan belum lengkap; bukan bukti bahwa requirement siap diterima. |
| `N/A` tanpa alasan atau pada field yang tidak diizinkan | ERROR | Penggunaan dan alasan tetap perlu ditinjau manusia. |
| Sumber tidak dipilih, tidak tersedia, atau sumber eksternal | WARN / NOT VERIFIED | Tidak boleh menyatakan sumber ada atau berwenang tanpa pemeriksaan. |
| ID sumber diperiksa dan tidak ditemukan | ERROR | Validator memeriksa keberadaan ID dalam satu PRD kanonis yang dipilih; tidak memverifikasi makna atau otoritas sumber. |
| Makna, testability, kesesuaian keamanan, authority dan approval | Human review / NOT VERIFIED | Lolos validasi tidak berarti dokumen disetujui atau pengujian telah dilakukan. |

## Keputusan untuk review

1. Apakah dua tabel sembilan kolom dan aturan isinya sesuai? Pertimbangkan apakah Preconditions dan Failure conditions perlu menjadi kolom tersendiri.
2. Apakah nilai priority, metode verifikasi, status dan aturan `N/A` / `TBD` sesuai?
3. Apakah ERROR dan WARN di atas sesuai, dengan ketentuan sumber existing dan prioritas proyek tidak diubah secara diam-diam?

Setelah disetujui, siapkan template, kontrak machine-readable dan validator secara bertahap, uji perilaku positif/negatif serta pertahankan file project existing. Tentukan spesifikasi konfigurasi ID/prioritas dan pemeriksaan lintas dokumen sebelum menyatakan fitur tersebut terimplementasi.
