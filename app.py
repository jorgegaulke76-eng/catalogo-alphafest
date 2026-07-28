import streamlit as st
import json
import os

# Configuração
st.set_page_config(page_title="Gestor Alphafest Master", layout="wide")
DB_FILE = "catalogo_limpo.json"

def carregar():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def salvar(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4)

if "produtos" not in st.session_state:
    st.session_state.produtos = carregar()

st.title("Gestor Alphafest Master")

# Adicionar produto (sem carregar arquivo de imagem para evitar erro)
with st.expander("➕ Adicionar Produto"):
    cat = st.text_input("Categoria")
    nome = st.text_input("Nome")
    preco = st.text_input("Preço")
    if st.button("Salvar"):
        st.session_state.produtos.append({"Nome": nome, "Categoria": cat, "Preco": preco})
        salvar(st.session_state.produtos)
        st.rerun()

st.divider()

# Listagem protegida
st.subheader("📦 Produtos")
for i, p in enumerate(st.session_state.produtos):
    with st.container(border=True):
        st.write(f"### {p.get('Nome')}")
        st.write(f"Preço: R$ {p.get('Preco')} | Categoria: {p.get('Categoria')}")
        if st.button("Excluir", key=f"d{i}"): 
            st.session_state.produtos.pop(i)
            salvar(st.session_state.produtos)
            st.rerun()
