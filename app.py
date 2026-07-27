import streamlit as st
import pandas as pd
import json
import os

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

def get_imgs(p):
    imgs = p.get('Imagens', [])
    return imgs if isinstance(imgs, list) else []

# --- GERADOR DE HTML (PARA O NETLIFY) ---
def gerar_html_master(lista):
    df = pd.DataFrame(lista)
    html = """<html><head><meta charset="UTF-8"><style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #f4f4f4; padding: 20px; }
        .card { background: white; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .preco { color: #27ae60; font-weight: bold; }
    </style></head><body><h1>Catálogo Alphafest</h1>"""
    
    if not df.empty:
        for cat in df['Categoria'].unique():
            html += f"<h2>{cat}</h2>"
            for _, p in df[df['Categoria'] == cat].iterrows():
                html += f"<div class='card'><h3>{p.get('Nome')}</h3><p>{p.get('Descricao')}</p><span class='preco'>R$ {p.get('Preco')}</span></div>"
    return html + "</body></html>"

# --- INTERFACE (GESTOR) ---
st.title("📦 Gestor Alphafest (Admin)")

# 1. SEGURANÇA E BACKUP
st.subheader("Segurança e Backup")
col_bkp1, col_bkp2 = st.columns(2)

if st.session_state.produtos_totais:
    col_bkp1.download_button("💾 Baixar Backup (JSON)", data=json.dumps(st.session_state.produtos_totais), file_name="backup.json")

uploaded_file = col_bkp2.file_uploader("Carregar Backup (JSON)", type=['json'])
if uploaded_file is not None:
    data = json.load(uploaded_file)
    st.session_state.produtos_totais = data
    salvar_catalogo(data)
    st.rerun()

# 2. GESTÃO
st.write("---")
with st.expander("➕ Adicionar Produto", expanded=True):
    col1, col2 = st.columns(2)
    cat = col1.text_input("Categoria")
    nome = col1.text_input("Nome do Produto")
    links = col1.text_area("URLs das Fotos")
    preco = col2.text_input("Preço (R$)")
    desc = col2.text_area("Descrição")
    
    if st.button("Salvar Produto"):
        novo_item = {"Nome": nome, "Categoria": cat, "Imagens": [l.strip() for l in links.split('\n') if l.strip()], "Descricao": desc, "Preco": preco}
        st.session_state.produtos_totais.append(novo_item)
        salvar_catalogo(st.session_state.produtos_totais)
        st.rerun()

# 3. GERAR SITE
st.write("---")
st.download_button("🖨️ BAIXAR index.html (PARA ATUALIZAR O SITE)", gerar_html_master(st.session_state.produtos_totais), "index.html", "text/html")

# 4. LISTAGEM (COM IMAGENS)
st.write("---")
for i, p in enumerate(st.session_state.produtos_totais):
    # Criamos 3 colunas: Imagem, Texto, Botão
    cols = st.columns([1, 3, 1]) 
    
    # Exibe a foto se ela existir
    imgs = get_imgs(p)
    if imgs and imgs[0]: 
        cols[0].image(imgs[0], width=80)
    else:
        cols[0].write("Sem foto")
        
    # Exibe o texto
    cols[1].write(f"**{p.get('Nome')}** ({p.get('Categoria')}) - R$ {p.get('Preco')}")
    
    # Botão de exclusão
    if cols[2].button("Excluir", key=f"d{i}"):
        st.session_state.produtos_totais.pop(i)
        salvar_catalogo(st.session_state.produtos_totais)
        st.rerun()
