import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from scipy.integrate import odeint
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulasi Antrean Drive-Thru", layout="wide")

st.title("Simulasi Antrean Drive-Thru Menggunakan Model Lotka–Volterra")
st.write("Dataset dimuat otomatis, tanpa upload CSV")

# ======================
# LOAD DATA OTOMATIS
# ======================
DATA_PATH = "queue_data.csv"

if not os.path.exists(DATA_PATH):
    st.error("File queue_data.csv tidak ditemukan di folder aplikasi")
    st.stop()

data = pd.read_csv(DATA_PATH)

# ======================
# PREPROCESSING (AMAN)
# ======================

# Gunakan wait_time langsung (menit)
queue_series = data["wait_time"].values

# Buang nilai tidak valid
queue_series = queue_series[queue_series > 0]

# Normalisasi sesuai tips pengerjaan
queue_series = queue_series / 10

# Cek keamanan
if len(queue_series) == 0:
    st.error("Data antrean kosong. Periksa kolom wait_time.")
    st.stop()

# ======================
# CEK DATA KOSONG
# ======================
if len(queue_series) == 0:
    st.error("Data antrean kosong setelah preprocessing. Periksa format waktu pada CSV.")
    st.stop()

# NORMALISASI (SESUIAI TIPS)
queue_series = queue_series / 10

# ======================
# LOAD PARAMETER NOTEBOOK
# ======================
PARAM_PATH = "best_param.json"

if os.path.exists(PARAM_PATH):
    with open(PARAM_PATH) as f:
        params = json.load(f)

    alpha0 = params["alpha"]
    beta0  = params["beta"]
    delta0 = params["delta"]
    gamma0 = params["gamma"]

    st.success("Parameter terbaik dimuat dari notebook")
else:
    st.warning("Parameter tidak ditemukan, menggunakan default")

    alpha0, beta0, delta0, gamma0 = 0.6, 0.02, 0.01, 0.4

# ======================
# SLIDER PARAMETER
# ======================
st.sidebar.header("Parameter Model")

alpha = st.sidebar.slider("α (Kedatangan)", 0.01, 2.0, alpha0, 0.01)
beta  = st.sidebar.slider("β (Pelayanan)", 0.001, 1.0, beta0, 0.001)
delta = st.sidebar.slider("δ (Adaptasi)", 0.001, 1.0, delta0, 0.001)
gamma = st.sidebar.slider("γ (Penurunan)", 0.01, 2.0, gamma0, 0.01)

# ======================
# MODEL LOTKA–VOLTERRA
# ======================
def lotka_volterra(z, t, a, b, d, g):
    x, y = z
    dxdt = a*x - b*x*y
    dydt = d*x*y - g*y
    return [dxdt, dydt]

# ======================
# SIMULASI
# ======================
x0 = queue_series[0]
y0 = 1.0

t = np.linspace(0, len(queue_series), len(queue_series))

sol = odeint(lotka_volterra, [x0, y0], t, args=(alpha, beta, delta, gamma))

# ======================
# VISUALISASI
# ======================
st.subheader("Time Series Antrean vs Simulasi")

fig1, ax1 = plt.subplots()
ax1.plot(queue_series, label="Data Antrean (Normalisasi)")
ax1.plot(sol[:, 0], label="Simulasi Model")
ax1.set_xlabel("Waktu")
ax1.set_ylabel("Panjang Antrean")
ax1.legend()
st.pyplot(fig1)

st.subheader("Phase Portrait")

fig2, ax2 = plt.subplots()
ax2.plot(sol[:, 0], sol[:, 1])
ax2.set_xlabel("Antrean Mobil (X)")
ax2.set_ylabel("Layanan (Y)")
st.pyplot(fig2)

# ======================
# INFO PARAMETER
# ======================
st.subheader("Nilai Parameter Digunakan")

st.write(f"α = {alpha:.4f}")
st.write(f"β = {beta:.4f}")
st.write(f"δ = {delta:.4f}")
st.write(f"γ = {gamma:.4f}")
