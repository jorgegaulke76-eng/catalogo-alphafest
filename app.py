import streamlit as st
import pandas as pd
import requests
import base64
from groq import Groq
from bs4 import BeautifulSoup

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Gestor Alphafest", layout="wide")
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- INICIALIZAÇÃO ---
if "produtos_totais" not in st.session_state: st.session_state.produtos_totais = []

# (Funções de apoio mantidas conforme o projeto anterior)
def obter_imagem_como_base64(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        return f"data:image/jpeg;base64,{base64.b64encode(response.content).decode()}"
    except: return "https://i.ibb.co/kV0jyTfK/logo.png"

def gerar_anuncio_ia(nome_produto):
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": "Seja especialista de marketing da ALPHAFEST. Curto e vendedor."},
                      {"role": "user", "content": f"Descreva: {nome_produto}"}],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except: return f"{nome_produto} de alta qualidade."

# --- INTERFACE ---
col1_h, col2_h = st.columns([1, 10])
with col1_h: st.image("https://i.ibb.co/kV0jyTfK/logo.png", width=80)
with col2_h: st.title("ALPHAFEST - Painel de Controle")

tab1, tab2 = st.tabs(["📦 Gestor de Catálogo", "🧮 Precificador 3D"])

with tab1:
    # (Mantido como você já conhece)
    st.info("Adicione itens ao seu catálogo master.")

with tab2:
    st.subheader("Calculadora de Peças 3D (Baseada em Custos)")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        peso_g = st.number_input("Peso da Peça (g)", 0.0)
        preco_rolo = st.number_input("Preço do Rolo de Filamento (R$)", 100.0)
        horas_imp = st.number_input("Horas de Impressão", 0.0)
        custo_energia = st.number_input("Custo Energia (estimado R$)", 0.0)
    with col_c2:
        depreciacao = st.number_input("Depreciação Máquina (R$)", 5.0)
        tempo_manual = st.number_input("Horas de Mão de Obra", 0.0)
        valor_hora = st.number_input("Valor da sua Hora (R$)", 30.0)
        margem = st.selectbox("Margem de Lucro", [2.0, 2.5, 3.0], format_func=lambda x: f"{int((x-1)*100)}% de lucro")

    # Cálculos Automáticos
    custo_filamento = (peso_g / 1000) * preco_rolo
    custo_mao_obra = tempo_manual * valor_hora
    riscos = (custo_filamento + custo_mao_obra) * 0.15 # 15% para falhas/riscos
    
    custo_total = custo_filamento + custo_mao_obra + custo_energia + depreciacao + riscos
    preco_venda = custo_total * margem
    
    st.divider()
    st.metric("Custo Total de Produção", f"R$ {custo_total:.2f}")
    st.success(f"### Preço de Venda Sugerido: R$ {preco_venda:.2f}")
    st.caption("Cálculo inclui: Filamento, Mão de obra, Energia, Depreciação e 15% de margem de risco.")
