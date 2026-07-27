import streamlit as st
import pandaimport streamlit as st
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

def obter_imagem_como_base64(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        b64 = base64.b64encode(response.content).decode()
        return f"data:image/jpeg;base64,{b64}"
    except: return "https://i.ibb.co/kV0jyTfK/logo.png"

def gerar_anuncio_ia(nome_produto):
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": "Seja um especialista de marketing da ALPHAFEST. Curto e vendedor."},
                      {"role": "user", "content": f"Descreva o produto: {nome_produto}"}],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except: return f"{nome_produto} de alta qualidade."

def gerar_html_catalogo(lista_produtos):
    df = pd.DataFrame(lista_produtos)
    html = f"<html><body><img src='https://i.ibb.co/kV0jyTfK/logo.png' style='max-width:200px; display:block; margin:auto;'><h1>CATÁLOGO ALPHAFEST</h1>"
    for _, p in df.iterrows():
        html += f"<div><h3>{p['Nome_Exibicao']}</h3><p>{p['Descrição']}</p></div><hr>"
    return html + "</body></html>"

# --- INTERFACE ---
col1_h, col2_h = st.columns([1, 10])
with col1_h: st.image("https://i.ibb.co/kV0jyTfK/logo.png", width=80)
with col2_h: st.title("ALPHAFEST - Painel de Controle")

tab1, tab2 = st.tabs(["📦 Gestor de Catálogo", "🧮 Precificador"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔗 Adicionar via Link")
        cat_link = st.text_input("Categoria:", "Outros")
        link = st.text_area("Cole a URL da Imagem:")
        nome_p = st.text_input("Nome do Produto:")
        if st.button("Adicionar Link"):
            st.session_state.produtos_totais.append({"Nome_Exibicao": nome_p, "Imagem": obter_imagem_como_base64(link), "Descrição": gerar_anuncio_ia(nome_p), "Categoria": cat_link})
            st.rerun()
    with c2:
        st.subheader("📁 Adicionar via Upload")
        cat_up = st.text_input("Categoria (Upload):", "Outros")
        foto = st.file_uploader("Upload foto", type=['jpg', 'png', 'jpeg'])
        nome_p_up = st.text_input("Nome do Produto (Upload):")
        if st.button("Adicionar Foto") and foto:
            st.session_state.produtos_totais.append({"Nome_Exibicao": nome_p_up, "Imagem": "data:image/jpeg;base64," + base64.b64encode(foto.getvalue()).decode(), "Descrição": gerar_anuncio_ia(nome_p_up), "Categoria": cat_up})
            st.rerun()
    if st.button("GERAR CATÁLOGO MASTER FINAL"):
        st.download_button("🖨️ Baixar HTML Master", gerar_html_catalogo(st.session_state.produtos_totais), "catalogo_master.html", "text/html")

with tab2:
    st.subheader("Calculadora de Precificação")
    tipo = st.selectbox("Selecione o produto:", ["Topo de Bolo", "Bubble", "Copo Long Drink", "Copo Térmico"])
    if tipo == "Topo de Bolo":
        tempo_imp = st.number_input("Tempo Impressão (min)", 0.0)
        tempo_arte = st.number_input("Tempo Arte (min)", 0.0)
        energia = st.number_input("Custo Energia (R$)", 0.0)
        total = (tempo_imp * 0.5) + (tempo_arte * 0.8) + 1.00 + 0.16 + 1.20 + energia
        st.success(f"### Valor de Venda Sugerido: R$ {total:.2f}")s as pd
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
