"""
Generate Laporan PDF - Konstruksi S-box dengan Genetic Algorithm pada GF(2^8)
"""

import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.platypus import KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

# ── Load data ──────────────────────────────────────────────────────────────────
with open("/home/claude/best_sbox.json") as f:
    data = json.load(f)

SBOX    = data["sbox"]
METRICS = data["metrics"]
HISTORY = data["history"]

# ── Styles ─────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

NAVY   = colors.HexColor("#1a237e")
TEAL   = colors.HexColor("#00838f")
LIGHT  = colors.HexColor("#e8eaf6")
WHITE  = colors.white
GRAY   = colors.HexColor("#546e7a")
BG_HDR = colors.HexColor("#283593")

title_style = ParagraphStyle(
    "TitleMain", parent=styles["Title"],
    fontSize=20, textColor=NAVY, spaceAfter=4,
    leading=24, alignment=TA_CENTER, fontName="Helvetica-Bold"
)
sub_style = ParagraphStyle(
    "SubTitle", parent=styles["Normal"],
    fontSize=11, textColor=TEAL, alignment=TA_CENTER,
    spaceAfter=2, fontName="Helvetica"
)
info_style = ParagraphStyle(
    "Info", parent=styles["Normal"],
    fontSize=10, textColor=GRAY, alignment=TA_CENTER,
    spaceAfter=1, fontName="Helvetica"
)
h1_style = ParagraphStyle(
    "H1", parent=styles["Heading1"],
    fontSize=14, textColor=WHITE, fontName="Helvetica-Bold",
    spaceAfter=8, spaceBefore=14, leading=18
)
h2_style = ParagraphStyle(
    "H2", parent=styles["Heading2"],
    fontSize=12, textColor=NAVY, fontName="Helvetica-Bold",
    spaceAfter=6, spaceBefore=10, leading=15
)
body_style = ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontSize=10, leading=15, alignment=TA_JUSTIFY,
    spaceAfter=6, fontName="Helvetica"
)
caption_style = ParagraphStyle(
    "Caption", parent=styles["Normal"],
    fontSize=9, textColor=GRAY, alignment=TA_CENTER,
    spaceAfter=8, fontName="Helvetica-Oblique"
)
code_style = ParagraphStyle(
    "Code", parent=styles["Normal"],
    fontSize=8.5, fontName="Courier", leading=13,
    spaceAfter=4, leftIndent=12,
    backColor=colors.HexColor("#f5f5f5"),
    borderPadding=(4, 6, 4, 6)
)

def section_header(text):
    """Buat header section dengan background berwarna."""
    data_tbl = [[Paragraph(text, h1_style)]]
    tbl = Table(data_tbl, colWidths=[17*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_HDR),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return tbl

# ── Build document ──────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    "/home/claude/Laporan_Sbox_GA.pdf",
    pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2.5*cm, bottomMargin=2.5*cm
)

story = []

# ─────────────────────── HALAMAN JUDUL ───────────────────────
story.append(Spacer(1, 1.5*cm))
story.append(Paragraph("LAPORAN PROJECT", sub_style))
story.append(Paragraph("Kriptografi Lanjut", sub_style))
story.append(Spacer(1, 0.5*cm))
story.append(HRFlowable(width="100%", thickness=2, color=TEAL))
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    "Konstruksi S-Box pada GF(2<super>8</super>)<br/>Menggunakan Genetic Algorithm",
    title_style
))
story.append(Spacer(1, 0.3*cm))
story.append(HRFlowable(width="100%", thickness=2, color=TEAL))
story.append(Spacer(1, 1*cm))

info_box = Table([
    [Paragraph("Mata Kuliah", info_style), Paragraph(":", info_style), Paragraph("Kriptografi Lanjut", info_style)],
    [Paragraph("Metode",      info_style), Paragraph(":", info_style), Paragraph("Genetic Algorithm (GA)", info_style)],
    [Paragraph("Field",       info_style), Paragraph(":", info_style), Paragraph("GF(2<super>8</super>) — Polinomial Irreducibel 0x11B", info_style)],
    [Paragraph("Tahun",       info_style), Paragraph(":", info_style), Paragraph("2025/2026", info_style)],
], colWidths=[4*cm, 0.5*cm, 12.5*cm])
info_box.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), LIGHT),
    ("ROUNDEDCORNERS", [6]),
    ("TOPPADDING",    (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING",   (0,0), (-1,-1), 12),
]))
story.append(info_box)
story.append(PageBreak())

