import streamlit as st
import pandas as pd
import requests
import json
import os
from groq import Groq

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Gestor Alphafest Master", layout="wide")
# Certifique-se de que a chave da API está configurada nos segredos do Streamlit
try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Chave da API Groq não encontrada nos secrets.")
    groq_client = None

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
if "preco_calc" not in st.session_state:
    st.session_state.preco_calc = 0.0

# --- FUNÇÃO DE SEGURANÇA PARA IMAGENS ---
def get_lista_imagens(p):
    """Garante que sempre retorna uma lista de imagens válida."""
    imgs = p.get('Imagens')
    if isinstance(imgs, list):
        return imgs
    return [] # Se não for lista, retorna lista vazia para não quebrar o HTML

# --- GERAÇÃO DO HTML ---
def gerar_html_master(lista):
    html = """
    <html><head><style>
        body { font-family: Arial; padding: 20px; }
        .card { display: flex; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; align-items: center; }
        .galeria { display: flex; gap: 10px; margin-right: 20px; flex-wrap: wrap; }
        .galeria img { width: 100px; height: 100px; object-fit: cover; cursor: pointer; }
        .preco { font-weight: bold; color: #2e7d32; font-size: 1.2em; margin-top: 10px; display: block; }
        .menu { background: #f9f9f9; padding: 15px; border: 1px solid #ddd; margin-bottom: 20px; }
    </style></head><body>
    <center><h1>CATÁLOGO MASTER - ALPHAFEST ITATIBA</h1></center>
    """
    if not lista: return html + "</body></html>"
    
    df = pd.DataFrame(lista)
    html += "<div class='menu'><h3>Categorias:</h3><ul>"
    for cat in df['Categoria'].unique():
        html += f"<li><a href='#{cat}'>{cat}</a></li>"
    html += "</ul></div>"
    
    for cat in df['Categoria'].unique():
        html += f"<h2 id='{cat}'>📁 {cat}</h2>"
        for _, p in df[df['Categoria']==cat].iterrows():
            # AQUI ESTÁ A CORREÇÃO: Usamos nossa função de segurança
            imgs = get_lista_imagens(p)
            preco = p.get('Preco', 'Consulte')
            
            html += f"<div class='card'><div class='galeria'>"
            for img in imgs:
                html += f"<img src='{img}'>"
            html += f"</div><div><h3>{p.get('Nome', 'Produto')}</h3><p>{p.get('Descricao', '')}</p><span class='preco'>R$ {preco}</span></div></div>"
    return html + "</body></html>"

# --- INTERFACE ---
st.title("📦 Gestor de Catálogo Master")
tab1, tab2 = st.tabs(["➕ Adicionar/Listar Produtos", "🧮 Precificador 3D"])

with tab1:
    with st.expander("➕ Adicionar Novo Produto", expanded=True):
        col1, col2 = st.columns(2)
        cat = col1.text_input("Categoria", "Geral")
        nome = col1.text_input("Nome do Produto")
        links_fotos = col1.text_area("URLs das Fotos (uma por linha):")
        preco_venda = col2.text_input("Preço de Venda (R$)", value=str(st.session_state.preco_calc))
        
        tema = col2.text_input("Tema/Ocasião")
        cor = col2.text_input("Cor/Material")
        
        if st.button("Adicionar ao Master"):
            lista_imgs = [url.strip() for url in links_fotos.split('\n') if url.strip()]
            novo_item = {
                "Nome": nome, 
                "Categoria": cat, 
                "Imagens": lista_imgs, 
                "Descricao": f"Tema: {tema} | Material: {cor}", 
                "Preco": preco_venda
            }
            st.session_state.produtos_totais.append(novo_item)
            salvar_catalogo(st.session_state.produtos_totais)
            st.success("Produto adicionado!")
            st.rerun()

    st.write("---")
    for i, p in enumerate(st.session_state.produtos_totais):
        c1, c2 = st.columns([1, 4])
        # Segurança também na visualização do painel
        imgs = get_lista_imagens(p)
        if imgs: c1.image(imgs[0], width=100)
        c2.write(f"**{p.get('Nome', 'Sem nome')}** - R$ {p.get('Preco', '0')}")
        if c2.button("Excluir", key=f"del_{i}"):
            st.session_state.produtos_totais.pop(i)
            salvar_catalogo(st.session_state.produtos_totais)
            st.rerun()

with tab2:
    st.subheader("Calculadora de Preço")
    peso = st.number_input("Peso (g)", value=0.0)
    preco_r = st.number_input("Preço Rolo (R$)", value=100.0)
    hr = st.number_input("Horas", value=0.0)
    margem = st.number_input("Margem (%)", value=100.0)
    
    custo = ((peso/1000)*preco_r) + (hr*30) + 5.0
    preco_calc = custo * (1 + (margem/100))
    st.metric("Sugestão", f"R$ {preco_calc:.2f}")
    if st.button("Usar este valor no Cadastro"):
        st.session_state.preco_calc = f"{preco_calc:.2f}"
        st.success("Valor copiado! Vá na aba 'Adicionar' e ele estará lá.")

st.download_button("🖨️ BAIXAR CATÁLOGO MASTER (HTML)", gerar_html_master(st.session_state.produtos_totais), "catalogo_master.html", "text/html")
