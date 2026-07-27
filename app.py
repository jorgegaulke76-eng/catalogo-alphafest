import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Alphafest Itatiba", layout="wide")
DB_FILE = "catalogo_db.json"

# --- PERSISTÊNCIA (MANTIDA IGUAL PARA NÃO PERDER DADOS) ---
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

def get_imgs(p):
    imgs = p.get('Imagens', [])
    if isinstance(imgs, list) and len(imgs) > 0: return imgs
    if isinstance(p.get('Imagem'), str): return [p.get('Imagem')]
    return []

# --- LÓGICA DE VISUALIZAÇÃO (CLIENTE VS ADMIN) ---
# Se o link tiver ?cliente=true, entramos no modo cliente
query_params = st.query_params
is_cliente = query_params.get("cliente") == "true"

# --- INTERFACE DO CLIENTE (VISUALIZAÇÃO PURA) ---
if is_cliente:
    st.markdown("<header style='text-align:center;'><h1>Catálogo Alphafest</h1></header>", unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.produtos_totais)
    if not df.empty:
        for cat in df['Categoria'].unique():
            st.subheader(f"📁 {cat}")
            for _, p in df[df['Categoria'] == cat].iterrows():
                cols = st.columns([1, 4])
                imgs = get_imgs(p)
                if imgs: cols[0].image(imgs[0], width=120)
                cols[1].write(f"### {p.get('Nome', 'Produto')}")
                cols[1].write(f"_{p.get('Descricao', '')}_")
                cols[1].write(f"**R$ {p.get('Preco', '0')}**")
                cols[1].markdown("---")
    st.success("Entre em contato conosco para fazer seu pedido!")

# --- INTERFACE DO ADMIN (SEU GESTOR) ---
else:
    st.title("📦 Gestor Alphafest (Admin)")
    
    # Exibir link para o cliente
    link_cliente = f"{st.runtime.get_instance().request.host}/?cliente=true"
    st.info(f"🔗 **Link para enviar ao cliente:** `{link_cliente}`")
    
    is_editing = st.session_state.edit_index is not None
    edit_data = st.session_state.produtos_totais[st.session_state.edit_index] if is_editing else {}

    with st.expander("➕ Adicionar/Editar Produto", expanded=True):
        col1, col2 = st.columns(2)
        cat = col1.text_input("Categoria", value=edit_data.get("Categoria", "Geral"))
        nome = col1.text_input("Nome do Produto", value=edit_data.get("Nome", ""))
        links = col1.text_area("URLs das Fotos (uma por linha):", value="\n".join(get_imgs(edit_data)))
        preco = col2.text_input("Preço (R$)", value=edit_data.get("Preco", "0"))
        desc = col2.text_area("Descrição", value=edit_data.get("Descricao", ""))
        
        if st.button("Salvar Produto"):
            novo_item = {"Nome": nome, "Categoria": cat, "Imagens": [l.strip() for l in links.split('\n') if l.strip()], "Descricao": desc, "Preco": preco}
            if is_editing:
                st.session_state.produtos_totais[st.session_state.edit_index] = novo_item
                st.session_state.edit_index = None
            else:
                st.session_state.produtos_totais.append(novo_item)
            salvar_catalogo(st.session_state.produtos_totais)
            st.rerun()

    # Lista de Edição
    for i, p in enumerate(st.session_state.produtos_totais):
        cols = st.columns([1, 4, 1])
        imgs = get_imgs(p)
        if imgs: cols[0].image(imgs[0], width=80)
        cols[1].write(f"**{p.get('Nome')}** - R$ {p.get('Preco')}")
        if cols[2].button("Editar", key=f"e{i}"):
            st.session_state.edit_index = i
            st.rerun()
        if cols[2].button("Excluir", key=f"d{i}"):
            st.session_state.pop(i) # Corrigido para remover da lista correta
            st.session_state.produtos_totais.pop(i)
            salvar_catalogo(st.session_state.produtos_totais)
            st.rerun()
