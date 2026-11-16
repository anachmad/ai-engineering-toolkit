# Filio Pilot — review awal keterkaitan BRD dan PRD

Tanggal: 2026-11-11. Status: **usulan untuk ditinjau pemilik produk**, bukan hubungan yang sudah disetujui atau bukti bahwa fitur sudah dibangun/diuji.

## Sumber dan batas pemeriksaan

- BRD: `/home/andik/project/filio-pilot/Filio_BRD_v2.md`, versi 2.0, draft strategis dan belum disetujui pemilik produk. BR tercantum pada baris 113–126.
- PRD: `/home/andik/project/filio-pilot/Filio_PRD_v2-1.md`, header menyatakan versi 2.0, draft untuk review dan merujuk ke BRD di atas. Tabel fitur utama pada baris 86–149. Tidak ditemukan referensi eksplisit `BR-xx` dalam PRD.
- File di `docs/01-requirements/business-requirements.md` dan `product-requirements.md` masih berisi placeholder. Pemeriksaan ini menggunakan dua file di root sebagai sumber isi yang tersedia, tanpa menyatakan keduanya sudah menjadi dokumen kanonis yang disetujui.
- Hubungan di bawah adalah interpretasi awal dari deskripsi, bukan persetujuan atau traceability formal. Cakupan fitur, prioritas dan hubungan perlu dikonfirmasi. Tidak ada file Filio yang diubah.

## Usulan hubungan untuk review

| BR di BRD | Kebutuhan ringkas | Kandidat di PRD | Dasar dan hal yang perlu dikonfirmasi |
| --- | --- | --- | --- |
| BR-01 | Keluarga mulai dengan aman dan cepat | F-A01, F-A02, F-A04 | Akun/family, login, notice dan tidak ada akun anak mendukung onboarding aman. Ukuran cepat dan bukti onboarding belum dibuktikan. |
| BR-02 | Jurnal nyaman tanpa rasa bersalah | F-C01–F-C04 | Pencatatan, tagging, timeline dan refleksi opsional mendukung jurnal; aspek kenyamanan dan bebas rasa bersalah perlu penilaian UX, bukan diasumsikan lulus. |
| BR-03 | Delapan fitrah sebagai klasifikasi interpretatif | F-D01–F-D04 | Penjelasan kategori, hitungan dan copy keterbatasan mendukung penggunaan yang bukan skor klinis. Uji pemahaman belum dibuktikan. |
| BR-04 | Orang tua mendapat ide tindakan berikutnya | F-E01–F-E03, F-E05 | Katalog, filter, aktivitas dan rencana lanjutan adalah kandidat; F-E05 V1.1, sehingga cakupan per rilis perlu dikonfirmasi. |
| BR-05 | Pengalaman pengasuhan dapat direfleksikan | F-C04, F-E04–F-E05 | Refleksi opsional, prompt mingguan dan rencana mendukung kebutuhan ini; tahap rilis berbeda. |
| BR-06 | Data keluarga terisolasi dan dapat dikelola | F-A03, F-A05, F-B02 | Otorisasi keluarga, ekspor/penghapusan dan pengelolaan profil mendukung sebagian kebutuhan. Cakupan semua data dan bukti security test perlu ditinjau. |
| BR-07 | Keluarga bekerja sama secara aman | F-A06 | Undangan caregiver, role dan pencabutan akses direncanakan V1.1; belum menjadi bukti fitur tersedia. |
| BR-08 | Komunitas mendukung kurasi tanpa akses jurnal pribadi | F-F01 | Kurator mempublikasikan aktivitas tanpa akses data privat; PRD menempatkannya pasca-MVP. |
| BR-09 | Menguji willingness-to-pay tanpa menjual data anak | Tidak ada ID fitur spesifik ditemukan | Tabel ruang lingkup PRD menyebut eksperimen WTP pada V1.1 (baris 59) dan pertanyaan terbuka freemium (baris 303). Perlu keputusan apakah eksperimen atau kriteria privasi memerlukan requirement ber-ID. |
| BR-10 | Platform mudah dipelihara dan dipantau | Tidak ada ID fitur spesifik ditemukan | NFR reliability dan deployment tercantum pada baris 230–233; perlu pemilik menentukan ID/traceability dan bukti verifikasi yang sesuai. |

## Temuan untuk ditindaklanjuti

1. Setiap hubungan BR–fitur di atas masih memerlukan konfirmasi; PRD hanya menyebut BRD pada tingkat dokumen. Hubungan yang tampak relevan belum tentu lengkap atau cukup memenuhi kebutuhan bisnis.
2. BRD berisi `BR-01` sampai `BR-10`; PRD menggunakan ID `F-A01` dan seterusnya. Pertahankan format dan ID lama sesuai keputusan pemilik. Jangan otomatis mengganti ID atau menambahkan hubungan ke dokumen sumber.
3. BR-09 dan BR-10 memiliki pembahasan di PRD, tetapi belum ditemukan ID requirement spesifik untuk pengujian WTP atau pemeliharaan/observability. Ini adalah gap traceability untuk dikonfirmasi, bukan bukti fitur tidak ada.
4. PRD menggunakan prioritas seperti `P0`, `P1` dan `V1.1`, sementara template baru menggunakan nilai berbeda. Jangan otomatis mengubah prioritas atau menyamakan maknanya tanpa keputusan pemilik.
5. Validator baru dapat dikonfigurasi untuk pola ID lama, tetapi PRD asli masih gagal terhadap struktur dan tabel kontrak baru. Validator tidak memeriksa hubungan BRD–PRD lintas file; hasil review ini bersifat manual.

## Keputusan berikutnya

Pemilik produk perlu meninjau usulan baris demi baris, terutama BR-09/BR-10 dan perbedaan rilis. Setelah itu, tentukan lokasi dan format rekaman traceability, serta cara mengadaptasi dokumen draft ke standar baru tanpa mengganti ID atau menimpa sumber. Setiap perubahan substantif terhadap dokumen proyek dilakukan melalui review yang sesuai.
