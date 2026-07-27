import streamlit as st
import pandas as pd
import requests
import base64
from groq import Groq

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Gestor Alphafest Master", layout="wide")
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "produtos_totais" not in st.session_state: st.session_state.produtos_totais = []

def obter_imagem_como_base64(url):
    try:
        response = requests.get(url, timeout=5)
        return base64.b64encode(response.content).decode()
    except: return None

def gerar_anuncio_ia(nome, especs):
    try:
        res = groq_client.chat.completions.create(
            messages=[{"role":"user", "content": f"Crie uma descrição vendedora para: {nome} com estas especificações: {especs}"}], 
            model="llama-3.1-8b-instant"
        )
        return res.choices[0].message.content
    except: return f"{nome} - {especs}"

def gerar_html_master(lista):
    html = "<html><style>.card{border:1px solid #ddd; padding:15px; margin:10px; border-radius:10px; font-family:Arial;}</style><body>"
    html += "<center><h1>CATÁLOGO MASTER ALPHAFEST</h1></center>"
    df = pd.DataFrame(lista)
    for cat in df['Categoria'].unique():
        html += f"<h2>{cat}</h2>"
        for _, p in df[df['Categoria']==cat].iterrows():
            html += f"<div class='card'><h3>{p['Nome']}</h3><p>{p['Descricao']}</p></div>"
    return html + "</body></html>"

# --- INTERFACE ---
st.title("📦 Gestor de Catálogo Master")

with st.expander("➕ Adicionar Novo Produto ao Catálogo"):
    col1, col2 = st.columns(2)
    cat = col1.text_input("Categoria", "Geral")
    nome = col1.text_input("Nome do Produto")
    link_foto = col1.text_input("URL da Foto")
    
    tema = col2.text_input("Tema/Ocasião")
    nome_pers = col2.text_input("Nome Personalizado")
    cor = col2.text_input("Cor/Material")
    
    if st.button("Adicionar ao Master"):
        especs = f"Tema: {tema}, Nome: {nome_pers}, Cor: {cor}"
        desc = gerar_anuncio_ia(nome, especs)
        st.session_state.produtos_totais.append({
            "Nome": nome, "Categoria": cat, "Imagem_B64": obter_imagem_como_base64(link_foto), 
            "Descricao": desc, "Especificacoes": especs
        })
        st.success("Produto adicionado ao catálogo!")
        st.rerun()

# --- VISUALIZAÇÃO E EXPORTAÇÃO ---
st.write("---")
if st.session_state.produtos_totais:
    st.subheader("Produtos no Catálogo Master")
    for i, p in enumerate(st.session_state.produtos_totais):
        c1, c2 = st.columns([1, 4])
        
        # USO DO .get() PARA EVITAR KEYERROR
        img_data = p.get('Imagem_B64')
        if img_data:
            c1.markdown(f'<img src="data:image/jpeg;base64,{img_data}" width="120">', unsafe_allow_html=True)
        else:
            c1.image("https://i.ibb.co/kV0jyTfK/logo.png", width=120)
            
        c2.write(f"**{p.get('Nome', 'Sem Nome')}** | *{p.get('Categoria', 'Sem Categoria')}*")
        c2.caption(p.get('Descricao', ''))
        if c2.button("Excluir", key=f"del_{i}"):
            st.session_state.produtos_totais.pop(i)
            st.rerun()
            
    st.write("---")
    st.download_button("🖨️ BAIXAR CATÁLOGO MASTER (HTML)", gerar_html_master(st.session_state.produtos_totais), "catalogo_master.html", "text/html")
