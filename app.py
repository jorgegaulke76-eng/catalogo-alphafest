import streamlit as st
import pandas as pd
import requests
import base64
from groq import Groq
from bs4 import BeautifulSoup

# Configuração da página
st.set_page_config(page_title="Gestor Alphafest", layout="wide")

# --- FUNÇÕES DE APOIO ---
def calcular_preco(custos):
    # Base de cálculo simples: Soma dos campos digitados
    return sum(custos.values())

# --- INTERFACE ---
st.image("https://i.ibb.co/kV0jyTfK/logo.png", width=80)
st.title("ALPHAFEST - Painel de Controle")

tab1, tab2 = st.tabs(["📦 Gestor de Catálogo", "🧮 Precificador"])

with tab1:
    st.subheader("Gerenciamento do Catálogo Público")
    # (Mantive a lógica do seu catálogo anterior aqui - omitido para brevidade)
    st.info("Aqui você adiciona produtos para o catálogo sem preço.")

with tab2:
    st.subheader("Ferramenta de Precificação")
    tipo = st.selectbox("Selecione o produto para calcular:", ["Topo de Bolo", "Bubble", "Copo Long Drink", "Copo Térmico"])
    
    if tipo == "Topo de Bolo":
        c1, c2 = st.columns(2)
        with c1:
            tempo_imp = st.number_input("Tempo Impressão (min)", 0.0)
            tempo_arte = st.number_input("Tempo Arte (min)", 0.0)
            papel = st.number_input("Custo Papel (R$)", 0.0)
        with c2:
            palito = st.number_input("Custo Palito (R$)", 0.0)
            canudo = st.number_input("Custo Canudo (R$)", 0.0)
            energia = st.number_input("Custo Energia (R$)", 0.0)
        preco = calcular_preco({"imp": tempo_imp*0.5, "arte": tempo_arte*1.0, "p": papel, "pal": palito, "can": canudo, "e": energia})
        st.success(f"Valor Sugerido: R$ {preco:.2f}")

    elif tipo == "Bubble":
        tamanho = st.number_input("Custo Tamanho (R$)", 0.0)
        arte = st.number_input("Tempo Arte Adesivo (min)", 0.0)
        base = st.number_input("Custo Base Bexiga (R$)", 0.0)
        baloes = st.number_input("Custo Balões Internos (R$)", 0.0)
        confete = st.number_input("Custo Confete (R$)", 0.0)
        vareta = st.number_input("Custo Vareta (R$)", 0.0)
        tempo = st.number_input("Tempo Montagem (min)", 0.0)
        energia = st.number_input("Energia (R$)", 0.0)
        preco = calcular_preco([tamanho, arte*0.8, base, baloes, confete, vareta, tempo*0.5, energia])
        st.success(f"Valor Sugerido: R$ {preco:.2f}")

    elif tipo == "Copo Long Drink":
        arte = st.number_input("Tempo Arte (min)", 0.0)
        transf = st.number_input("Tempo Transfer (min)", 0.0)
        tipo_t = st.number_input("Custo Material Transfer (R$)", 0.0)
        energia = st.number_input("Energia (R$)", 0.0)
        preco = calcular_preco([arte*0.8, transf*0.8, tipo_t, energia])
        st.success(f"Valor Sugerido: R$ {preco:.2f}")

    elif tipo == "Copo Térmico":
        arte = st.number_input("Tempo Arte (min)", 0.0)
        grav = st.number_input("Tempo Gravação (min)", 0.0)
        energia = st.number_input("Energia (R$)", 0.0)
        preco = calcular_preco([arte*1.0, grav*1.5, energia])
        st.success(f"Valor Sugerido: R$ {preco:.2f}")