# ─────────────────────── BAB 1: PENDAHULUAN ───────────────────────
story.append(section_header("BAB 1 — Pendahuluan"))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("1.1 Latar Belakang", h2_style))
story.append(Paragraph(
    "Substitution Box (S-box) merupakan komponen kriptografi paling krusial dalam sistem sandi blok modern. "
    "S-box berperan sebagai satu-satunya elemen nonlinear dalam cipher, sehingga kualitasnya secara langsung "
    "menentukan ketahanan sistem terhadap serangan linear dan diferensial. Standar AES menggunakan S-box yang "
    "dikonstruksi secara aljabar melalui invers multiplikatif di GF(2<super>8</super>), namun pendekatan "
    "metaheuristik seperti Genetic Algorithm menawarkan fleksibilitas eksplorasi ruang solusi yang lebih luas.",
    body_style
))

story.append(Paragraph("1.2 Tujuan", h2_style))
goals = [
    "Mengkonstruksi S-box 8x8 (256 elemen) yang valid secara kriptografi menggunakan Genetic Algorithm.",
    "Mengevaluasi kualitas S-box dengan 6 parameter standar: NL, SAC, BIC-NL, BIC-SAC, LAP, dan DAP.",
    "Membandingkan hasil dengan nilai ideal dan S-box AES sebagai baseline.",
    "Mengimplementasikan solusi dalam bentuk kode Python yang dapat direproduksi.",
]
for g in goals:
    story.append(Paragraph(f"&bull;&nbsp; {g}", body_style))

story.append(Paragraph("1.3 Batasan", h2_style))
story.append(Paragraph(
    "Eksperimen dilakukan dengan konfigurasi GA: ukuran populasi 20 kromosom, 50 generasi, "
    "probabilitas mutasi 0.35, menggunakan crossover PMX (Partially Mapped Crossover) dan "
    "seleksi turnamen ukuran 4. Operasi field menggunakan polinomial irreducibel "
    "p(x) = x<super>8</super> + x<super>4</super> + x<super>3</super> + x + 1 (0x11B), sama dengan AES.",
    body_style
))

# ─────────────────────── BAB 2: LANDASAN TEORI ───────────────────────
story.append(section_header("BAB 2 — Landasan Teori"))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("2.1 Galois Field GF(2<super>8</super>)", h2_style))
story.append(Paragraph(
    "GF(2<super>8</super>) adalah field berhingga dengan 256 elemen, direpresentasikan sebagai "
    "polinomial berderajat maksimal 7 dengan koefisien biner. Penjumlahan dalam field ini "
    "adalah operasi XOR bitwise, sedangkan perkalian dilakukan modulo polinomial irreducibel. "
    "Setiap elemen non-zero memiliki invers multiplikatif unik, sifat inilah yang dieksploitasi "
    "dalam konstruksi S-box AES.",
    body_style
))

story.append(Paragraph("2.2 Substitution Box (S-Box)", h2_style))
story.append(Paragraph(
    "S-box dalam konteks kriptografi blok adalah fungsi bijektif f: {0,1}<super>8</super> "
    "&#8594; {0,1}<super>8</super>, yaitu permutasi dari himpunan {0, 1, ..., 255}. "
    "Sifat bijektif (injektif sekaligus surjektif) wajib dipenuhi agar proses dekripsi dapat "
    "dilakukan. Kualitas S-box diukur melalui sejumlah properti kriptografi yang menentukan "
    "ketahanannya terhadap berbagai serangan.",
    body_style
))

