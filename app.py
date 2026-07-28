import streamlit as st
import pandas as pd
import json
import os
import base64

# Configurações do App
st.set_page_config(page_title="Gestor Alphafest Master", layout="wide")
DB_FILE = "catalogo_db.json"
UPLOAD_DIR = "uploads"
LOGO_FILE = "logo.png"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- FUNÇÕES ---
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
    try:
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            ext = os.path.splitext(path)[1].replace('.', '')
            return f"data:image/{ext};base64,{encoded}"
    except: return ""

# --- GERADOR DE HTML PROFISSIONAL ---
def gerar_html_master(lista, logo_path):
    df = pd.DataFrame(lista)
    categorias = df['Categoria'].unique() if not df.empty else []
    logo_src = get_image_base64(logo_path)
    
    # CSS Profissional
    css = """
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; display: flex; color: #333; }
        #sidebar { width: 280px; background: #f8f9fa; padding: 20px; height: 100vh; position: sticky; top: 0; border-right: 1px solid #ddd; }
        #main { flex-grow: 1; padding: 40px; background: #fff; }
        .logo { width: 100%; margin-bottom: 30px; }
        .nav-link { display: block; padding: 10px; color: #555; text-decoration: none; font-weight: 600; border-radius: 5px; margin-bottom: 5px; }
        .nav-link:hover { background: #e9ecef; color: #000; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 25px; margin-top: 20px; }
        .card { border: 1px solid #eee; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: transform 0.2s; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
        .card img { width: 100%; height: 200px; object-fit: cover; }
        .card-body { padding: 15px; }
        .price { color: #2ecc71; font-weight: bold; font-size: 1.2em; }
    </style>
    """
    
    html = f"<html><head><meta charset='UTF-8'>{css}</head><body>"
    html += f"<div id='sidebar'><img src='{logo_src}' class='logo'><h3>Categorias</h3>"
    for cat in categorias:
        html += f"<a href='#{cat.replace(' ', '_')}' class='nav-link'>{cat}</a>"
    html += "</div><div id='main'><h1>Catálogo Alphafest</h1>"
    
    if not df.empty:
        for cat in categorias:
            html += f"<h2 id='{cat.replace(' ', '_')}'>{cat}</h2><div class='grid'>"
            for _, p in df[df['Categoria'] == cat].iterrows():
                # Tenta pegar a imagem, se não houver, deixa vazio
                imgs = p.get('Imagens', [])
                img_tag = f"<img src='{get_image_base64(imgs[0])}'>" if (imgs and os.path.exists(imgs[0])) else "<div style='height:200px; background:#eee;'></div>"
                html += f"""<div class='card'>{img_tag}<div class='card-body'>
                            <h3>{p.get('Nome')}</h3><p>{p.get('Descricao')}</p>
                            <p class='price'>R$ {p.get('Preco')}</p></div></div>"""
            html += "</div>"
    html += "</div></body></html>"
    return html

# --- INTERFACE ---
st.title("Gestor Alphafest Master")

# Edição ou Adição
if st.session_state.get("edit_index") is not None:
    idx = st.session_state["edit_index"]
    item = st.session_state.produtos_totais[idx]
    st.subheader(f"✏️ Editando: {item['Nome']}")
    # ... (restante da lógica de edição igual à anterior)
    if st.button("❌ Cancelar"): st.session_state.edit_index = None; st.rerun()
else:
    with st.expander("➕ Adicionar Novo Produto", expanded=True):
        # ... (restante da lógica de cadastro)
        pass

# Listagem Final com o botão de gerar
st.divider()
col1, col2 = st.columns([4, 1])
col1.subheader("📦 Produtos Cadastrados")
col2.download_button("🖨️ Gerar Catálogo HTML", gerar_html_master(st.session_state.produtos_totais, LOGO_FILE), "index.html", "text/html")

for i, p in enumerate(st.session_state.produtos_totais):
    with st.container(border=True):
        c_row1, c_row2, c_row3 = st.columns([1, 5, 2])
        try:
            if p.get('Imagens') and os.path.exists(p['Imagens'][0]):
                c_row1.image(p['Imagens'][0], width=80)
            else:
                c_row1.write("📷")
        except: c_row1.write("📷")
        
        c_row2.write(f"**{p.get('Nome')}** - R$ {p.get('Preco')}")
        if c_row3.button("✏️", key=f"e{i}"): st.session_state.edit_index = i; st.rerun()
