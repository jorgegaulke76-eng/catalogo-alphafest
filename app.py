import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Gestor Alphafest Master", layout="wide")
DB_FILE = "catalogo_db.json"

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
if "edit_index" not in st.session_state: st.session_state.edit_index = None

# --- FUNÇÃO QUE RECUPERA IMAGENS DE QUALQUER VERSÃO ---
def get_imgs(p):
    # Tenta na lista nova 'Imagens', depois na string antiga 'Imagem'
    imgs = p.get('Imagens')
    if isinstance(imgs, list) and len(imgs) > 0: return imgs
    if p.get('Imagem'): return [p.get('Imagem')]
    return []

def gerar_html_master(lista):
    html = "<html><head><style>.card{display:flex; border:1px solid #ddd; padding:15px; margin:10px 0; border-radius:8px; align-items:center;} .galeria img {width:80px; margin-right:10px;}</style></head><body><h1>CATÁLOGO MASTER</h1>"
    for p in lista:
        imgs = get_imgs(p)
        img_tag = f"<div class='galeria'>{''.join([f'<img src=\"{i}\">' for i in imgs])}</div>" if imgs else ""
        html += f"<div class='card'>{img_tag}<div><h3>{p.get('Nome', 'Sem nome')}</h3><p>R$ {p.get('Preco', '0')}</p></div></div>"
    return html + "</body></html>"

st.title("📦 Gestor de Catálogo Master")

# Formulario de Adição/Edição
is_editing = st.session_state.edit_index is not None
edit_data = st.session_state.produtos_totais[st.session_state.edit_index] if is_editing else {}

with st.expander("➕ Adicionar/Editar Produto", expanded=True):
    col1, col2 = st.columns(2)
    cat = col1.text_input("Categoria", value=edit_data.get("Categoria", "Geral"))
    nome = col1.text_input("Nome do Produto", value=edit_data.get("Nome", ""))
    links = col1.text_area("URLs das Fotos (uma por linha):", value="\n".join(get_imgs(edit_data)))
    preco = col2.text_input("Preço (R$)", value=edit_data.get("Preco", "0"))
    desc = col2.text_input("Descrição", value=edit_data.get("Descricao", ""))
    
    if st.button("Salvar Produto"):
        novo_item = {"Nome": nome, "Categoria": cat, "Imagens": [l.strip() for l in links.split('\n') if l.strip()], "Descricao": desc, "Preco": preco}
        if is_editing:
            st.session_state.produtos_totais[st.session_state.edit_index] = novo_item
            st.session_state.edit_index = None
        else:
            st.session_state.produtos_totais.append(novo_item)
        salvar_catalogo(st.session_state.produtos_totais)
        st.rerun()

# Lista de Produtos
for i, p in enumerate(st.session_state.produtos_totais):
    cols = st.columns([1, 4, 1])
    imgs = get_imgs(p)
    if imgs: cols[0].image(imgs[0], width=80)
    cols[1].write(f"**{p.get('Nome')}** - R$ {p.get('Preco')}")
    if cols[2].button("Editar", key=f"e{i}"):
        st.session_state.edit_index = i
        st.rerun()
    if cols[2].button("Excluir", key=f"d{i}"):
        st.session_state.produtos_totais.pop(i)
        salvar_catalogo(st.session_state.produtos_totais)
        st.rerun()

st.download_button("🖨️ BAIXAR HTML", gerar_html_master(st.session_state.produtos_totais), "catalogo.html", "text/html")
