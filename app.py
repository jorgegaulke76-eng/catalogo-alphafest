import streamlit as st
import pandas as pd
import json
import os
import base64

# Configurações do App
st.set_page_config(page_title="Gestor Alphafest Master", layout="wide")
DB_FILE = "catalogo_db.json"
UPLOAD_DIR = "uploads"

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
if "temp_desc" not in st.session_state: st.session_state.temp_desc = ""

# --- GERADOR DE HTML ---
def gerar_html_master(lista, logo_input):
    df = pd.DataFrame(lista)
    categorias = df['Categoria'].unique() if not df.empty else []
    
    # Processa Logo (se for arquivo local, converte para Base64)
    if logo_input.lower().startswith("http"):
        final_logo_src = logo_input
    else:
        final_logo_src = get_image_base64(logo_input)
    
    html = f"""<html><head><meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
        header {{ background: #fff; padding: 20px; text-align: center; border-bottom: 2px solid #eee; }}
        .logo {{ max-width: 200px; margin-bottom: 10px; }}
        nav {{ background: #333; padding: 10px; position: sticky; top: 0; z-index: 100; display: flex; gap: 10px; overflow-x: auto; justify-content: center; }}
        nav a {{ color: white; text-decoration: none; padding: 8px 15px; white-space: nowrap; font-size: 0.9em; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        .card {{ background: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .card img {{ width: 100%; height: 200px; object-fit: cover; border-radius: 8px; cursor: pointer; }}
        .preco {{ color: #27ae60; font-size: 1.2em; font-weight: bold; margin-top: 10px; display: block; }}
        .modal {{ display: none; position: fixed; z-index: 1000; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.9); }}
        .modal-img {{ margin: auto; display: block; max-width: 90%; max-height: 80%; margin-top: 50px; }}
    </style></head><body>
    <header><img src="{final_logo_src}" class="logo"><h1>Catálogo Alphafest</h1></header>
    <nav>"""
    for cat in categorias: html += f'<a href="#{cat.replace(" ", "_")}">{cat}</a>'
    html += "</nav><div class='container'>"
    
    if not df.empty:
        for cat in categorias:
            html += f"<h2 id='{cat.replace(' ', '_')}'>{cat}</h2><div class='grid'>"
            for _, p in df[df['Categoria'] == cat].iterrows():
                imgs = p.get('Imagens', [])
                img_src = get_image_base64(imgs[0]) if (imgs and os.path.exists(imgs[0])) else (imgs[0] if imgs else "")
                
                html += f"""
                <div class='card'>
                    <img src='{img_src}' onclick="document.getElementById('modal').style.display='block'; document.getElementById('modal-content').src='{img_src}'">
                    <h3>{p.get('Nome')}</h3>
                    <p>{p.get('Descricao')}</p>
                    <span class='preco'>R$ {p.get('Preco')}</span>
                </div>"""
            html += "</div>"
            
    html += """</div><div id="modal" class="modal" onclick="this.style.display='none'">
        <span class="close">&times;</span>
        <img class="modal-img" id="modal-content">
    </div></body></html>"""
    return html

# --- INTERFACE ADMIN ---
st.title("📦 Gestor Alphafest (Admin)")

# Configurações de Logo
logo_path = st.text_input("Caminho do arquivo ou link da Logo", value="logo.png")

with st.expander("💾 Backup e Segurança"):
    col_bkp1, col_bkp2 = st.columns(2)
    col_bkp1.download_button("Baixar Backup JSON", data=json.dumps(st.session_state.produtos_totais), file_name="backup.json")
    uploaded = col_bkp2.file_uploader("Carregar Backup", type=['json'])
    if uploaded:
        data = json.load(uploaded)
        st.session_state.produtos_totais = data
        salvar_catalogo(data)
        st.rerun()

with st.expander("➕ Adicionar Novo Produto", expanded=True):
    c1, c2 = st.columns(2)
    cat = c1.text_input("Categoria")
    nome = c1.text_input("Nome do Produto")
    
    raw_desc = c1.text_area("Descrição Rápida (Ideias)")
    if c1.button("✨ Otimizar com IA"):
        st.session_state.temp_desc = otimizar_descricao_ia(nome, raw_desc)
    
    desc_final = c1.text_area("Descrição Final", value=st.session_state.temp_desc)
    
    links = c2.text_area("URLs das Fotos (uma por linha)")
    upload = c2.file_uploader("Ou enviar foto local", type=['jpg', 'png', 'jpeg'])
    preco = c2.text_input("Preço (R$)")
    
    if c2.button("Salvar Produto"):
        lista_imgs = [l.strip() for l in links.split('\n') if l.strip()]
        if upload:
            caminho = os.path.join(UPLOAD_DIR, upload.name)
            with open(caminho, "wb") as f: f.write(upload.getbuffer())
            lista_imgs.append(caminho)
            
        st.session_state.produtos_totais.append({"Nome": nome, "Categoria": cat, "Imagens": lista_imgs, "Descricao": desc_final, "Preco": preco})
        salvar_catalogo(st.session_state.produtos_totais)
        st.session_state.temp_desc = ""
        st.rerun()

st.write("---")
st.download_button("🖨️ GERAR E BAIXAR index.html ATUALIZADO", gerar_html_master(st.session_state.produtos_totais, logo_path), "index.html", "text/html")

for i, p in enumerate(st.session_state.produtos_totais):
    c = st.columns([1, 4, 1])
    imgs = p.get('Imagens', [])
    if imgs: 
        if os.path.exists(imgs[0]): c[0].image(imgs[0], width=100)
        else: c[0].image(imgs[0], width=100)
    c[1].write(f"**{p.get('Nome')}** - R$ {p.get('Preco')}")
    if c[2].button("Excluir", key=f"d{i}"):
        st.session_state.produtos_totais.pop(i)
        salvar_catalogo(st.session_state.produtos_totais)
        st.rerun()
