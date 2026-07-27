import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Alphafest Itatiba", layout="wide")
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

def get_imgs(p):
    imgs = p.get('Imagens', [])
    if isinstance(imgs, list) and len(imgs) > 0: return imgs
    return []

# --- INTERFACE ---
st.title("📦 Gestor Alphafest (Admin)")

# 1. BOTÃO DE BACKUP (Para você não perder seus dados nunca mais)
st.subheader("Segurança de Dados")
if st.session_state.produtos_totais:
    btn = st.download_button(
        label="💾 Baixar Backup da Base de Dados (JSON)",
        data=json.dumps(st.session_state.produtos_totais, indent=4),
        file_name="catalogo_db_backup.json",
        mime="application/json"
    )

# 2. GESTOR DE PRODUTOS
st.write("---")
with st.expander("➕ Adicionar/Editar Produto", expanded=True):
    col1, col2 = st.columns(2)
    cat = col1.text_input("Categoria")
    nome = col1.text_input("Nome do Produto")
    links = col1.text_area("URLs das Fotos (uma por linha)")
    preco = col2.text_input("Preço (R$)")
    desc = col2.text_area("Descrição")
    
    if st.button("Salvar Produto"):
        novo_item = {
            "Nome": nome, 
            "Categoria": cat, 
            "Imagens": [l.strip() for l in links.split('\n') if l.strip()], 
            "Descricao": desc, 
            "Preco": preco
        }
        st.session_state.produtos_totais.append(novo_item)
        salvar_catalogo(st.session_state.produtos_totais)
        st.success("Produto salvo!")
        st.rerun()

# 3. LISTAGEM SIMPLES
st.write("---")
for i, p in enumerate(st.session_state.produtos_totais):
    cols = st.columns([1, 4, 1])
    imgs = get_imgs(p)
    if imgs: cols[0].image(imgs[0], width=80)
    cols[1].write(f"**{p.get('Nome')}** ({p.get('Categoria')}) - R$ {p.get('Preco')}")
    if cols[2].button("Excluir", key=f"d{i}"):
        st.session_state.produtos_totais.pop(i)
        salvar_catalogo(st.session_state.produtos_totais)
        st.rerun()
