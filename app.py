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

tab1, tab2 = st.tabs(["📦 Gestor de Catálogo", "🧮 Precificador 3D"])

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
        margem_percentual = st.number_input("Margem de Lucro (%)", min_value=0.0, value=100.0)

    # Cálculos
    custo_filamento = (peso_g / 1000) * preco_rolo
    custo_mao_obra = tempo_manual * valor_hora
    riscos = (custo_filamento + custo_mao_obra) * 0.15 
    custo_total = custo_filamento + custo_mao_obra + custo_energia + depreciacao + riscos
    
    # Aplicação da margem digitada pelo usuário
    multiplicador = 1 + (margem_percentual / 100)
    preco_venda = custo_total * multiplicador
    
    st.divider()
    st.metric("Custo Total de Produção", f"R$ {custo_total:.2f}")
    st.success(f"### Preço de Venda Sugerido: R$ {preco_venda:.2f}")
