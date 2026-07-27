import streamlit as st
import pandas as pd
import requests
import json
import os

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Gestor Alphafest Master", layout="wide")

DB_FILE = "catalogo_db.json"

# --- PERSISTÊNCIA ---
def carregar_catalogo():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def salvar_catalogo(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4)

if "produtos_totais" not in st.session_state: 
    st.session_state.produtos_totais = carregar_catalogo()

# --- FUNÇÃO DE RECUPERAÇÃO DE IMAGENS (SEGURA) ---
def buscar_imagens_produto(p):
    """Tenta pegar imagens do novo formato (lista) ou do antigo (string)"""
    imgs = p.get('Imagens')
    if imgs and isinstance(imgs, list):
        return imgs
    elif p.get('Imagem'):
        return [p.get('Imagem')] # Converte a antiga string em lista
    return []

# --- GERAÇÃO DO HTML ---
def gerar_html_master(lista):
    html = """
    <html><head><style>
        body { font-family: Arial; padding: 20px; }
        .card { display: flex; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; }
        .galeria { display: flex; gap: 10px; margin-right: 20px; flex-wrap: wrap; }
        .galeria img { width: 100px; height: 100px; object-fit: cover; cursor: pointer; transition: 0.3s; }
        .galeria img:hover { opacity: 0.7; }
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
            imagens = buscar_imagens_produto(p)
            html += f"<div class='card'><div class='galeria'>"
            for img in imagens:
                html += f"<img src='{img}' onclick=\"openModal('{img}')\">"
            html += f"</div><div><h3>{p.get('Nome', 'Produto')}</h3><p>{p.get('Descricao', '')}</p></div></div>"
    
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

with st.expander("➕ Adicionar Novo Produto"):
    col1, col2 = st.columns(2)
    cat = col1.text_input("Categoria", "Geral")
    nome = col1.text_input("Nome do Produto")
    links_fotos = col1.text_area("URLs das Fotos (uma por linha):")
    
    tema = col2.text_input("Tema/Ocasião")
    cor = col2.text_input("Cor/Material")
    
    if st.button("Adicionar ao Master"):
        lista_imgs = [url.strip() for url in links_fotos.split('\n') if url.strip()]
        novo_item = {
            "Nome": nome, 
            "Categoria": cat, 
            "Imagens": lista_imgs, 
            "Descricao": f"Tema: {tema} | Material: {cor}"
        }
        st.session_state.produtos_totais.append(novo_item)
        salvar_catalogo(st.session_state.produtos_totais)
        st.success("Produto adicionado!")
        st.rerun()

# --- VISUALIZAÇÃO ---
st.write("---")
for i, p in enumerate(st.session_state.produtos_totais):
    c1, c2 = st.columns([1, 4])
    imgs = buscar_imagens_produto(p)
    if imgs:
        c1.image(imgs[0], width=100)
    
    c2.write(f"**{p.get('Nome')}** ({len(imgs)} fotos)")
    if c2.button("Excluir", key=f"del_{i}"):
        st.session_state.produtos_totais.pop(i)
        salvar_catalogo(st.session_state.produtos_totais)
        st.rerun()
            
st.write("---")
st.download_button("🖨️ BAIXAR CATÁLOGO MASTER (HTML)", gerar_html_master(st.session_state.produtos_totais), "catalogo_master.html", "text/html")
