import streamlit as st
import pandas as pd
import json
import os
import base64

# Configurações
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
    final_logo_src = get_image_base64(logo_path) if os.path.exists(logo_path) else ""
    
    html = f"<html><body><div class='header'><img src='{final_logo_src}' style='max-width:200px'><h1>Catálogo</h1></div>"
    for cat in categorias:
        html += f"<h2>{cat}</h2>"
        for _, p in df[df['Categoria'] == cat].iterrows():
            html += f"<div><h3>{p.get('Nome')}</h3><p>{p.get('Descricao')}</p><span>R$ {p.get('Preco')}</span></div>"
    html += "</body></html>"
    return html

# --- INTERFACE ---
st.title("Gestor Alphafest Master")

# Backup
with st.expander("💾 Backup e Segurança"):
    col_b1, col_b2 = st.columns(2)
    col_b1.download_button("📥 Baixar Backup JSON", data=json.dumps(st.session_state.produtos_totais), file_name="backup.json")
    uploaded = col_b2.file_uploader("📤 Carregar Backup", type=['json'])
    if uploaded:
        st.session_state.produtos_totais = json.load(uploaded)
        salvar_catalogo(st.session_state.produtos_totais)
        st.rerun()

# Edição ou Adição
if st.session_state.edit_index is not None:
    idx = st.session_state.edit_index
    item = st.session_state.produtos_totais[idx]
    st.subheader(f"✏️ Editando: {item['Nome']}")
    c_e1, c_e2 = st.columns(2)
    new_cat = c_e1.text_input("Categoria", value=item['Categoria'])
    new_nome = c_e1.text_input("Nome", value=item['Nome'])
    new_desc = c_e2.text_area("Descrição", value=item['Descricao'])
    new_preco = c_e2.text_input("Preço", value=item['Preco'])
    new_upload = c_e2.file_uploader("Trocar Foto", type=['jpg', 'png', 'jpeg'])
    
    if st.button("💾 Salvar Alterações"):
        lista_imgs = item['Imagens']
        if new_upload:
            caminho = os.path.join(UPLOAD_DIR, new_upload.name)
            with open(caminho, "wb") as f: f.write(new_upload.getbuffer())
            lista_imgs = [caminho]
        
        st.session_state.produtos_totais[idx] = {"Nome": new_nome, "Categoria": new_cat, "Imagens": lista_imgs, "Descricao": new_desc, "Preco": new_preco}
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

# Listagem Protegida
st.subheader("📦 Produtos Cadastrados")
for i, p in enumerate(st.session_state.produtos_totais):
    with st.container(border=True):
        c_row1, c_row2, c_row3 = st.columns([1, 5, 2])
        imgs = p.get('Imagens', [])
        
        # --- LÓGICA DE EXIBIÇÃO CORRIGIDA PARA LINKS E ARQUIVOS ---
        if imgs and len(imgs) > 0:
            caminho = imgs[0]
            try:
                if caminho.startswith("http"): # É um link da web
                    c_row1.image(caminho, width=80)
                elif os.path.exists(caminho): # É um arquivo local
                    c_row1.image(caminho, width=80)
                else:
                    c_row1.write("📷")
            except:
                c_row1.write("⚠️")
        else:
            c_row1.write("📷")
        
        c_row2.write(f"### {p.get('Nome')}")
        c_row2.write(f"**Preço:** R$ {p.get('Preco')} | **Cat:** {p.get('Categoria')}")
        
        if c_row3.button("✏️ Editar", key=f"e{i}"): st.session_state.edit_index = i; st.rerun()
        if c_row3.button("🗑️ Excluir", key=f"d{i}"): 
            st.session_state.produtos_totais.pop(i)
            salvar_catalogo(st.session_state.produtos_totais)
            st.rerun()
