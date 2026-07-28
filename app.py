import streamlit as st
import pandas as pd
import json
import os
import base64

# Configurações do App
st.set_page_config(page_title="Gestor Alphafest Master", layout="wide")
DB_FILE = "catalogo_db.json"
UPLOAD_DIR = "uploads"
LOGO_FILE = "logo.png" # Definimos o nome padrão da logo

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- FUNÇÕES AUXILIARES ---
def carregar_catalogo():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def salvar_catalogo(lista):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4)

def get_image_base64(path):
    if not path or not os.path.exists(path): return ""
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
        ext = os.path.splitext(path)[1].replace('.', '')
        return f"data:image/{ext};base64,{encoded}"

def otimizar_descricao_ia(nome, desc_raw):
    return f"Produto exclusivo Alphafest: {nome}. {desc_raw.strip()} | Acabamento impecável, produzido com máquinas de última geração para garantir a perfeição em cada peça."

# Inicialização
if "produtos_totais" not in st.session_state: st.session_state.produtos_totais = carregar_catalogo()
if "edit_index" not in st.session_state: st.session_state.edit_index = None
if "temp_desc" not in st.session_state: st.session_state.temp_desc = ""

# --- GERADOR DE HTML ---
def gerar_html_master(lista, logo_path):
    df = pd.DataFrame(lista)
    categorias = df['Categoria'].unique() if not df.empty else []
    
    # Se o arquivo existir, usa base64. Se for URL, usa direto.
    final_logo_src = get_image_base64(logo_path) if os.path.exists(logo_path) else logo_path
    
    html = f"""<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
        header {{ background: #fff; padding: 20px; text-align: center; border-bottom: 2px solid #eee; }}
        .logo {{ max-width: 200px; margin-bottom: 10px; }}
        nav {{ background: #333; padding: 10px; position: sticky; top: 0; z-index: 100; display: flex; gap: 10px; overflow-x: auto; justify-content: center; }}
        nav a {{ color: white; text-decoration: none; padding: 8px 15px; white-space: nowrap; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        .card {{ background: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .card img {{ width: 100%; height: 200px; object-fit: cover; border-radius: 8px; cursor: pointer; }}
        .preco {{ color: #27ae60; font-size: 1.2em; font-weight: bold; margin-top: 10px; display: block; }}
    </style></head><body><header><img src="{final_logo_src}" class="logo"><h1>Catálogo Alphafest</h1></header><nav>"""
    for cat in categorias: html += f'<a href="#{cat.replace(" ", "_")}">{cat}</a>'
    html += "</nav><div class='container'>"
    if not df.empty:
        for cat in categorias:
            html += f"<h2 id='{cat.replace(' ', '_')}'>{cat}</h2><div class='grid'>"
            for _, p in df[df['Categoria'] == cat].iterrows():
                imgs = p.get('Imagens', [])
                img_src = get_image_base64(imgs[0]) if (imgs and os.path.exists(imgs[0])) else (imgs[0] if imgs else "")
                html += f"""<div class='card'><img src='{img_src}'><h3>{p.get('Nome')}</h3><p>{p.get('Descricao')}</p><span class='preco'>R$ {p.get('Preco')}</span></div>"""
            html += "</div>"
    html += "</div></body></html>"
    return html

# --- INTERFACE ADMIN ---
# Exibindo o Logo no Painel
if os.path.exists(LOGO_FILE):
    st.image(LOGO_FILE, width=200)
else:
    st.title("📦 Gestor Alphafest (Admin)")

# 1. Backup e Segurança
with st.expander("💾 Backup e Segurança"):
    col_bkp1, col_bkp2 = st.columns(2)
    col_bkp1.download_button("Baixar Backup JSON", data=json.dumps(st.session_state.produtos_totais), file_name="backup.json")
    uploaded = col_bkp2.file_uploader("Carregar Backup", type=['json'])
    if uploaded:
        data = json.load(uploaded)
        st.session_state.produtos_totais = data
        salvar_catalogo(data)
        st.rerun()

# 2. Adição e Edição
if st.session_state.edit_index is not None:
    idx = st.session_state.edit_index
    item = st.session_state.produtos_totais[idx]
    st.subheader(f"Editando: {item['Nome']}")
    new_cat = st.text_input("Categoria", value=item['Categoria'])
    new_nome = st.text_input("Nome", value=item['Nome'])
    new_desc = st.text_area("Descrição", value=item['Descricao'])
    new_preco = st.text_input("Preço", value=item['Preco'])
    if st.button("Salvar Alterações"):
        st.session_state.produtos_totais[idx] = {"Nome": new_nome, "Categoria": new_cat, "Imagens": item['Imagens'], "Descricao": new_desc, "Preco": new_preco}
        salvar_catalogo(st.session_state.produtos_totais)
        st.session_state.edit_index = None
        st.rerun()
else:
    with st.expander("➕ Adicionar Produto"):
        c1, c2 = st.columns(2)
        cat = c1.text_input("Categoria")
        nome = c1.text_input("Nome")
        raw_d = c1.text_area("Ideias p/ Descrição")
        if c1.button("✨ Otimizar com IA"): st.session_state.temp_desc = otimizar_descricao_ia(nome, raw_d)
        desc = c1.text_area("Descrição Final", value=st.session_state.temp_desc)
        preco = c2.text_input("Preço")
        links = c2.text_area("URLs Fotos")
        upload = c2.file_uploader("Upload local", type=['jpg', 'png'])
        if c2.button("Salvar Produto"):
            lista_imgs = [l.strip() for l in links.split('\n') if l.strip()]
            if upload:
                caminho = os.path.join(UPLOAD_DIR, upload.name)
                with open(caminho, "wb") as f: f.write(upload.getbuffer())
                lista_imgs.append(caminho)
            st.session_state.produtos_totais.append({"Nome": nome, "Categoria": cat, "Imagens": lista_imgs, "Descricao": desc, "Preco": preco})
            salvar_catalogo(st.session_state.produtos_totais)
            st.session_state.temp_desc = ""
            st.rerun()

# 3. Listagem e Gerador
st.write("---")
st.download_button("🖨️ GERAR index.html ATUALIZADO", gerar_html_master(st.session_state.produtos_totais, LOGO_FILE), "index.html", "text/html")
for i, p in enumerate(st.session_state.produtos_totais):
    cols = st.columns([0.5, 3, 1, 1])
    imgs = p.get('Imagens', [])
    if imgs and imgs[0]:
        if os.path.exists(imgs[0]): cols[0].image(imgs[0], width=60)
        else: cols[0].image(imgs[0], width=60)
    cols[1].write(f"**{p.get('Nome')}** - R$ {p.get('Preco')}")
    if cols[2].button("✏️ Editar", key=f"e{i}"): st.session_state.edit_index = i; st.rerun()
    if cols[3].button("🗑️ Excluir", key=f"d{i}"): st.session_state.produtos_totais.pop(i); salvar_catalogo(st.session_state.produtos_totais); st.rerun()
