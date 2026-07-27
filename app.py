import streamlit as st
import pandas as pd
import json
import os

# ... (Mantenha as mesmas funções carregar/salvar/get_imgs) ...

# --- MODO DE VISUALIZAÇÃO ---
# Se o link tiver ?cliente=true, mostra o catálogo. Se não, mostra o gestor.
query_params = st.query_params
is_cliente = query_params.get("cliente") == "true"

if is_cliente:
    # --- VISÃO DO CLIENTE (Link que você envia) ---
    st.set_page_config(page_title="Catálogo Alphafest", layout="wide")
    st.header("Catálogo Alphafest Itatiba")
    lista = carregar_catalogo()
    # (Aqui você coloca o código da exibição do catálogo que criamos antes)
    # ... código para exibir cards organizados por categoria ...
    st.info("Entre em contato conosco para fazer seu pedido!")
else:
    # --- VISÃO DO GESTOR (O que você usa) ---
    st.title("📦 Gestor Alphafest")
    # ... (Todo o seu código de adicionar/editar/excluir produtos) ...
