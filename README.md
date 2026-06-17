# 🔐 Konstruksi S-Box pada GF(2⁸) dengan Genetic Algorithm

> **Project Kriptografi Lanjut** — Konstruksi dan Evaluasi S-box menggunakan pendekatan Genetic Algorithm (GA) pada Galois Field GF(2⁸).

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Deskripsi

S-box (*Substitution Box*) adalah komponen nonlinear paling krusial dalam sandi blok modern (AES, DES, dll). Project ini mengkonstruksi S-box berkualitas kriptografi menggunakan **Genetic Algorithm (GA)** pada **GF(2⁸)** dengan polinomial irreducibel `0x11B`.

S-box yang dihasilkan dievaluasi dengan **6 parameter kriptografi standar**:

| Parameter | Keterangan | Nilai Ideal |
|-----------|-----------|-------------|
| **NL** | Nonlinearity | ≥ 112 (AES) |
| **SAC** | Strict Avalanche Criterion | = 0.5 |
| **BIC-NL** | Bit Independence Criterion - NL | ≥ 100 |
| **BIC-SAC** | Bit Independence Criterion - SAC | ≈ 0.5 |
| **LAP** | Linear Approximation Probability | rendah |
| **DAP** | Differential Approximation Probability | rendah |

---

## 🧬 Metode: Genetic Algorithm

### Representasi
Setiap **kromosom** = permutasi dari `{0, 1, ..., 255}` (S-box valid secara bijektif).

### Alur GA
```
Inisialisasi Populasi
        ↓
Evaluasi Fitness (6 parameter kriptografi)
        ↓
Seleksi Turnamen
        ↓
Crossover PMX (Partially Mapped Crossover)
        ↓
Mutasi Swap (tukar n pasang elemen)
        ↓
Elitisme (2 terbaik lanjut)
        ↓
[Ulangi hingga konvergen]
        ↓
S-box Terbaik → Evaluasi Final
```

### Fungsi Fitness
```python
fitness = (NL/112)×30 + (1-|SAC-0.5|×2)×20 + (BIC_NL/112)×20 
        + (1-|BIC_SAC-0.5|×2)×15 + (1-LAP)×10 + (1-DAP)×5
```

---

## 📁 Struktur Project

```
sbox-ga-gf28/
│
├── sbox_ga.py          # Core: implementasi GA + semua fungsi evaluasi
├── app.py              # Streamlit app (UI interaktif)
├── generate_report.py  # Generator laporan PDF
├── best_sbox.json      # Hasil S-box terbaik (output)
├── requirements.txt    # Dependensi Python
└── README.md           # Dokumentasi ini
```

---

## 🚀 Instalasi & Cara Pakai

### 1. Clone Repository
```bash
git clone https://github.com/username/sbox-ga-gf28.git
cd sbox-ga-gf28
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Jalankan GA (Command Line)
```bash
python sbox_ga.py
```

Output:
```
S-Box Construction via Genetic Algorithm on GF(2^8)
Inisialisasi populasi (20 individu)...
  Generasi   1/50 | Best Fitness: 94.21 | Global Best: 94.21
  ...
  Generasi  50/50 | Best Fitness: 95.48 | Global Best: 95.48

--- S-Box Terbaik (16x16) ---
  ...

--- Evaluasi 6 Parameter ---
  NL      : 104
  SAC     : 0.5007
  BIC_NL  : 104.57
  BIC_SAC : 0.4998
  LAP     : 0.1172
  DAP     : 0.0312
```

### 4. Jalankan Streamlit App
```bash
streamlit run app.py
```
Buka browser di `http://localhost:8501`

### 5. Generate Laporan PDF
```bash
python generate_report.py
```

---

## 📊 Hasil Eksperimen