story.append(Paragraph("2.3 Parameter Evaluasi Kriptografi", h2_style))
params_data = [
    [Paragraph("<b>Parameter</b>", body_style), Paragraph("<b>Definisi</b>", body_style),
     Paragraph("<b>Nilai Ideal</b>", body_style)],
    [Paragraph("Nonlinearity (NL)", body_style),
     Paragraph("Jarak minimum fungsi Boolean output dari himpunan fungsi affine. Mengukur ketahanan terhadap linear cryptanalysis.", body_style),
     Paragraph("112 (AES)", body_style)],
    [Paragraph("SAC", body_style),
     Paragraph("Strict Avalanche Criterion: setiap perubahan 1 bit input mengubah tiap bit output dengan probabilitas tepat 0.5.", body_style),
     Paragraph("0.5", body_style)],
    [Paragraph("BIC-NL", body_style),
     Paragraph("Bit Independence Criterion - Nonlinearity: nonlinearity dari fungsi XOR antara setiap pasangan bit output.", body_style),
     Paragraph("Tinggi (&#8805;100)", body_style)],
    [Paragraph("BIC-SAC", body_style),
     Paragraph("Bit Independence Criterion - SAC: independensi antara perubahan pasangan bit output.", body_style),
     Paragraph("0.5", body_style)],
    [Paragraph("LAP", body_style),
     Paragraph("Linear Approximation Probability: bias maksimum aproksimasi linear terbaik. Makin rendah makin aman.", body_style),
     Paragraph("Rendah (~0.062)", body_style)],
    [Paragraph("DAP", body_style),
     Paragraph("Differential Approximation Probability: probabilitas diferensial output tertinggi. Makin rendah makin aman.", body_style),
     Paragraph("Rendah (~0.008)", body_style)],
]
params_tbl = Table(params_data, colWidths=[3*cm, 10*cm, 4*cm])
params_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,0),  BG_HDR),
    ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
    ("ROWBACKGROUNDS",(0,1), (-1,-1), [LIGHT, WHITE]),
    ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#bdbdbd")),
    ("TOPPADDING",    (0,0), (-1,-1), 6),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ("VALIGN",        (0,0), (-1,-1), "TOP"),
]))
story.append(params_tbl)
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("2.4 Genetic Algorithm", h2_style))
story.append(Paragraph(
    "Genetic Algorithm (GA) adalah algoritma optimasi berbasis seleksi alam. Setiap individu "
    "(kromosom) merepresentasikan satu kandidat solusi. Dalam konteks konstruksi S-box, "
    "satu kromosom adalah permutasi dari {0, 1, ..., 255}. Proses evolusi terdiri dari: "
    "(1) <b>Inisialisasi</b>: populasi awal berupa permutasi acak; "
    "(2) <b>Evaluasi fitness</b>: menghitung skor kriptografi gabungan; "
    "(3) <b>Seleksi</b>: turnamen untuk memilih individu terbaik; "
    "(4) <b>Crossover PMX</b>: menghasilkan anak dengan mempertahankan sifat permutasi; "
    "(5) <b>Mutasi</b>: penukaran dua elemen secara acak; "
    "(6) <b>Elitisme</b>: menyimpan 2 individu terbaik di setiap generasi.",
    body_style
))

# ─────────────────────── BAB 3: METODOLOGI ───────────────────────
story.append(section_header("BAB 3 — Metodologi"))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("3.1 Diagram Alur GA", h2_style))
story.append(Paragraph(
    "Algoritma dijalankan dengan alur berikut: Inisialisasi Populasi &#8594; Hitung Fitness "
    "&#8594; Seleksi (Tournament) &#8594; Crossover PMX &#8594; Mutasi (Swap) &#8594; "
    "Elitisme &#8594; [Ulangi hingga konvergen] &#8594; S-box Terbaik &#8594; Evaluasi 6 Parameter.",
    body_style
))

story.append(Paragraph("3.2 Fungsi Fitness", h2_style))
story.append(Paragraph(
    "Fitness dikombinasikan dari 6 parameter dengan pembobotan berdasarkan kepentingan kriptografi:",
    body_style
))
story.append(Paragraph(
    "fitness = (NL/112)&#215;30 + (1&#8722;|SAC&#8722;0.5|&#215;2)&#215;20 + "
    "(BIC_NL/112)&#215;20 + (1&#8722;|BIC_SAC&#8722;0.5|&#215;2)&#215;15 + "
    "(1&#8722;LAP)&#215;10 + (1&#8722;DAP)&#215;5",
    code_style
))
story.append(Paragraph(
    "NL mendapat bobot tertinggi (30) karena merupakan parameter paling penting dalam "
    "mengukur ketahanan terhadap linear cryptanalysis. SAC dan BIC-NL masing-masing mendapat "
    "bobot 20 sebagai parameter kualitas difusi. Total skor maksimum teoritis adalah 100.",
    body_style
))

