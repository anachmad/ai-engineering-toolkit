# Impact Assessment: Engineering Standards Enforcement Framework

Status: draft
Decision: proposed; belum disetujui untuk implementasi
Tanggal: 2026-11-03
Dasar: change request pengguna, [spesifikasi arsitektur](../../specifications/AI_Engineering_Toolkit_Architecture_Integration_Spec_v1.md), [Phase 1 sign-off](../reviews/phase-1-acceptance-recheck.md), [Phase 2 sign-off](../reviews/phase-2-signoff.md), dan working tree saat assessment.

## Ringkasan

Arah yang diusulkan dapat dibangun secara bertahap di atas standar dan scaffold yang ada. Kebutuhan baru yang paling besar adalah kontrak artefak yang dapat divalidasi, pemeriksaan struktur dan traceability, serta penghubung hasil validasi ke quality gate dan CI. Semantic review oleh AI, hasil pemeriksaan deterministik, dan persetujuan manusia harus tetap menjadi bukti yang berbeda.

**Belum siap diimplementasikan sebagai standar final:** daftar 18 bagian BRD yang disebut sudah disepakati belum ditemukan di repository. Kerangka PRD, SRS/SRD, SAD dan dokumen lain juga memerlukan persetujuan terpisah sesuai change request. Assessment ini tidak menetapkan isi atau mengklaim persetujuan tersebut.

Phase 2 telah ditandatangani dengan batasan, tetapi seluruh implementasi Phase 2 dan dokumen sign-off masih **belum di-commit** pada saat assessment. Baseline Git terakhir adalah `11ed547` (Phase 1). Sebelum perubahan arsitektur, review dan tetapkan baseline Phase 2 agar kompatibilitas dapat diukur terhadap versi yang jelas.

## Kondisi saat ini

