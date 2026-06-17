"""
Streamlit App: Konstruksi S-Box dengan Genetic Algorithm pada GF(2^8)
Kriptografi Lanjut Project

Jalankan: streamlit run app.py
"""

import streamlit as st
import numpy as np
import random
import time
import json
import pandas as pd

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="S-Box GA | Kriptografi Lanjut",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2rem; font-weight: 800; color: #1a237e;
        text-align: center; margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem; color: #00838f; text-align: center; margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #e8eaf6, #ffffff);
        border-left: 4px solid #283593;
        border-radius: 8px; padding: 12px 16px; margin: 6px 0;
    }
    .metric-good  { border-left-color: #2e7d32; background: linear-gradient(135deg, #e8f5e9, #fff); }
    .metric-warn  { border-left-color: #f57f17; background: linear-gradient(135deg, #fff8e1, #fff); }
    .sbox-cell { font-family: monospace; font-size: 0.75rem; text-align: center; }
    .stProgress > div > div { background-color: #283593; }
    .highlight { background-color: #e8eaf6; border-radius: 6px; padding: 8px 12px; }
</style>
""", unsafe_allow_html=True)

# ─── GF(2^8) & Evaluation Functions ─────────────────────────────────────────────
def gf_mul(a, b):
    p = 0
    for _ in range(8):
        if b & 1: p ^= a
        hi = a & 0x80; a = (a << 1) & 0xFF
        if hi: a ^= 0x1B
        b >>= 1
    return p

def wht(f):
    W = np.array([1 - 2 * int(b) for b in f], dtype=np.float64)
    step = 1
    while step < 256:
        for i in range(0, 256, step * 2):
            for j in range(i, i + step):
                u, v = W[j], W[j + step]; W[j] = u + v; W[j + step] = u - v
        step *= 2
    return W

def nl_func(f):
    return int((256 - np.max(np.abs(wht(f)))) // 2)

def compute_NL(s):
    return min(nl_func(np.array([(s[x] >> b) & 1 for x in range(256)])) for b in range(8))

def compute_SAC(s):
    t = sum(bin(s[x] ^ s[x ^ (1 << b)]).count('1')
            for x in range(256) for b in range(8))
    return t / (256 * 8 * 8)

def compute_BIC(s):
    from itertools import combinations
    nl_v, sac_v = [], []
    for i, j in combinations(range(8), 2):
        f = np.array([((s[x] >> i) & 1) ^ ((s[x] >> j) & 1) for x in range(256)])
        nl_v.append(nl_func(f))
        c = sum(1 for x in range(256) for b in range(8)
                if (((s[x] >> i) & 1) ^ ((s[x] >> j) & 1)) !=
                   (((s[x ^ (1 << b)] >> i) & 1) ^ ((s[x ^ (1 << b)] >> j) & 1)))
        sac_v.append(c / (256 * 8))
    return np.mean(nl_v), np.mean(sac_v)

def fast_lap(s):
    mb = 0
    for a in random.sample(range(1, 256), 40):
        for b in random.sample(range(1, 256), 40):
            c = sum(1 for x in range(256) if bin(a & x).count('1') % 2 == bin(b & s[x]).count('1') % 2)
            mb = max(mb, abs(c - 128))
    return mb / 256

def fast_dap(s):
    mc = 0
    for di in random.sample(range(1, 256), 50):
        dt = [0] * 256
        for x in range(256): dt[s[x ^ di] ^ s[x]] += 1
        mc = max(mc, max(dt))
    return mc / 256

def evaluate_sbox(s):
    nl = compute_NL(s); sac = compute_SAC(s)
    bn, bs = compute_BIC(s); lap = fast_lap(s); dap = fast_dap(s)
    return {'NL': nl, 'SAC': round(sac, 4), 'BIC_NL': round(float(bn), 4),
            'BIC_SAC': round(float(bs), 4), 'LAP': round(lap, 4), 'DAP': round(dap, 4)}

def fitness(s):
    nl = compute_NL(s); sac = compute_SAC(s)
    bn, bs = compute_BIC(s); lap = fast_lap(s); dap = fast_dap(s)
    return ((nl/112)*30 + (1-abs(sac-0.5)*2)*20 + (bn/112)*20 +
            (1-abs(bs-0.5)*2)*15 + (1-lap)*10 + (1-dap)*5)

def pmx(p1, p2):
    c = [-1]*256; a, b = sorted(random.sample(range(256), 2))
    c[a:b] = p1[a:b]; m = {p1[i]: p2[i] for i in range(a, b)}
    for i in list(range(a)) + list(range(b, 256)):
        v = p2[i]
        while v in m: v = m[v]
        c[i] = v
    return c

def mutate(s, n=4):
    s = s[:]
    for _ in range(n):
        i, j = random.sample(range(256), 2); s[i], s[j] = s[j], s[i]
    return s

def tourn(pop, fits, k=4):
    ix = random.sample(range(len(pop)), k)
    return pop[max(ix, key=lambda i: fits[i])]

# ─── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Konfigurasi GA")
pop_size   = st.sidebar.slider("Ukuran Populasi",   min_value=5,  max_value=50,  value=15, step=5)
n_gen      = st.sidebar.slider("Jumlah Generasi",   min_value=5,  max_value=100, value=20, step=5)
mut_rate   = st.sidebar.slider("Probabilitas Mutasi", min_value=0.1, max_value=0.9, value=0.35, step=0.05)
n_swaps    = st.sidebar.slider("Jumlah Swap Mutasi", min_value=1, max_value=10, value=4)
tourn_k    = st.sidebar.slider("Ukuran Turnamen",   min_value=2,  max_value=8,   value=4)
seed_val   = st.sidebar.number_input("Random Seed", min_value=0, max_value=9999, value=42)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**📌 Penjelasan Parameter:**
- **Populasi**: banyak S-box kandidat
- **Generasi**: iterasi evolusi
- **Mutasi**: prob. tukar elemen
- **Turnamen**: kompetisi seleksi
""")

# ─── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🔐 Konstruksi S-Box dengan Genetic Algorithm</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">GF(2⁸) · Kriptografi Lanjut · Evaluasi: NL, SAC, BIC-NL, BIC-SAC, LAP, DAP</div>', unsafe_allow_html=True)

# ─── Tab Layout ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Jalankan GA", "📊 Hasil & Evaluasi", "📐 Teori", "💾 Export"])

# ──────────────────────────── TAB 1: JALANKAN GA ────────────────────────────────
with tab1:
    col_run, col_info = st.columns([2, 1])
    with col_run:
        run_btn = st.button("▶ Jalankan Genetic Algorithm", type="primary", use_container_width=True)
    with col_info:
        st.info(f"Config: Pop={pop_size}, Gen={n_gen}, MutRate={mut_rate}")

    if run_btn:
        random.seed(seed_val)
        np.random.seed(seed_val)

        progress_bar = st.progress(0, text="Menginisialisasi populasi...")
        fitness_chart= st.empty()
        status_txt   = st.empty()

        pop = [list(range(256)) for _ in range(pop_size)]
        for p in pop: random.shuffle(p)

        best_s = None; best_f = -1; hist = []; gen_list = []

        for g in range(n_gen):
            fits = [fitness(s) for s in pop]
            bi = max(range(pop_size), key=lambda i: fits[i])
            if fits[bi] > best_f: best_f = fits[bi]; best_s = pop[bi][:]
            hist.append(round(best_f, 4)); gen_list.append(g + 1)

            progress_bar.progress((g + 1) / n_gen, text=f"Generasi {g+1}/{n_gen} | Best Fitness: {best_f:.3f}")
            status_txt.markdown(f"**Gen {g+1}** | Populasi Fit: {fits[bi]:.3f} | Global Best: {best_f:.3f}")

            chart_df = pd.DataFrame({"Generasi": gen_list, "Fitness": hist})
            fitness_chart.line_chart(chart_df.set_index("Generasi"))

            ei = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)[:2]
            new = [pop[i][:] for i in ei]
            while len(new) < pop_size:
                p1 = tourn(pop, fits, tourn_k); p2 = tourn(pop, fits, tourn_k)
                ch = pmx(p1, p2)
                if random.random() < mut_rate: ch = mutate(ch, n_swaps)
                new.append(ch)
            pop = new

        progress_bar.progress(1.0, text="✅ GA Selesai!")
        st.success(f"GA berhasil! Best Fitness = {best_f:.4f}")

        with st.spinner("Mengevaluasi S-box (ini butuh ~30 detik)..."):
            metrics = evaluate_sbox(best_s)

        st.session_state["best_sbox"]  = best_s
        st.session_state["metrics"]    = metrics
        st.session_state["history"]    = hist
        st.session_state["gen_list"]   = gen_list
        st.session_state["best_fit"]   = best_f

        st.balloons()
        st.markdown("### ✅ Selesai! Buka tab **Hasil & Evaluasi** untuk melihat hasil lengkap.")

    elif "best_sbox" not in st.session_state:
        st.markdown("""
        ### 👋 Selamat datang!
        
        Aplikasi ini mengkonstruksi **S-box kriptografi** menggunakan **Genetic Algorithm** pada **GF(2⁸)**.
        
        **Cara pakai:**
        1. Atur parameter di sidebar kiri
        2. Klik **▶ Jalankan Genetic Algorithm**
        3. Lihat hasil di tab **Hasil & Evaluasi**
        4. Export di tab **Export**
        
        **Estimasi waktu:** ~30-90 detik tergantung konfigurasi
        """)

# ──────────────────────────── TAB 2: HASIL ──────────────────────────────────────
with tab2:
    if "best_sbox" not in st.session_state:
        st.warning("⚠️ Belum ada hasil. Jalankan GA di tab pertama terlebih dahulu.")
    else:
        sbox    = st.session_state["best_sbox"]
        metrics = st.session_state["metrics"]
        hist    = st.session_state["history"]
        gen_list= st.session_state["gen_list"]

        st.markdown("### 📈 Konvergensi Fitness")
        chart_df = pd.DataFrame({"Fitness": hist}, index=gen_list)
        st.line_chart(chart_df)

        st.markdown("### 🔢 Evaluasi 6 Parameter")

        ideal = {'NL':112,'SAC':0.5,'BIC_NL':112,'BIC_SAC':0.5,'LAP':0.0625,'DAP':0.0078}
        aes_v = {'NL':112,'SAC':0.5039,'BIC_NL':112.0,'BIC_SAC':0.5013,'LAP':0.0625,'DAP':0.0156}
        descs = {
            'NL':     ('Nonlinearity', 'Ketahanan vs linear attack', '≥ 112', lambda v: v >= 100),
            'SAC':    ('Strict Avalanche', '1-bit flip → 50% perubahan', '= 0.5', lambda v: abs(v-0.5) < 0.05),
            'BIC_NL': ('BIC Nonlinearity', 'NL antar pasangan output bit', '≥ 100', lambda v: v >= 100),
            'BIC_SAC':('BIC SAC', 'SAC antar pasangan output bit', '≈ 0.5', lambda v: abs(v-0.5) < 0.05),
            'LAP':    ('Linear Approx.', 'Bias aproksimasi linear (rendah=aman)', '< 0.063', lambda v: v < 0.15),
            'DAP':    ('Differential Approx.', 'Prob. diferensial (rendah=aman)', '< 0.008', lambda v: v < 0.05),
        }

        cols = st.columns(3)
        for idx, (key, (name, desc, ideal_str, chk)) in enumerate(descs.items()):
            val = metrics[key]; good = chk(val)
            emoji = "✅" if good else "⚠️"
            color = "normal" if not good else "off"
            with cols[idx % 3]:
                st.metric(
                    label=f"{emoji} {name}",
                    value=f"{val}",
                    delta=f"Ideal: {ideal_str}",
                    delta_color=color
                )

        st.markdown("### 📋 Tabel Perbandingan Lengkap")
        df_eval = pd.DataFrame({
            'Parameter': list(descs.keys()),
            'Hasil GA':  [metrics[k] for k in descs],
            'Nilai AES': [aes_v[k] for k in descs],
            'Ideal':     [ideal[k] for k in descs],
            'Status':    ['✅ Baik' if descs[k][3](metrics[k]) else '⚠️ Perlu Peningkatan' for k in descs]
        })
        st.dataframe(df_eval, use_container_width=True, hide_index=True)

        st.markdown("### 🗃️ S-Box Terbaik (Heksadesimal, 16×16)")
        sbox_arr = np.array(sbox).reshape(16, 16)
        hex_df = pd.DataFrame(
            [[f"{sbox_arr[i,j]:02X}" for j in range(16)] for i in range(16)],
            index=[f"{i:X}x" for i in range(16)],
            columns=[f"x{j:X}" for j in range(16)]
        )
        st.dataframe(hex_df, use_container_width=True)

        st.markdown("### 🔍 Lookup S-Box Interaktif")
        col_l, col_r = st.columns(2)
        with col_l:
            input_val = st.number_input("Input (desimal, 0-255)", min_value=0, max_value=255, value=0)
            st.markdown(f"**S-box({input_val}) = {sbox[input_val]}** (0x{sbox[input_val]:02X})")
        with col_r:
            input_hex = st.text_input("Input (hex, contoh: FF)", value="00")
            try:
                hv = int(input_hex, 16) % 256
                st.markdown(f"**S-box(0x{hv:02X}) = 0x{sbox[hv]:02X}** ({sbox[hv]})")
            except:
                st.error("Format hex tidak valid")

# ──────────────────────────── TAB 3: TEORI ──────────────────────────────────────
with tab3:
    st.markdown("### 📐 Landasan Teori")

    with st.expander("🔢 GF(2⁸) — Galois Field", expanded=True):
        st.markdown("""
**Galois Field GF(2⁸)** adalah field berhingga dengan **256 elemen** (0 sampai 255).

- **Penjumlahan** = XOR bitwise: `a + b = a XOR b`
- **Perkalian** = modulo polinomial irreducibel
- **Polinomial AES**: `p(x) = x⁸ + x⁴ + x³ + x + 1 = 0x11B`
- Setiap elemen non-zero memiliki **invers multiplikatif unik**

Elemen 0x53 dalam biner = `01010011`, merepresentasikan `x⁶ + x⁴ + x + 1`.
        """)

    with st.expander("🧬 Genetic Algorithm untuk S-Box"):
        st.markdown("""
**Representasi:** Setiap kromosom = permutasi dari {0, 1, ..., 255} (256 elemen)

**Alur GA:**
1. **Inisialisasi** → populasi permutasi acak
2. **Evaluasi Fitness** → hitung skor kriptografi gabungan
3. **Seleksi Turnamen** → pilih k kandidat acak, ambil yang terbaik
4. **Crossover PMX** → Partially Mapped Crossover (menjaga sifat permutasi)
5. **Mutasi Swap** → tukar n pasang elemen secara acak
6. **Elitisme** → 2 individu terbaik selalu lanjut ke generasi berikutnya
7. Ulangi dari langkah 2

**Fitness Function:**
```
fitness = (NL/112)×30 + (1-|SAC-0.5|×2)×20 + (BIC_NL/112)×20 
        + (1-|BIC_SAC-0.5|×2)×15 + (1-LAP)×10 + (1-DAP)×5
```
        """)

    with st.expander("📏 6 Parameter Evaluasi"):
        param_data = {
            "Parameter": ["NL", "SAC", "BIC-NL", "BIC-SAC", "LAP", "DAP"],
            "Nama Lengkap": ["Nonlinearity", "Strict Avalanche Criterion",
                             "BIC Nonlinearity", "BIC SAC",
                             "Linear Approx. Probability", "Differential Approx. Probability"],
            "Ideal": ["112 (AES)", "0.5000", "≥ 100", "0.5000", "~0.063 (rendah)", "~0.008 (rendah)"],
            "Arti Fisik": [
                "Jauh dari fungsi linear → tahan serangan linear",
                "1-bit input flip → 50% output bit berubah",
                "NL dari XOR tiap pasangan output bit",
                "Independensi SAC antar pasangan output bit",
                "Makin kecil makin aman vs linear cryptanalysis",
                "Makin kecil makin aman vs differential cryptanalysis",
            ]
        }
        st.dataframe(pd.DataFrame(param_data), use_container_width=True, hide_index=True)

# ──────────────────────────── TAB 4: EXPORT ─────────────────────────────────────
with tab4:
    st.markdown("### 💾 Export Hasil")

    if "best_sbox" not in st.session_state:
        st.warning("⚠️ Belum ada hasil. Jalankan GA terlebih dahulu.")
    else:
        sbox    = st.session_state["best_sbox"]
        metrics = st.session_state["metrics"]
        hist    = st.session_state["history"]

        # JSON
        export_data = {"sbox": sbox, "metrics": metrics, "history": hist,
                       "config": {"pop_size": pop_size, "n_gen": n_gen,
                                  "mut_rate": mut_rate, "seed": seed_val}}
        json_str = json.dumps(export_data, indent=2)
        st.download_button("⬇️ Download S-box (JSON)", data=json_str,
                           file_name="sbox_ga_result.json", mime="application/json")

        # CSV S-box
        sbox_arr = np.array(sbox).reshape(16, 16)
        csv_rows = "\n".join(",".join(str(v) for v in row) for row in sbox_arr)
        st.download_button("⬇️ Download S-box (CSV, 16×16)", data=csv_rows,
                           file_name="sbox_ga.csv", mime="text/csv")

        # Python array
        py_code = f"""# S-box hasil Genetic Algorithm pada GF(2^8)
# Metrics: NL={metrics['NL']}, SAC={metrics['SAC']}, BIC_NL={metrics['BIC_NL']},
#          BIC_SAC={metrics['BIC_SAC']}, LAP={metrics['LAP']}, DAP={metrics['DAP']}

SBOX = {sbox}

def substitute(byte):
    \"\"\"Substitusi 1 byte menggunakan S-box GA.\"\"\"
    return SBOX[byte & 0xFF]
"""
        st.download_button("⬇️ Download S-box (Python array)", data=py_code,
                           file_name="sbox_ga.py", mime="text/plain")

        st.markdown("#### 📋 S-box (Format Array Python)")
        st.code(f"SBOX = {sbox[:32]}...  # (256 elemen total)", language="python")

        st.markdown("#### 📊 Ringkasan Metrics")
        st.json(metrics)