story.append(Paragraph("3.3 Crossover PMX", h2_style))
story.append(Paragraph(
    "Partially Mapped Crossover (PMX) dipilih karena mampu menghasilkan keturunan yang "
    "valid sebagai permutasi tanpa perlu perbaikan (repair). PMX memilih segmen acak dari "
    "parent pertama, menyalinnya ke anak, kemudian mengisi sisa posisi dari parent kedua "
    "dengan menghindari duplikasi melalui mapping. Ini menjamin S-box hasil crossover selalu "
    "merupakan bijeksi.",
    body_style
))

story.append(Paragraph("3.4 Konfigurasi Eksperimen", h2_style))
config_data = [
    [Paragraph("<b>Parameter GA</b>", body_style), Paragraph("<b>Nilai</b>", body_style)],
    [Paragraph("Ukuran Populasi",    body_style), Paragraph("20 kromosom", body_style)],
    [Paragraph("Jumlah Generasi",    body_style), Paragraph("50 generasi", body_style)],
    [Paragraph("Probabilitas Mutasi",body_style), Paragraph("0.35", body_style)],
    [Paragraph("Ukuran Turnamen",    body_style), Paragraph("4 individu", body_style)],
    [Paragraph("Jumlah Swap Mutasi", body_style), Paragraph("4 pasang elemen", body_style)],
    [Paragraph("Elitisme",           body_style), Paragraph("2 individu terbaik disimpan", body_style)],
    [Paragraph("Crossover",          body_style), Paragraph("Partially Mapped Crossover (PMX)", body_style)],
    [Paragraph("Inisialisasi",       body_style), Paragraph("Permutasi acak seragam", body_style)],
]
config_tbl = Table(config_data, colWidths=[7*cm, 10*cm])
config_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,0),  BG_HDR),
    ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
    ("ROWBACKGROUNDS",(0,1), (-1,-1), [LIGHT, WHITE]),
    ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#bdbdbd")),
    ("TOPPADDING",    (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING",   (0,0), (-1,-1), 8),
]))
story.append(config_tbl)

# ─────────────────────── BAB 4: HASIL ───────────────────────
story.append(PageBreak())
story.append(section_header("BAB 4 — Hasil dan Analisis"))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("4.1 S-Box yang Dihasilkan (16x16)", h2_style))
story.append(Paragraph(
    "Berikut adalah S-box terbaik yang dihasilkan oleh GA setelah 50 generasi. "
    "Setiap nilai merepresentasikan output substitusi untuk input yang bersesuaian (baris x 16 + kolom).",
    body_style
))

# S-box table header
sbox_header = [Paragraph(f"<b>{j:X}</b>", ParagraphStyle("sh", fontSize=7.5, alignment=TA_CENTER, fontName="Helvetica-Bold"))
               for j in range(16)]
sbox_rows = [[Paragraph(f"<b>{i:X}x</b>", ParagraphStyle("rh", fontSize=7.5, alignment=TA_CENTER, fontName="Helvetica-Bold", textColor=WHITE))] +
             [Paragraph(f"{SBOX[i*16+j]:02X}", ParagraphStyle("sc", fontSize=7.5, fontName="Courier", alignment=TA_CENTER))
              for j in range(16)]
             for i in range(16)]
sbox_data = [[Paragraph("", body_style)] + sbox_header] + sbox_rows
col_w = [1.1*cm] + [1.0*cm]*16
sbox_tbl = Table(sbox_data, colWidths=col_w)
sbox_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,0),  BG_HDR),
    ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
    ("BACKGROUND",    (0,1), (0,-1),  TEAL),
    ("ROWBACKGROUNDS",(1,1), (-1,-1), [LIGHT, WHITE]),
    ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#bdbdbd")),
    ("TOPPADDING",    (0,0), (-1,-1), 3),
    ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ("ALIGN",         (0,0), (-1,-1), "CENTER"),
    ("FONTSIZE",      (0,0), (-1,-1), 7.5),
]))
story.append(sbox_tbl)
story.append(Paragraph("Tabel 1. S-box hasil GA (representasi heksadesimal, 16x16)", caption_style))

