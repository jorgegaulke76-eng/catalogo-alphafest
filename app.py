import streamlit as st
import pandas as pd
import requests
import base64
from groq import Groq

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Gestor Alphafest", layout="wide")
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "produtos_totais" not in st.session_state: st.session_state.produtos_totais = []
if "preco_sugerido_temp" not in st.session_state: st.session_state.preco_sugerido_temp = 0.0

def obter_imagem_como_base64(url):
    try:
        response = requests.get(url, timeout=5)
        return f"data:image/jpeg;base64,{base64.b64encode(response.content).decode()}"
    except: return "https://i.ibb.co/kV0jyTfK/logo.png"

def gerar_anuncio_ia(nome_produto):
    try:
        res = groq_client.chat.completions.create(messages=[{"role":"user", "content": f"Descreva o produto: {nome_produto}"}], model="llama-3.1-8b-instant")
        return res.choices[0].message.content
    except: return "Produto de alta qualidade."

def gerar_html_catalogo(lista):
    html = "<html><style>.card{border:1px solid #ccc; padding:10px; margin:10px; border-radius:8px;}</style><body>"
    html += "<center><img src='https://i.ibb.co/kV0jyTfK/logo.png' width='200'></center>"
    df = pd.DataFrame(lista)
    for cat in df['Categoria'].unique():
        html += f"<h1>{cat}</h1>"
        for _, p in df[df['Categoria']==cat].iterrows():
            html += f"<div class='card'><h3>{p['Nome_Exibicao']}</h3><p>{p['Descrição']}</p></div>"
    return html + "</body></html>"

# --- INTERFACE ---
st.title("ALPHAFEST - Painel de Controle")
tab1, tab2 = st.tabs(["📦 Gestor de Catálogo", "🧮 Precificador 3D"])

with tab1:
    c_add1, c_add2 = st.columns(2)
    with c_add1:
        cat_link = st.text_input("Categoria:", "Geral")
        link = st.text_input("URL Imagem:")
        nome_p = st.text_input("Nome do Produto:")
        if st.button("Adicionar"):
            st.session_state.produtos_totais.append({"Nome_Exibicao": nome_p, "Imagem": obter_imagem_como_base64(link), "Descrição": gerar_anuncio_ia(nome_p), "Categoria": cat_link})
    
    # Grid de Edição/Visualização
    st.write("---")
    for i, p in enumerate(st.session_state.produtos_totais):
        cols = st.columns([1, 3, 1])
        cols[0].image(p['Imagem'], width=100)
        cols[1].write(f"**{p['Nome_Exibicao']}** ({p['Categoria']})")
        cols[1].caption(p['Descrição'])
        if cols[2].button("🗑️", key=f"del_{i}"):
            st.session_state.produtos_totais.pop(i); st.rerun()

    if st.button("GERAR CATÁLOGO MASTER"):
        st.download_button("📥 Baixar HTML", gerar_html_catalogo(st.session_state.produtos_totais), "catalogo.html", "text/html")

with tab2:
    p1, p2 = st.columns(2)
    peso = p1.number_input("Peso (g)", value=0.0)
    preco_r = p1.number_input("Preço Rolo (R$)", value=100.0)
    hr = p1.number_input("Horas", value=0.0)
    margem = p2.number_input("Margem (%)", value=100.0)
    valor_h = p2.number_input("Valor Hora (R$)", value=30.0)
    
    custo = ((peso/1000)*preco_r) + (hr*valor_h) + 5.0
    preco_venda = custo * (1 + (margem/100))
    st.metric("Preço de Venda Sugerido", f"R$ {preco_venda:.2f}")
    
    if st.button("💾 Usar este preço em um produto"):
        st.session_state.preco_sugerido_temp = preco_venda
        st.success("Preço salvo! Adicione o produto no Gestor com este valor.")
