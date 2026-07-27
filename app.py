import streamlit as st
import pandas as pd
import requests
import json
import os
from groq import Groq

st.set_page_config(page_title="Gestor Alphafest Master", layout="wide")

# Tente configurar a API
try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    groq_client = None

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
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# --- FUNÇÕES ---
def get_lista_imagens(p):
    imgs = p.get('Imagens')
    return imgs if isinstance(imgs, list) else []

def gerar_html_master(lista):
    html = """<html><head><style>
        body { font-family: Arial; padding: 20px; }
        .card { display: flex; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; }
        .galeria img { width: 100px; height: 100px; margin-right: 10px; }
        .preco { font-weight: bold; color: #2e7d32; }
    </style></head><body><center><h1>CATÁLOGO MASTER - ALPHAFEST ITATIBA</h1></center>"""
    
    if not lista: return html + "</body></html>"
    df = pd.DataFrame(lista)
    for cat in df['Categoria'].unique():
        html += f"<h2>📁 {cat}</h2>"
        for _, p in df[df['Categoria']==cat].iterrows():
            imgs = get_lista_imagens(p)
            html += f"<div class='card'><div class='galeria'>"
            for img in imgs: html += f"<img src='{img}'>"
            html += f"</div><div><h3>{p.get('Nome', 'Produto')}</h3><p>{p.get('Descricao', '')}</p><span class='preco'>R$ {p.get('Preco', '0')}</span></div></div>"
    return html + "</body></html>"

# --- INTERFACE ---
st.title("📦 Gestor de Catálogo Master")

# Lógica de Edição
is_editing = st.session_state.edit_index is not None
edit_data = st.session_state.produtos_totais[st.session_state.edit_index] if is_editing else {}

with st.expander("➕ Adicionar/Editar Produto", expanded=True):
    col1, col2 = st.columns(2)
    cat = col1.text_input("Categoria", value=edit_data.get("Categoria", "Geral"))
    nome = col1.text_input("Nome do Produto", value=edit_data.get("Nome", ""))
    links = col1.text_area("URLs das Fotos (uma por linha):", value="\n".join(get_lista_imagens(edit_data)))
    preco = col2.text_input("Preço de Venda (R$)", value=edit_data.get("Preco", "0"))
    tema = col2.text_input("Descrição Curta", value=edit_data.get("Descricao", ""))
    
    btn_label = "Salvar Alterações" if is_editing else "Adicionar ao Master"
    if st.button(btn_label):
        lista_imgs = [url.strip() for url in links.split('\n') if url.strip()]
        novo_item = {"Nome": nome, "Categoria": cat, "Imagens": lista_imgs, "Descricao": tema, "Preco": preco}
        
        if is_editing:
            st.session_state.produtos_totais[st.session_state.edit_index] = novo_item
            st.session_state.edit_index = None
        else:
            st.session_state.produtos_totais.append(novo_item)
            
        salvar_catalogo(st.session_state.produtos_totais)
        st.success("Operação realizada!")
        st.rerun()

# --- VISUALIZAÇÃO ---
for i, p in enumerate(st.session_state.produtos_totais):
    c1, c2, c3 = st.columns([1, 3, 1])
    c1.image(get_lista_imagens(p)[0] if get_lista_imagens(p) else "https://i.ibb.co/kV0jyTfK/logo.png", width=80)
    c2.write(f"**{p.get('Nome')}** - R$ {p.get('Preco')}")
    if c3.button("Editar", key=f"edit_{i}"):
        st.session_state.edit_index = i
        st.rerun()
    if c3.button("Excluir", key=f"del_{i}"):
        st.session_state.produtos_totais.pop(i)
        salvar_catalogo(st.session_state.produtos_totais)
        st.rerun()

st.download_button("🖨️ BAIXAR CATÁLOGO MASTER (HTML)", gerar_html_master(st.session_state.produtos_totais), "catalogo_master.html", "text/html")