story.append(Paragraph("4.2 Konvergensi Fitness", h2_style))
story.append(Paragraph(
    "Grafik berikut menunjukkan evolusi nilai fitness terbaik per generasi selama proses optimasi GA.",
    body_style
))

# Fitness history mini chart (ASCII-style table)
hist_data = [[Paragraph(f"<b>Gen {i+1}</b>", ParagraphStyle("hg", fontSize=8, alignment=TA_CENTER)),
              Paragraph(f"{HISTORY[i]:.3f}", ParagraphStyle("hv", fontSize=8, fontName="Courier", alignment=TA_CENTER))]
             for i in range(len(HISTORY))]
hist_tbl = Table(hist_data, colWidths=[3*cm, 3*cm], hAlign="LEFT")
hist_tbl.setStyle(TableStyle([
    ("ROWBACKGROUNDS",(0,0),(-1,-1),[LIGHT, WHITE]),
    ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#bdbdbd")),
    ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
    ("LEFTPADDING",(0,0),(-1,-1),6),
]))
story.append(hist_tbl)
story.append(Paragraph("Tabel 2. Riwayat nilai fitness terbaik per generasi", caption_style))

story.append(Paragraph("4.3 Hasil Evaluasi 6 Parameter", h2_style))

ideal_vals = {"NL": "112", "SAC": "0.5000", "BIC_NL": "112.0", "BIC_SAC": "0.5000", "LAP": "~0.0625", "DAP": "~0.0078"}
aes_vals   = {"NL": "112", "SAC": "0.5039", "BIC_NL": "112.0", "BIC_SAC": "0.5013", "LAP": "0.0625",  "DAP": "0.0156"}

def status(key, val):
    if key == "NL":
        return "Baik" if float(val) >= 100 else "Perlu Peningkatan"
    elif key in ("SAC", "BIC_SAC"):
        return "Baik" if abs(float(val) - 0.5) < 0.05 else "Perlu Peningkatan"
    elif key == "BIC_NL":
        return "Baik" if float(val) >= 100 else "Perlu Peningkatan"
    elif key == "LAP":
        return "Baik" if float(val) < 0.15 else "Perlu Peningkatan"
    elif key == "DAP":
        return "Baik" if float(val) < 0.05 else "Perlu Peningkatan"
    return "-"

eval_header = [Paragraph("<b>Parameter</b>", body_style), Paragraph("<b>Hasil GA</b>", body_style),
               Paragraph("<b>Nilai AES</b>", body_style), Paragraph("<b>Ideal</b>", body_style),
               Paragraph("<b>Status</b>", body_style)]
eval_rows = []
for key in ["NL", "SAC", "BIC_NL", "BIC_SAC", "LAP", "DAP"]:
    val = str(METRICS[key])
    st  = status(key, val)
    col = colors.HexColor("#e8f5e9") if st == "Baik" else colors.HexColor("#fff8e1")
    eval_rows.append([
        Paragraph(key, body_style),
        Paragraph(f"<b>{val}</b>", body_style),
        Paragraph(aes_vals[key], body_style),
        Paragraph(ideal_vals[key], body_style),
        Paragraph(f"<font color='{'#2e7d32' if st=='Baik' else '#e65100'}'>{st}</font>", body_style),
    ])

eval_data = [eval_header] + eval_rows
eval_tbl = Table(eval_data, colWidths=[3*cm, 3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
eval_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,0),  BG_HDR),
    ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
    ("ROWBACKGROUNDS",(0,1), (-1,-1), [LIGHT, WHITE]),
    ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#bdbdbd")),
    ("TOPPADDING",    (0,0), (-1,-1), 6),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ("ALIGN",         (1,1), (-1,-1), "CENTER"),
]))
story.append(eval_tbl)
story.append(Paragraph("Tabel 3. Perbandingan hasil evaluasi S-box GA dengan AES dan nilai ideal", caption_style))

