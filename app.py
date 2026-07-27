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
if "edit_index" not in st.session_state: st.session_state.edit_index = None

# --- FUNÇÃO DE RECUPERAÇÃO ---
def get_imgs(p):
    imgs = p.get('Imagens')
    if isinstance(imgs, list) and len(imgs) > 0: return imgs
    if p.get('Imagem'): return [p.get('Imagem')]
    return []

# --- GERAÇÃO DO HTML (LAYOUT NOVO) ---
def gerar_html_master(lista):
    html = """
    <html><head><style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; padding: 20px; color: #333; }
        .container { max-width: 900px; margin: auto; }
        header { text-align: center; margin-bottom: 40px; }
        header img { width: 180px; margin-bottom: 15px; }
        header h1 { color: #2c3e50; margin: 0; font-size: 2.5em; }
        .card { background: white; border-radius: 12px; display: flex; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .galeria { flex: 0 0 150px; }
        .galeria img { width: 130px; height: 130px; object-fit: cover; border-radius: 8px; border: 1px solid #ddd; }
        .info { flex: 1; padding-left: 20px; }
        .info h3 { margin: 0 0 10px 0; color: #e67e22; font-size: 1.5em; }
        .desc { color: #666; font-size: 1em; line-height: 1.5; margin-bottom: 10px; }
        .preco { color: #27ae60; font-weight: bold; font-size: 1.3em; display: block; }
    </style></head><body>
    <div class="container">
        <header>
            <img src="https://i.ibb.co/kV0jyTfK/logo.png" alt="Logo">
            <h1>Catálogo Alphafest</h1>
        </header>
    """
    
    for p in lista:
        imgs = get_imgs(p)
        img_html = f"<div class='galeria'><img src='{imgs[0]}'></div>" if imgs else ""
        html += f"""
        <div class='card'>
            {img_html}
            <div class='info'>
                <h3>{p.get('Nome', 'Sem nome')}</h3>
                <div class='desc'>{p.get('Descricao', '')}</div>
                <span class='preco'>R$ {p.get('Preco', '0')}</span>
            </div>
        </div>"""
    
    return html + "</div></body></html>"

# --- INTERFACE ---
st.title("📦 Gestor de Catálogo Master")

is_editing = st.session_state.edit_index is not None
edit_data = st.session_state.produtos_totais[st.session_state.edit_index] if is_editing else {}

with st.expander("➕ Adicionar/Editar Produto", expanded=True):
    col1, col2 = st.columns(2)
    cat = col1.text_input("Categoria", value=edit_data.get("Categoria", "Geral"))
    nome = col1.text_input("Nome do Produto", value=edit_data.get("Nome", ""))
    links = col1.text_area("URLs das Fotos (uma por linha):", value="\n".join(get_imgs(edit_data)))
    preco = col2.text_input("Preço (R$)", value=edit_data.get("Preco", "0"))
    desc = col2.text_area("Descrição do Produto", value=edit_data.get("Descricao", ""))
    
    if st.button("Salvar Produto"):
        novo_item = {"Nome": nome, "Categoria": cat, "Imagens": [l.strip() for l in links.split('\n') if l.strip()], "Descricao": desc, "Preco": preco}
        if is_editing:
            st.session_state.produtos_totais[st.session_state.edit_index] = novo_item
            st.session_state.edit_index = None
        else:
            st.session_state.produtos_totais.append(novo_item)
        salvar_catalogo(st.session_state.produtos_totais)
        st.rerun()

# --- LISTA ---
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

st.download_button("🖨️ BAIXAR HTML COMPLETO", gerar_html_master(st.session_state.produtos_totais), "catalogo.html", "text/html")
