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
    return imgs if isinstance(imgs, list) else []

# --- DETECTAR MODO (ADMIN OU CLIENTE) ---
query_params = st.query_params
if query_params.get("mode") == "catalogo":
    # --- VISÃO DO CLIENTE ---
    st.markdown("<h1 style='text-align:center;'>Catálogo Alphafest</h1>", unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.produtos_totais)
    if not df.empty:
        for cat in df['Categoria'].unique():
            st.subheader(f"📁 {cat}")
            for _, p in df[df['Categoria'] == cat].iterrows():
                cols = st.columns([1, 4])
                imgs = get_imgs(p)
                if imgs: cols[0].image(imgs[0], width=150)
                cols[1].write(f"### {p.get('Nome', 'Produto')}")
                cols[1].write(f"_{p.get('Descricao', '')}_")
                cols[1].write(f"**R$ {p.get('Preco', '0')}**")
                cols[1].markdown("---")
    else:
        st.write("Catálogo em atualização. Volte em breve!")

else:
    # --- VISÃO DO ADMIN ---
    st.title("📦 Gestor Alphafest (Admin)")
    
    # Gerar link para o cliente
    base_url = st.query_params.get("mode") # Placeholder lógico
    st.success("Você está no modo Admin. Copie o link abaixo para enviar ao seu cliente:")
    # Nota: No Streamlit Cloud, o link é o seu URL atual + ?mode=catalogo
    link_cliente = f"https://catalogo-alphafest.streamlit.app/?mode=catalogo"
    st.code(link_cliente, language="text")
    
    with st.expander("➕ Adicionar/Editar Produto", expanded=True):
        col1, col2 = st.columns(2)
        cat = col1.text_input("Categoria")
        nome = col1.text_input("Nome do Produto")
        links = col1.text_area("URLs das Fotos (uma por linha)")
        preco = col2.text_input("Preço (R$)")
        desc = col2.text_area("Descrição")
        
        if st.button("Salvar Produto"):
            novo_item = {
                "Nome": nome, "Categoria": cat, 
                "Imagens": [l.strip() for l in links.split('\n') if l.strip()], 
                "Descricao": desc, "Preco": preco
            }
            st.session_state.produtos_totais.append(novo_item)
            salvar_catalogo(st.session_state.produtos_totais)
            st.success("Produto salvo!")
            st.rerun()

    # Botões de Backup/Upload
    col_bkp1, col_bkp2 = st.columns(2)
    col_bkp1.download_button("💾 Baixar Backup", data=json.dumps(st.session_state.produtos_totais), file_name="backup.json")
    
    # Listagem para edição
    st.write("---")
    for i, p in enumerate(st.session_state.produtos_totais):
        cols = st.columns([1, 4, 1])
        imgs = get_imgs(p)
        if imgs: cols[0].image(imgs[0], width=80)
        cols[1].write(f"**{p.get('Nome')}** - R$ {p.get('Preco')}")
        if cols[2].button("Excluir", key=f"d{i}"):
            st.session_state.produtos_totais.pop(i)
            salvar_catalogo(st.session_state.produtos_totais)
            st.rerun()