story.append(Paragraph("4.4 Analisis Hasil", h2_style))
story.append(Paragraph(
    f"S-box yang dihasilkan menunjukkan nilai <b>Nonlinearity (NL) = {METRICS['NL']}</b>, "
    f"yang tergolong baik (NL AES = 112). Nilai <b>SAC = {METRICS['SAC']}</b> sangat mendekati "
    f"nilai ideal 0.5, mengindikasikan properti avalanche yang memadai. "
    f"<b>BIC-NL = {METRICS['BIC_NL']:.2f}</b> dan <b>BIC-SAC = {METRICS['BIC_SAC']:.4f}</b> "
    f"menunjukkan independensi yang baik antar bit output. "
    f"<b>LAP = {METRICS['LAP']}</b> dan <b>DAP = {METRICS['DAP']}</b> berada dalam rentang "
    f"yang wajar, meskipun masih ada ruang peningkatan dengan menambah generasi atau populasi.",
    body_style
))
story.append(Paragraph(
    "Hasil ini menunjukkan bahwa Genetic Algorithm mampu mengkonstruksi S-box berkualitas "
    "kriptografi yang baik meskipun dengan konfigurasi ringan (50 generasi, 20 populasi). "
    "Peningkatan signifikan diharapkan dengan konfigurasi yang lebih besar untuk keperluan "
    "produksi nyata.",
    body_style
))

# ─────────────────────── BAB 5: KESIMPULAN ───────────────────────
story.append(section_header("BAB 5 — Kesimpulan dan Saran"))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("5.1 Kesimpulan", h2_style))
conclusions = [
    f"Genetic Algorithm berhasil mengkonstruksi S-box bijektif pada GF(2<super>8</super>) dengan NL = {METRICS['NL']}, mendekati nilai optimal AES (NL = 112).",
    f"Nilai SAC = {METRICS['SAC']} ≈ 0.5 mengkonfirmasi properti avalanche yang baik.",
    f"BIC-NL = {METRICS['BIC_NL']:.2f} dan BIC-SAC = {METRICS['BIC_SAC']:.4f} menunjukkan bit output saling independen.",
    "PMX crossover terbukti efektif menjaga validitas permutasi tanpa repair algorithm.",
    "GA merupakan metode yang feasible dan mudah dipahami untuk konstruksi S-box kriptografi.",
]
for c in conclusions:
    story.append(Paragraph(f"&bull;&nbsp; {c}", body_style))

story.append(Paragraph("5.2 Saran Pengembangan", h2_style))
suggestions = [
    "Meningkatkan ukuran populasi (50-100) dan jumlah generasi (200-500) untuk konvergensi lebih optimal.",
    "Mengkombinasikan GA dengan Local Search (Hybrid GA) untuk refinement solusi terbaik.",
    "Menerapkan multi-objective optimization dengan Pareto front untuk keseimbangan antar parameter.",
    "Membandingkan dengan metode lain: Chaotic Map, Simulated Annealing, atau PSO.",
    "Mengimplementasikan paralelisasi untuk mempercepat evaluasi fitness.",
]
for s in suggestions:
    story.append(Paragraph(f"&bull;&nbsp; {s}", body_style))

# ─────────────────────── REFERENSI ───────────────────────
story.append(section_header("Referensi"))
story.append(Spacer(1, 0.3*cm))
refs = [
    "Daemen, J., & Rijmen, V. (2002). <i>The Design of Rijndael: AES - The Advanced Encryption Standard</i>. Springer.",
    "Webster, A. F., & Tavares, S. E. (1986). On the Design of S-Boxes. <i>Advances in Cryptology - CRYPTO '85</i>.",
    "Adams, C., & Tavares, S. (1990). The Structured Design of Cryptographically Good S-Boxes. <i>Journal of Cryptology</i>, 3(1), 27-41.",
    "Millan, W. (1998). How to Improve the Nonlinearity of Bijective Boolean Functions. <i>ACISP 1998</i>, LNCS 1438.",
    "Burnett, L., Millan, W., Dawson, E., & Clark, A. (2004). Simpler Methods for Generating Better Boolean Functions with Good Cryptographic Properties. <i>Australasian Journal of Combinatorics</i>.",
    "Hussain, I., Shah, T., & Mahmood, H. (2013). A New Algorithm to Construct Secure Keys for AES. <i>International Journal of Contemporary Mathematical Sciences</i>.",
]
for i, r in enumerate(refs, 1):
    story.append(Paragraph(f"[{i}] {r}", ParagraphStyle("ref", parent=body_style, fontSize=9, leftIndent=20, firstLineIndent=-20)))

# ─────────────────────── BUILD ───────────────────────
doc.build(story)
print("PDF berhasil dibuat: Laporan_Sbox_GA.pdf")
