import streamlit as st
import pandas as pd
import requests
import base64
import json
import os
from groq import Groq

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Gestor Alphafest Master", layout="wide")
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
DB_FILE = "catalogo_db.json"

# --- PERSISTÊNCIA (LER E SALVAR) ---
def carregar_catalogo():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def salvar_catalogo(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4)

# Inicializa o estado com o que está salvo no arquivo
if "produtos_totais" not in st.session_state: 
    st.session_state.produtos_totais = carregar_catalogo()

def obter_imagem_como_base64(url):
    try:
        response = requests.get(url, timeout=5)
        return f"data:image/jpeg;base64,{base64.b64encode(response.content).decode()}"
    except: return "https://i.ibb.co/kV0jyTfK/logo.png"

def gerar_anuncio_ia(nome, especs):
    try:
        res = groq_client.chat.completions.create(
            messages=[{"role":"user", "content": f"Crie uma descrição vendedora para: {nome} com estas especificações: {especs}"}], 
            model="llama-3.1-8b-instant"
        )
        return res.choices[0].message.content
    except: return f"{nome} - {especs}"

def gerar_html_master(lista):
    html = """
    <html><head><style>
        body { font-family: Arial; padding: 20px; }
        .card { display: flex; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; align-items: center; }
        .card img { width: 150px; margin-right: 20px; cursor: pointer; transition: 0.3s; }
        .card img:hover { opacity: 0.7; }
        .menu { background: #f9f9f9; padding: 15px; border: 1px solid #ddd; margin-bottom: 20px; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }
        .modal-content { margin: auto; display: block; max-width: 80%; max-height: 80%; margin-top: 50px; }
    </style></head><body>
    <center><h1>CATÁLOGO MASTER - ALPHAFEST ITATIBA</h1></center>
    """
    if not lista: return html + "</body></html>"
    
    df = pd.DataFrame(lista)
    html += "<div class='menu'><h3>Selecione a Categoria:</h3><ul>"
    for cat in df['Categoria'].unique():
        html += f"<li><a href='#{cat}'>{cat}</a></li>"
    html += "</ul></div>"
    
    for cat in df['Categoria'].unique():
        html += f"<h2 id='{cat}'>📁 {cat}</h2>"
        for _, p in df[df['Categoria']==cat].iterrows():
            img_src = p.get('Imagem', 'https://i.ibb.co/kV0jyTfK/logo.png')
            html += f"""
            <div class='card'>
                <img src='{img_src}' onclick="openModal('{img_src}')">
                <div><h3>{p.get('Nome', 'Produto')}</h3><p>{p.get('Descricao', '')}</p></div>
            </div>
            """
    
    html += """
    <div id="myModal" class="modal" onclick="this.style.display='none'">
        <img class="modal-content" id="img01">
    </div>
    <script>
        function openModal(src) {
            document.getElementById('myModal').style.display = 'block';
            document.getElementById('img01').src = src;
        }
    </script>
    </body></html>
    """
    return html

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
        novo_item = {
            "Nome": nome, 
            "Categoria": cat, 
            "Imagem": obter_imagem_como_base64(link_foto), 
            "Descricao": desc
        }
        st.session_state.produtos_totais.append(novo_item)
        salvar_catalogo(st.session_state.produtos_totais) # Salva no arquivo!
        st.success("Produto adicionado com sucesso!")
        st.rerun()

# --- VISUALIZAÇÃO ---
st.write("---")
if st.session_state.produtos_totais:
    st.subheader("Produtos no Catálogo Master")
    for i, p in enumerate(st.session_state.produtos_totais):
        c1, c2 = st.columns([1, 4])
        c1.image(p.get('Imagem', 'https://i.ibb.co/kV0jyTfK/logo.png'), width=120)
        c2.write(f"**{p.get('Nome', 'Sem Nome')}** | *{p.get('Categoria', 'Sem Cat.')}*")
        c2.caption(p.get('Descricao', ''))
        if c2.button("Excluir", key=f"del_{i}"):
            st.session_state.produtos_totais.pop(i)
            salvar_catalogo(st.session_state.produtos_totais) # Salva a exclusão!
            st.rerun()
            
    st.write("---")
    st.download_button("🖨️ BAIXAR CATÁLOGO MASTER (HTML)", gerar_html_master(st.session_state.produtos_totais), "catalogo_master.html", "text/html")
