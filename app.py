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
    final_logo_src = get_image_base64(logo_path) if os.path.exists(logo_path) else logo_path
    
    html = f"""<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .logo {{ max-width: 200px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        .card {{ background: white; border-radius: 15px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
        .card img {{ width: 100%; height: 200px; object-fit: cover; border-radius: 10px; }}
        .preco {{ color: #27ae60; font-size: 1.3em; font-weight: bold; display: block; margin-top: 10px; }}
    </style></head><body>
    <div class='header'><img src="{final_logo_src}" class='logo'><h1>Nosso Catálogo</h1></div>
    <div class='grid'>"""
    for _, p in df.iterrows():
        imgs = p.get('Imagens', [])
        img_src = get_image_base64(imgs[0]) if (imgs and os.path.exists(imgs[0])) else (imgs[0] if imgs else "")
        html += f"<div class='card'><img src='{img_src}'><h3>{p.get('Nome')}</h3><p>{p.get('Descricao')}</p><span class='preco'>R$ {p.get('Preco')}</span></div>"
    html += "</div></body></html>"
    return html

# --- INTERFACE CENTRALIZADA ---
c_left, c_main, c_right = st.columns([1, 5, 1])

with c_main:
    # 1. Logo Centralizada (Técnica do Sanduíche de colunas interno)
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, use_container_width=True)
    
    st.markdown("<h1 style='text-align: center;'>Gestor Alphafest Master</h1>", unsafe_allow_html=True)
    st.divider()

    # 2. Backup e Segurança
    with st.expander("💾 Backup e Segurança", expanded=False):
        col_b1, col_b2 = st.columns(2)
        col_b1.download_button("📥 Baixar Backup JSON", data=json.dumps(st.session_state.produtos_totais), file_name="backup.json")
        uploaded = col_b2.file_uploader("📤 Carregar Backup", type=['json'])
        if uploaded:
            st.session_state.produtos_totais = json.load(uploaded)
            salvar_catalogo(st.session_state.produtos_totais)
            st.rerun()

    # 3. Adição e Edição
    if st.session_state.edit_index is not None:
        idx = st.session_state.edit_index
        item = st.session_state.produtos_totais[idx]
        st.subheader(f"✏️ Editando: {item['Nome']}")
        c_e1, c_e2 = st.columns(2)
        new_cat = c_e1.text_input("Categoria", value=item['Categoria'])
        new_nome = c_e1.text_input("Nome", value=item['Nome'])
        new_desc = c_e2.text_area("Descrição", value=item['Descricao'])
        new_preco = c_e2.text_input("Preço", value=item['Preco'])
        if st.button("💾 Salvar Alterações"):
            st.session_state.produtos_totais[idx] = {"Nome": new_nome, "Categoria": new_cat, "Imagens": item['Imagens'], "Descricao": new_desc, "Preco": new_preco}
            salvar_catalogo(st.session_state.produtos_totais)
            st.session_state.edit_index = None
            st.rerun()
    else:
        with st.expander("➕ Adicionar Novo Produto", expanded=True):
            c1, c2 = st.columns(2)
            cat = c1.text_input("Categoria")
            nome = c1.text_input("Nome do Produto")
            raw_d = c1.text_area("Ideias para descrição")
            if c1.button("✨ Otimizar com IA"): st.session_state.temp_desc = otimizar_descricao_ia(nome, raw_d)
            desc = c1.text_area("Descrição Final", value=st.session_state.temp_desc)
            preco = c2.text_input("Preço (R$)")
            links = c2.text_area("URLs Fotos (se houver)")
            upload = c2.file_uploader("Upload Foto", type=['jpg', 'png', 'jpeg'])
            if c2.button("✅ Salvar Produto"):
                lista_imgs = [l.strip() for l in links.split('\n') if l.strip()]
                if upload:
                    caminho = os.path.join(UPLOAD_DIR, upload.name)
                    with open(caminho, "wb") as f: f.write(upload.getbuffer())
                    lista_imgs.append(caminho)
                st.session_state.produtos_totais.append({"Nome": nome, "Categoria": cat, "Imagens": lista_imgs, "Descricao": desc, "Preco": preco})
                salvar_catalogo(st.session_state.produtos_totais)
                st.session_state.temp_desc = ""
                st.rerun()

    st.divider()
    
    # 4. Listagem
    col_gen1, col_gen2 = st.columns([4, 1])
    col_gen1.subheader("📦 Produtos Cadastrados")
    col_gen2.download_button("🖨️ Gerar HTML", gerar_html_master(st.session_state.produtos_totais, LOGO_FILE), "index.html", "text/html")
    
    for i, p in enumerate(st.session_state.produtos_totais):
        with st.container(border=True):
            # Layout das colunas na lista: Imagem (largura fixa) + Texto + Botões
            c_row1, c_row2, c_row3 = st.columns([1, 5, 2])
            imgs = p.get('Imagens', [])
            if imgs and imgs[0]:
                if os.path.exists(imgs[0]): 
                    c_row1.image(imgs[0], width=100)
                else: 
                    c_row1.image(imgs[0], width=100) # Tenta exibir links externos
            
            c_row2.write(f"### {p.get('Nome')}")
            c_row2.write(f"**Preço:** R$ {p.get('Preco')} | **Cat:** {p.get('Categoria')}")
            
            if c_row3.button("✏️ Editar", key=f"e{i}"): st.session_state.edit_index = i; st.rerun()
            if c_row3.button("🗑️ Excluir", key=f"d{i}"): st.session_state.produtos_totais.pop(i); salvar_catalogo(st.session_state.produtos_totais); st.rerun()
