"""
S-box Construction using Genetic Algorithm over GF(2^8)
Kriptografi Lanjut - Project
"""

import numpy as np
import random
import time
from itertools import combinations

# ──────────────────────────────────────────
# GF(2^8) Operations
# ──────────────────────────────────────────
IRREDUCIBLE_POLY = 0x11B  # x^8 + x^4 + x^3 + x + 1 (AES)

def gf_mul(a, b):
    """Perkalian dua elemen di GF(2^8)."""
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= (IRREDUCIBLE_POLY & 0xFF)
        b >>= 1
    return p

def gf_inverse(a):
    """Invers multiplikatif di GF(2^8). Invers(0) = 0."""
    if a == 0:
        return 0
    for b in range(1, 256):
        if gf_mul(a, b) == 1:
            return b
    return 0

# ──────────────────────────────────────────
# S-box Evaluation Criteria
# ──────────────────────────────────────────

def bool_to_bits(val, n_bits=8):
    """Konversi integer ke array bit."""
    return np.array([(val >> i) & 1 for i in range(n_bits)], dtype=np.int32)

def compute_walsh_transform(f):
    """Walsh-Hadamard Transform untuk fungsi Boolean f (array 256 nilai bit)."""
    n = 256
    W = np.array([1 - 2*int(b) for b in f], dtype=np.float64)
    step = 1
    while step < n:
        for i in range(0, n, step * 2):
            for j in range(i, i + step):
                u, v = W[j], W[j + step]
                W[j], W[j + step] = u + v, u - v
        step *= 2
    return W

