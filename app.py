import streamlit as st
import pandas as pd
import io
import requests
import base64
from groq import Groq
from bs4 import BeautifulSoup

# --- CONFIGURAÇÕES ---
# O Streamlit vai ler a chave do seu painel 'Secrets'
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- INICIALIZAÇÃO DE ESTADO ---
if "produtos_totais" not in st.session_state: st.session_state.produtos_totais = []

# --- FUNÇÕES ---

def obter_imagem_como_base64(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if 'text/html' in response.headers.get('Content-Type', ''):
            soup = BeautifulSoup(response.content, 'html.parser')
            meta = soup.find("meta", property="og:image")
            if meta and meta.get("content"): return obter_imagem_como_base64(meta["content"])
            return "https://i.ibb.co/kV0jyTfK/logo.png"
        b64 = base64.b64encode(response.content).decode()
        return f"data:image/jpeg;base64,{b64}"
    except: return "https://i.ibb.co/kV0jyTfK/logo.png"

def image_to_base64(uploaded_file):
    return f"data:image/jpeg;base64,{base64.b64encode(uploaded_file.getvalue()).decode()}"

def gerar_anuncio_ia(nome_produto, contexto_manual=""):
    prompt = f"Produto: {nome_produto}. Detalhes: {contexto_manual}. Escreva uma descrição curta, profissional e vendedora."
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": "Você é um especialista de marketing da ALPHAFEST ITATIBA. Seja direto, profissional e vendedor."},
                      {"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except: return f"{nome_produto} de alta qualidade."

def gerar_html_catalogo(lista_produtos):
    df = pd.DataFrame(lista_produtos)
    categorias = df['Categoria'].unique()
    capa_links = "".join([f"<li><a href='#{c.replace(' ', '_')}'>{c}</a></li>" for c in categorias])
    
    html = f"""<!DOCTYPE html><html><head><style>
        body{{font-family: sans-serif; padding: 20px; background-color: #f9f9f9;}} 
        .capa{{background: white; padding: 20px; border-radius: 10px; margin-bottom: 30px; text-align: center;}}
        .categoria-section{{page-break-before: always; margin-top: 40px;}}
        .card{{display: flex; align-items: center; background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}} 
        img{{width: 100px; height: 100px; object-fit: cover; cursor: pointer;}}
    </style></head><body>
    <h1>CATÁLOGO MASTER - ALPHAFEST</h1>
    <div class="capa"><h3>Menu de Categorias:</h3><ul>{capa_links}</ul></div>"""
    
    for categoria, group in df.groupby('Categoria'):
        html += f"<div id='{categoria.replace(' ', '_')}' class='categoria-section'><h2>📂 {categoria}</h2>"
        for _, p in group.iterrows():
            html += f"""<div class="card"><img src="{p['Imagem']}"><div><h3>{p['Nome_Exibicao']}</h3><p>{p['Descrição']}</p></div></div>"""
        html += "</div>"
    return html + "</body></html>"

# --- INTERFACE ---
st.set_page_config(page_title="Catálogo Master", layout="wide")
st.title("📦 ALPHAFEST - Gestor de Catálogo Master")

c1, c2 = st.columns(2)
with c1:
    cat_link = st.text_input("Categoria:", "Outros")
    link = st.text_area("Cole a URL da Imagem:")
    nome_p = st.text_input("Nome do Produto:")
    if st.button("Adicionar Link"):
        st.session_state.produtos_totais.append({"Nome_Exibicao": nome_p, "Imagem": obter_imagem_como_base64(link), "Descrição": gerar_anuncio_ia(nome_p), "Categoria": cat_link})
        st.rerun()

with c2:
    foto = st.file_uploader("Upload foto", type=['jpg', 'png'])
    if st.button("Adicionar Foto") and foto:
        st.session_state.produtos_totais.append({"Nome_Exibicao": "Produto", "Imagem": image_to_base64(foto), "Descrição": "...", "Categoria": cat_link})
        st.rerun()

if st.button("GERAR CATÁLOGO MASTER FINAL"):
    st.download_button("🖨️ Baixar HTML Master", gerar_html_catalogo(st.session_state.produtos_totais), "catalogo_master.html", "text/html")