- `standards/profiles.yaml`, `standards/documentation-standard.md`, dan `standards/quality-gates.yaml` mendefinisikan profil `lean`, `standard`, dan `business-critical`, artefak, serta deskripsi gate. Profil Lite/Standard/Critical dalam change request **belum** menjadi nama konfigurasi yang disetujui.
- `standards/document-prompts.yaml` bersama `templates/project/document.md` menghasilkan dokumen draft dengan prompt per artefak. Ini belum merupakan registry template resmi per jenis dokumen atau jaminan bahwa setiap dokumen memiliki struktur yang telah disetujui.
- `playbook/__main__.py` memiliki validasi struktur konfigurasi/manifest dan pemeriksaan keberadaan artefak. `audit` tidak memvalidasi heading dokumen, metadata seluruh artefak, ID duplikat, referensi rusak, makna requirement, atau persetujuan.
- `orchestration/core.py` membaca konfigurasi routing dan mengevaluasi gate keamanan S1–S5 dari evidence yang diberikan. Hasil dapat `BLOCKED` atau `REVIEW_REQUIRED`; evidence dan identitas bersifat self-attested. Output menyatakan bahwa gate profil kanonis belum ditegakkan oleh evaluator dan tidak mengotorisasi release.
- Dua adapter host mengarah ke skill dan standar bersama. Uji host sebelumnya bersifat skenario terbatas; integrasi eksternal belum dipin, diinstal, atau diverifikasi oleh toolkit.
- Kondisi verifikasi lokal saat assessment: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` — **56 tests passed** pada Linux/Python 3.14.4. Hasil ini bukan bukti bahwa acceptance criteria baru telah terpenuhi.

## Gap analysis dan dampak

| Requirement | Reuse yang tersedia | Gap / dampak |
| --- | --- | --- |
| AR-001 Standards Registry | Standar dan konfigurasi versioned di `standards/` | Belum ada kontrak eksplisit per jenis artefak yang menghubungkan versi standar, metadata wajib, template, dan aturan validasi. Orchestration policy juga belum memiliki entry top-level dalam `standards/schemas/policies-v1.json`, sebagaimana temuan independent review. |
| AR-002 Template Registry | Template Markdown dan prompt berdasarkan path | Belum ada registry template per jenis/versi, struktur yang disetujui, atau kontrol bahwa dokumen berasal dari versi template tertentu. Hindari menyalin aturan ke template dan validator secara terpisah. |
| AR-003 Validation Engine | Validasi manifest/policy; audit keberadaan; skill audit/refresh | Belum ada engine dokumen deterministik. Semantic review dan human approval saat ini berupa instruksi/rekaman, bukan mekanisme verifikasi yang independen. Perlu status terpisah dan batas kewenangan yang jelas. |
| AR-004 Traceability | Konvensi ID dalam dokumentasi; prompt traceability | Belum ada model relasi yang dapat diparse, uniqueness check, pemeriksaan referensi, atau hubungan requirement → implementasi → test → evidence. Format ID Filio yang sudah ada juga harus direkonsiliasi tanpa penggantian diam-diam. |
| AR-005 Quality Gates | Profil gate dan evaluator keamanan S1–S5 | Gate profil saat ini deskriptif, bukan enforcement; status evaluator keamanan berbeda dari PASS/WARN/FAIL yang diusulkan. Perlu agregasi yang tidak mengubah NOT_RUN menjadi PASS dan tidak mengesampingkan bukti atau approval yang belum ada. |
| AR-006 Pluggable Skills | Registry, status ketersediaan dan routing | Pertahankan pemisahan capability dari standar wajib; belum ada bukti bahwa external skill dapat menegakkan validator baru. Tidak perlu menginstal atau menyalin toolkit eksternal untuk mulai membuat validator. |
| AR-007 Enforcement Profiles | `lean`, `standard`, `business-critical` dan risk floors | `Lite`, `Standard`, `Critical` memerlukan keputusan alias atau migrasi. Mengganti nama sekarang akan merusak manifest dan integrasi existing. Nama profil yang disimpan tetap tidak berubah sampai ada keputusan dan rencana kompatibilitas. |
| AR-008 CI/CD Integration | CLI lokal non-interaktif dan exit code pada beberapa operasi | Belum ada command validasi artefak yang cocok untuk pipeline, output hasil yang stabil, atau enforcement CI yang diuji. Spesifikasi asli menunjuk GitLab; kemampuan instalasi GitLab aktual belum diverifikasi. |
| AR-009 Change Management | Status dokumen, review MR, `provenance.json` snapshot hash | Belum ada alur standar untuk membandingkan versi requirement/standar, impact assessment terstruktur, dan approval berdasarkan risiko. Hash snapshot bukan bukti approval atau asal Git yang terverifikasi. |
| AR-010 Cross-Agent Portability | Shared skill dan thin adapters; uji host lokal | Belum ada uji kompatibilitas Codex/Claude Code untuk validator dan evidence model baru. Kebijakan harus tetap terpusat; adapter tidak boleh menyalin aturan. |

## Keputusan yang perlu diselesaikan

1. **18 bagian BRD:** tentukan dokumen sumber, judul/urutan resmi, metadata, variasi yang diperbolehkan, versi, dan pemberi approval. Jangan mengisi daftar berdasarkan tebakan atau BRD Filio.
2. **Profil:** apakah `Lite` dan `Critical` adalah nama tampilan/alias bagi `lean` dan `business-critical`, atau diperlukan migrasi? Rekomendasi: pertahankan identifier tersimpan dan bahas alias secara eksplisit; jangan ubah otomatis.
3. **Terminologi:** apakah `SRS` identik dengan `SRD` yang sudah digunakan? Tentukan pemilik dan hubungan dokumen sebelum membuat template baru.
4. **Kontrak dokumen:** setujui front matter/metadata, bahasa heading, penanganan dokumen linked, fenced code, subheading, status draft, dan stable ID lintas dokumen. Tentukan kapan ID harus unik: per dokumen, per proyek, atau per namespace.
5. **Approval dan evidence:** tentukan sumber identitas/approval yang dapat dipercaya, reviewer berwenang, masa berlaku, dan kebijakan waiver. File atau string yang mengaku disetujui bukan bukti independen; semantic review AI bukan human approval.
6. **CI target dan pengecualian:** tetapkan platform/pipeline pertama, perlakuan `WARN`, aturan mandatory per profil, dan mekanisme enforcement yang benar-benar tersedia. Tidak mengasumsikan kemampuan GitLab Free atau mengubah branch protection.
7. **Penggunaan materi referensi:** tentukan jenis, lisensi, sensitivitas, lokasi, dan otoritas sumber; dokumen pendukung tidak otomatis menjadi requirement yang disetujui.

## Arsitektur usulan: reuse first

1. Tambahkan **artifact contract registry** versioned sebagai konfigurasi kanonis yang menunjuk ke template Markdown dan aturan struktural per jenis artefak. Mulai dari artefak yang struktur dan pemiliknya sudah disetujui. Gunakan schema/validator Phase 1 untuk kontrak konfigurasi sejauh cocok; hindari membuat definisi standar kedua di adapter host.
2. Buat satu modul validasi dengan interface CLI non-interaktif yang menerima project root, manifest, dan versi registry, lalu menghasilkan hasil terstruktur: rule ID, lokasi, severity, status, dan evidence. Pisahkan validator struktur dan relasi dari semantic review dan pemeriksaan approval. Gunakan Python standard library bila format dan kebutuhan memungkinkan.
3. Tetapkan satu model sumber untuk ID dan relasi yang dapat di-audit. Pemeriksaan awal harus mendeteksi duplikat dan target referensi hilang tanpa menganggap setiap teks mirip ID sebagai requirement; kode dalam fenced blocks, external links, dan linked documents perlu aturan yang eksplisit dan diuji.
4. Definisikan adapter agregasi ke `PASS`/`WARN`/`FAIL` tanpa menghapus outcome keamanan yang sudah ada (`NOT_RUN`, `NOT_APPLICABLE`, `WAIVED`, `REVIEW_REQUIRED`). Ketiadaan mandatory evidence atau approval harus terlihat dan memblokir sesuai policy yang disetujui; keputusan release tetap pada CI dan manusia berwenang.
5. Gunakan CLI dan report yang sama dari Codex, Claude Code, dan CI. Skill eksternal dapat memberi evidence atau melakukan semantic review, tetapi tidak dapat mengubah aturan mandatory atau menyatakan approval manusia.

## Rencana implementasi bertahap

### M0 — Persetujuan dan baseline

- Review perubahan Phase 2 yang belum di-commit dan tetapkan baseline; selesaikan atau terima temuan schema orchestration secara eksplisit.
- Dapatkan sumber 18 bagian BRD, keputusan profil dan terminologi, serta tetapkan pemilik standar dan approver.
- **Exit:** input standar BRD dan scope fase disetujui; standar lain tetap draft sampai approval masing-masing.

### M1 — Kontrak dan validasi deterministik

- Definisikan registry dan schema versioned untuk artefak, template, dan rule yang telah disetujui; tentukan compatibility dan kebijakan perubahan versi.
- Implementasikan validasi metadata dan struktur Markdown untuk BRD menggunakan daftar 18 bagian yang disetujui. Pertahankan dokumen existing; mulai dengan audit/report, tanpa rewrite otomatis.
- **Exit:** contoh valid/invalid dapat direproduksi; heading salah/hilang, metadata hilang, versi tidak didukung, dan konflik existing dilaporkan dengan lokasi dan exit code; dokumen disetujui tidak diubah.

### M2 — Traceability dan lifecycle evidence

- Definisikan registry ID/referensi dan implementasikan pemeriksaan duplikat serta referensi hilang, termasuk kasus dokumen linked dan fixture aman.
- Rekam hasil deterministik, semantic review, dan approval manusia sebagai jenis evidence berbeda; tampilkan unknown/not-run sebagai belum terpenuhi, bukan sukses.
- **Exit:** fixture dengan ID duplikat, broken reference, evidence hilang dan approval belum terverifikasi menghasilkan diagnosis yang tepat; perubahan requirement menghasilkan daftar dampak untuk review.

### M3 — Gate dan CI yang disetujui

- Agregasikan hasil ke PASS/WARN/FAIL sambil mempertahankan status rinci; tentukan mapping untuk missing evidence, WAIVED dan NOT_APPLICABLE berdasarkan policy yang disetujui.
- Sediakan CLI yang stabil dan non-interaktif; tambahkan contoh pipeline hanya untuk platform yang telah dipilih dan diuji. Tidak mengubah production, branch protection, atau secret.
- **Exit:** pipeline test fixture memblokir mandatory failure; warning sesuai policy; semantic review AI tidak dapat menggantikan approval; audit output dapat ditelusuri ke evidence.

### M4 — Cross-agent acceptance dan keputusan sign-off

- Jalankan end-to-end valid dan invalid di Codex dan Claude Code terhadap standar yang sama dan proyek sementara. Rekam versi host, command, output, serta apa yang tidak diuji.
- Tambahkan regression tests untuk perubahan standar/template/validator dan review kompatibilitas proyek Phase 1/2 serta proyek yang memiliki dokumen existing.
- **Exit:** acceptance criteria untuk standar yang sudah disetujui memiliki bukti; pemilik menyetujui hasil dan residual risk sebelum sign-off. Struktur PRD/SRS/SAD yang belum disetujui tetap tidak dinyatakan selesai.

## Risiko dan strategi kompatibilitas

- **False confidence:** heading yang valid bukan bukti bahwa requirement benar, lengkap, aman, atau disetujui. Output harus memisahkan temuan deterministik, semantic review, dan approval.
- **Konten existing:** aturan baru bisa menandai dokumen lama noncompliant. Awali dengan report-only dan patch untuk review; jangan overwrite atau otomatis menyatakan dokumen tidak berlaku.
- **Perubahan format dan versi:** pertahankan identifier profil, manifest v1, command Phase 1/2, dan outcome S1–S5. Tambahan schema harus versioned; perubahan inkompatibel memerlukan rencana migrasi yang disetujui, bukan perubahan diam-diam.
- **Sumber standar ganda:** registry menjadi rujukan struktur tunggal; template, validator, host, dan CI mengonsumsinya. Kebijakan engineering mandatory tetap terpisah dari registrasi external skill.
- **Dokumen berisi data sensitif:** fixture harus disanitasi; output CI tidak boleh menyalin secret atau data project yang tidak perlu. Pembacaan filesystem mengikuti threat model Phase 1 yang sudah diterima sampai ada keputusan baru.
- **Batas fase:** Toolkit Manager, instalasi third-party dan deployment production tidak diperlukan untuk membuktikan validator. Integrasi CI yang diusulkan bergantung pada persetujuan platform dan pengujian di lingkungan nyata.

## Rekomendasi keputusan

Setujui assessment dan mulai dengan M0. Setelah daftar 18 bagian BRD, pilihan profil, dan lingkup approval tersedia, minta persetujuan untuk kontrak artefak dan rencana implementasi. Jangan nyatakan change request selesai sampai acceptance end-to-end untuk scope yang disetujui lulus dan bukti approval tersedia.