def nonlinearity_of_function(f_bits):
    """NL satu fungsi Boolean."""
    W = compute_walsh_transform(f_bits)
    return int((256 - np.max(np.abs(W))) // 2)

def compute_NL(sbox):
    """Nonlinearity minimum dari 8 output bit functions."""
    nl_vals = []
    for bit in range(8):
        f = np.array([(sbox[x] >> bit) & 1 for x in range(256)], dtype=np.int32)
        nl_vals.append(nonlinearity_of_function(f))
    return min(nl_vals)

def compute_SAC(sbox):
    """
    Strict Avalanche Criterion.
    Rata-rata probabilitas bit output berubah ketika 1 bit input di-flip.
    Ideal = 0.5
    """
    total = 0
    count = 0
    for x in range(256):
        for bit_pos in range(8):
            x_flipped = x ^ (1 << bit_pos)
            diff = sbox[x] ^ sbox[x_flipped]
            total += bin(diff).count('1')
            count += 8
    return total / count

def compute_BIC(sbox):
    """
    Bit Independence Criterion.
    Mengembalikan (BIC_NL, BIC_SAC)
    """
    bic_nl_vals = []
    bic_sac_vals = []
    
    for i, j in combinations(range(8), 2):
        # f_ij(x) = bit_i(sbox(x)) XOR bit_j(sbox(x))
        f = np.array([((sbox[x] >> i) & 1) ^ ((sbox[x] >> j) & 1) for x in range(256)], dtype=np.int32)
        
        # BIC-NL
        nl = nonlinearity_of_function(f)
        bic_nl_vals.append(nl)
        
        # BIC-SAC: untuk setiap bit input yang di-flip
        sac_count = 0
        for x in range(256):
            for bit_pos in range(8):
                x_flip = x ^ (1 << bit_pos)
                fi_x  = ((sbox[x]      >> i) & 1) ^ ((sbox[x]      >> j) & 1)
                fi_xf = ((sbox[x_flip] >> i) & 1) ^ ((sbox[x_flip] >> j) & 1)
                if fi_x != fi_xf:
                    sac_count += 1
        bic_sac_vals.append(sac_count / (256 * 8))
    
    bic_nl  = np.mean(bic_nl_vals)
    bic_sac = np.mean(bic_sac_vals)
    return bic_nl, bic_sac

def compute_LAP(sbox):
    """
    Linear Approximation Probability.
    LAP = max|{x : a·x XOR b·S(x) = 0}| / 256  (dikurangi 0.5, diambil max)
    Nilai lebih rendah = lebih aman.
    """
    max_bias = 0
    for a in range(1, 256):
        for b in range(1, 256):
            count = 0
            for x in range(256):
                lhs = bin(a & x).count('1') % 2
                rhs = bin(b & sbox[x]).count('1') % 2
                if lhs == rhs:
                    count += 1
            bias = abs(count - 128)
            if bias > max_bias:
                max_bias = bias
    return max_bias / 256

def compute_DAP(sbox):
    """
    Differential Approximation Probability.
    DAP = max_{delta_in != 0} max_{delta_out} |{x: S(x XOR delta_in) XOR S(x) = delta_out}| / 256
    Nilai lebih rendah = lebih aman.
    """
    max_count = 0
    for delta_in in range(1, 256):
        diff_table = [0] * 256
        for x in range(256):
            delta_out = sbox[x ^ delta_in] ^ sbox[x]
            diff_table[delta_out] += 1
        max_count = max(max_count, max(diff_table))
    return max_count / 256

def evaluate_sbox(sbox):
    """Hitung semua 6 parameter sekaligus."""
    nl      = compute_NL(sbox)
    sac     = compute_SAC(sbox)
    bic_nl, bic_sac = compute_BIC(sbox)
    lap     = compute_LAP(sbox)
    dap     = compute_DAP(sbox)
    return {
        "NL":      nl,
        "SAC":     round(sac, 4),
        "BIC_NL":  round(bic_nl, 4),
        "BIC_SAC": round(bic_sac, 4),
        "LAP":     round(lap, 4),
        "DAP":     round(dap, 4),
    }

# ──────────────────────────────────────────
# Fitness Function
# ──────────────────────────────────────────

def fitness(sbox):
    """
    Gabungan skor kriptografi (makin tinggi = makin baik).
    NL       → normalize ke [0,1] target 112
    SAC      → proximity ke 0.5
    BIC_NL   → normalize ke [0,1] target 112
    BIC_SAC  → proximity ke 0.5
    LAP      → 1 - nilai (rendah = baik)
    DAP      → 1 - nilai (rendah = baik)
    """
    nl          = compute_NL(sbox)
    sac         = compute_SAC(sbox)
    bic_nl, bic_sac = compute_BIC(sbox)
    lap         = compute_LAP(sbox)
    dap         = compute_DAP(sbox)

    score  = (nl / 112.0) * 30          # bobot NL paling tinggi
    score += (1 - abs(sac - 0.5) * 2) * 20
    score += (bic_nl / 112.0) * 20
    score += (1 - abs(bic_sac - 0.5) * 2) * 15
    score += (1 - lap) * 10
    score += (1 - dap) * 5
    return score

# ──────────────────────────────────────────
# Genetic Algorithm
# ──────────────────────────────────────────

def random_sbox():
    """Buat S-box acak (permutasi 0-255)."""
    s = list(range(256))
    random.shuffle(s)
    return s

def crossover_pmx(p1, p2):
    """Partially Mapped Crossover (PMX) — menjaga sifat permutasi."""
    size = 256
    child = [-1] * size
    a, b = sorted(random.sample(range(size), 2))
    
    child[a:b] = p1[a:b]
    mapping = {p1[i]: p2[i] for i in range(a, b)}
    
    for i in list(range(0, a)) + list(range(b, size)):
        val = p2[i]
        while val in mapping:
            val = mapping[val]
        child[i] = val
    return child

def mutate_swap(sbox, n_swaps=3):
    """Mutasi: tukar n pasang elemen secara acak."""
    s = sbox[:]
    for _ in range(n_swaps):
        i, j = random.sample(range(256), 2)
        s[i], s[j] = s[j], s[i]
    return s

def tournament_select(population, fitnesses, k=5):
    """Pilih individu terbaik dari k kandidat acak."""
    indices = random.sample(range(len(population)), k)
    best = max(indices, key=lambda i: fitnesses[i])
    return population[best]

def run_ga(pop_size=30, generations=100, mutation_rate=0.3, verbose=True):
    """
    Jalankan Genetic Algorithm untuk konstruksi S-box.
    
    Parameter:
        pop_size    : ukuran populasi
        generations : jumlah generasi
        mutation_rate: probabilitas mutasi
        verbose     : print progress
    
    Return:
        best_sbox   : S-box terbaik (list 256 elemen)
        history     : list fitness per generasi
    """
    print(f"Inisialisasi populasi ({pop_size} individu)...")
    population = [random_sbox() for _ in range(pop_size)]
    
    best_sbox    = None
    best_fitness = -1
    history      = []

    for gen in range(generations):
        fitnesses = [fitness(s) for s in population]
        
        gen_best_idx = max(range(pop_size), key=lambda i: fitnesses[i])
        gen_best_fit = fitnesses[gen_best_idx]
        history.append(gen_best_fit)
        
        if gen_best_fit > best_fitness:
            best_fitness = gen_best_fit
            best_sbox    = population[gen_best_idx][:]
        
        if verbose and (gen % 10 == 0 or gen == generations - 1):
            print(f"  Generasi {gen+1:3d}/{generations} | Best Fitness: {gen_best_fit:.4f} | Global Best: {best_fitness:.4f}")
        
        # Elitisme: simpan 2 terbaik
        elite_indices = sorted(range(pop_size), key=lambda i: fitnesses[i], reverse=True)[:2]
        new_pop = [population[i][:] for i in elite_indices]
        
        # Isi sisa populasi
        while len(new_pop) < pop_size:
            p1 = tournament_select(population, fitnesses)
            p2 = tournament_select(population, fitnesses)
            child = crossover_pmx(p1, p2)
            if random.random() < mutation_rate:
                child = mutate_swap(child)
            new_pop.append(child)
        
        population = new_pop
    
    print(f"\nSelesai! Best Fitness = {best_fitness:.4f}")
    return best_sbox, history


# ──────────────────────────────────────────
# Main
# ──────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  S-Box Construction via Genetic Algorithm on GF(2^8)")
    print("=" * 60)

    # Jalankan GA (kurangi generations untuk testing cepat)
    start = time.time()
    best_sbox, history = run_ga(pop_size=20, generations=50, verbose=True)
    elapsed = time.time() - start

    print(f"\nWaktu eksekusi: {elapsed:.1f} detik")
    
    print("\n--- S-Box Terbaik (16x16) ---")
    for row in range(16):
        print("  " + " ".join(f"{best_sbox[row*16 + col]:3d}" for col in range(16)))

    print("\n--- Evaluasi 6 Parameter ---")
    metrics = evaluate_sbox(best_sbox)
    for k, v in metrics.items():
        print(f"  {k:8s}: {v}")

    # Simpan S-box ke file
    import json
    with open("/home/claude/best_sbox.json", "w") as f:
        json.dump({"sbox": best_sbox, "metrics": metrics}, f, indent=2)
    print("\nS-box tersimpan di best_sbox.json")