### Konfigurasi GA
| Parameter | Nilai |
|-----------|-------|
| Ukuran Populasi | 20 kromosom |
| Jumlah Generasi | 50 |
| Probabilitas Mutasi | 0.35 |
| Jumlah Swap Mutasi | 4 pasang |
| Ukuran Turnamen | 4 individu |
| Crossover | PMX (Partially Mapped Crossover) |
| Elitisme | 2 individu terbaik |
| Random Seed | 42 |

### Hasil Evaluasi

| Parameter | Hasil GA | Nilai AES | Ideal |
|-----------|----------|-----------|-------|
| NL | **104** | 112 | 112 |
| SAC | **0.5007** | 0.5039 | 0.5000 |
| BIC-NL | **104.57** | 112.00 | ≥ 100 |
| BIC-SAC | **0.4998** | 0.5013 | 0.5000 |
| LAP | **0.1172** | 0.0625 | rendah |
| DAP | **0.0312** | 0.0156 | rendah |

> ✅ **NL, SAC, BIC-NL, BIC-SAC** sudah mencapai kualitas baik.  
> ⚠️ **LAP dan DAP** masih dapat ditingkatkan dengan populasi/generasi lebih besar.

---

## 🖥️ Fitur Streamlit App

- ⚙️ **Konfigurasi GA** via slider sidebar (populasi, generasi, mutasi, dll.)
- 📈 **Grafik konvergensi fitness** real-time selama GA berjalan
- 📊 **Evaluasi 6 parameter** dengan indikator ✅/⚠️
- 🗃️ **Tabel S-box** heksadesimal 16×16 interaktif
- 🔍 **Lookup S-box** interaktif (desimal/hex)
- 💾 **Export** ke JSON, CSV, Python array

---

## 📚 Landasan Teori

### GF(2⁸)
Field berhingga dengan 256 elemen. Penjumlahan = XOR, perkalian = modulo polinomial irreducibel `x⁸ + x⁴ + x³ + x + 1`.

### Nonlinearity (NL)
Dihitung via Walsh-Hadamard Transform:
```
NL(f) = (256 - max|W_f(a)|) / 2
```
dimana `W_f` adalah Walsh transform dari fungsi Boolean `f`.

### SAC (Strict Avalanche Criterion)
```
SAC = (1 / 256·8·8) · Σ_x Σ_b HW(S(x) XOR S(x XOR e_b))
```
dimana `e_b` adalah vektor basis dengan 1 di posisi `b`, dan `HW` adalah Hamming Weight.

---

## 📦 Requirements

```
numpy>=1.21.0
streamlit>=1.20.0
pandas>=1.3.0
reportlab>=3.6.0
```

Install semua:
```bash
pip install -r requirements.txt
```

---

## 🔮 Pengembangan Selanjutnya

- [ ] Hybrid GA + Local Search untuk refinement
- [ ] Multi-objective optimization (Pareto front)  
- [ ] Perbandingan dengan Chaotic Map dan PSO
- [ ] Paralelisasi evaluasi fitness
- [ ] Populasi lebih besar (100+) dan generasi lebih banyak (500+)
- [ ] Deploy Streamlit ke Streamlit Cloud

---

## 📖 Referensi

1. Daemen, J., & Rijmen, V. (2002). *The Design of Rijndael: AES*. Springer.
2. Webster, A. F., & Tavares, S. E. (1986). On the Design of S-Boxes. *CRYPTO '85*.
3. Adams, C., & Tavares, S. (1990). The Structured Design of Cryptographically Good S-Boxes. *Journal of Cryptology*, 3(1), 27-41.
4. Millan, W. (1998). How to Improve the Nonlinearity of Bijective Boolean Functions. *ACISP 1998*.
5. Burnett, L. et al. (2004). Simpler Methods for Generating Better Boolean Functions. *AJC*.

---

## 📄 Lisensi

MIT License — bebas digunakan untuk keperluan akademik.

---

*Project ini dibuat untuk memenuhi tugas Project Mata Kuliah Kriptografi Lanjut.*
