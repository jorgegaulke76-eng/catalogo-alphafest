ALPHAFEST MANAGER 3.0 ESTÁVEL
================================

O sistema funciona em computador e celular e usa somente serviços com plano gratuito.

1) PREPARAR O SUPABASE
----------------------
1. Entre no projeto Alphafest no Supabase.
2. No menu esquerdo, abra SQL Editor.
3. Clique em New query.
4. Abra o arquivo supabase_setup.sql deste pacote.
5. Copie todo o conteúdo, cole no SQL Editor e clique em Run.
6. Deve aparecer a mensagem de execução concluída.

2) CONFIGURAR O STREAMLIT CLOUD
-------------------------------
1. Abra o aplicativo no Streamlit Cloud.
2. Clique em Manage app.
3. Abra Settings > Secrets.
4. Cole exatamente:

SUPABASE_URL = "https://guejrwlblcxptzlobhit.supabase.co"
SUPABASE_KEY = "COLE_AQUI_SUA_CHAVE_SB_PUBLISHABLE"

5. Clique em Save.
6. Reinicie o aplicativo.

IMPORTANTE: não coloque o arquivo secrets.toml verdadeiro no GitHub.
A chave publishable deve ser configurada no painel Secrets do Streamlit.

3) ATUALIZAR O GITHUB
---------------------
1. Faça backup do repositório atual.
2. No GitHub, envie todos os arquivos desta pasta.
3. O arquivo principal deve se chamar app.py.
4. Mantenha logo.png, historico_orcamentos.json e catalogo_db.json.
5. Confirme o Commit changes.
6. Aguarde o Streamlit atualizar.

4) PRIMEIRO ACESSO
------------------
No primeiro acesso, se o banco estiver vazio, o sistema importa automaticamente:
- historico_orcamentos.json
- catalogo_db.json

Depois disso, alterações feitas no celular ou computador ficam no Supabase e aparecem
para todos os dispositivos.

5) IMAGENS DO CATÁLOGO
----------------------
Novas imagens enviadas pelo painel são guardadas no bucket público catalogo do Supabase.
Links externos existentes continuam funcionando.

6) BACKUP
---------
O botão BAIXAR BACKUP continua disponível. Faça backups periódicos, mesmo usando banco online.

7) MODO DE SEGURANÇA
--------------------
Caso o Supabase fique temporariamente indisponível, o sistema tenta usar a cópia JSON local.
Na barra lateral aparece o estado da conexão.
