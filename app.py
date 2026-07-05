import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import base64
import os
import random

# Configuração mobile-first
st.set_page_config(page_title="Bolão das Oitavas", page_icon="⚽", layout="centered")

# --- CSS CUSTOMIZADO: TEMA ESCURO COM NEON BRASIL E REMOÇÃO DOS BOTÕES + e - ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117 !important; color: #ffffff !important; }
    h1, h2, h3, h4, h5 { color: #009B3A !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.05); }
    h1, h2, h3, h4, h5, p, span, label, .stMarkdown { color: #ffffff !important; }
    
    .main .block-container { 
        max-width: 480px; 
        padding-top: 1rem; 
        padding-left: 0.8rem; 
        padding-right: 0.8rem; 
    }
    
    [data-testid="stForm"] {
        background-color: #161a22 !important;
        border: 2px solid #009B3A !important;
        border-radius: 16px !important;
        box-shadow: 0 0 15px rgba(0, 155, 58, 0.6), inset 0 0 10px rgba(255, 223, 0, 0.2) !important;
        padding: 20px !important;
        margin-bottom: 25px !important;
    }
    
    .stButton > button {
        background-color: #009B3A !important;
        color: #FFDF00 !important;
        border: 2px solid #FFDF00 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        box-shadow: 0 0 10px rgba(0, 155, 58, 0.5) !important;
        transition: 0.3s !important;
    }
    .stButton > button:hover {
        background-color: #FFDF00 !important;
        color: #009B3A !important;
        border: 2px solid #009B3A !important;
        box-shadow: 0 0 15px rgba(255, 223, 0, 0.8) !important;
    }

    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button { 
        -webkit-appearance: none; 
        margin: 0; 
    }
    input[type=number] {
        -moz-appearance: textfield;
        text-align: center !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        background-color: #202632 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
    }
    
    .avatar-grande-display { font-size: 85px; text-align: center; margin-top: -10px; margin-bottom: 10px; }
    .stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: bold; color: #8b949e; }
    .stTabs [aria-selected="true"] { color: #009B3A !important; border-bottom-color: #009B3A !important; }
    
    .top1-glow {
        background: linear-gradient(145deg, #1f242e, #161a22);
        border: 2px solid #FFDF00;
        box-shadow: 0 0 20px 5px rgba(255, 223, 0, 0.5);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        color: white;
        text-align: center;
        font-size: 1.2rem;
    }
    
    .ranking-normal {
        background-color: #161a22;
        border-left: 5px solid #009B3A;
        border-top: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
        border-right: 1px solid #30363d;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        color: #ffffff;
    }

    .dancing-ronaldinho {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 100%;
        max-width: 250px;
        height: auto;
        border-radius: 15px;
        border: 3px solid #FFDF00;
        box-shadow: 0 0 25px 5px rgba(0, 155, 58, 0.7);
    }
    
    .gif-sorteio {
        border-radius: 12px;
        border: 2px solid #009B3A;
        width: 100%;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- MINIGAME NA BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("🎲 Qual jogador você é hoje?")
    st.write("Clique abaixo para sortear o seu mood do dia para o bolão!")
    
    if st.button("Sortear Meu Jogador!", type="primary", use_container_width=True):
        gifs_jogadores = [
            ("Ronaldinho (O Bruxo da Festa)", "https://media.giphy.com/media/8cErRl4M1KIiXpW3Fp/giphy.gif"),
            ("Cristiano Ronaldo (A Máquina - SIIUU)", "https://media.giphy.com/media/xT1XGVp95PNYTFg5p6/giphy.gif"),
            ("Messi (O Gênio Calmo)", "https://media.giphy.com/media/TjAcxImn74uo1ODzMi/giphy.gif"),
            ("Neymar (Ousadia e Alegria)", "https://media.giphy.com/media/l41lOugZmGBoQ4M6s/giphy.gif"),
            ("Cássio (O Paredão Frio)", "https://media.tenor.com/tHqX1sR2A7oAAAAC/cassio-corinthians.gif"),
            ("Richarlison (O Pombo)", "https://media.giphy.com/media/wMjd1Xk8dZf5Z91U9m/giphy.gif")
        ]
        jogador_sorteado = random.choice(gifs_jogadores)
        
        st.success(f"**Você tirou:** {jogador_sorteado[0]}")
        st.markdown(f"<img src='{jogador_sorteado[1]}' class='gif-sorteio'>", unsafe_allow_html=True)
    st.divider()
    st.caption("Arraste para o lado para fechar este menu.")


st.title("⚽ BOLÃO ONLINE DAS OITAVAS DE FINAL")
st.markdown("Confira os horários dos jogos, dê seus palpites e acompanhe o Ranking com estilo Neon Brasil!")

# Lista de avatares e cores
lista_avatares = [
    "⚽", "🏆", "🥇", "😎", "👑", "🔥", "⚡", "🌟", "🎯", "🦁", 
    "🤖", "🧙‍♂️", "🥷", "🦸‍♂️", "🕵️‍♂️", "🧑‍💻", "🦊", "🦅", "🦍", "🐼", 
    "🦈", "🐙", "🐉", "🚀", "🎮", "🥋", "🤠", "🤡", "👻", "👽", 
    "😈", "Rex", "🦄", "🐸", "🐷", "🐯", "🐶", "🐺", "🐻", "🦖"
]

cores_paises = {
    "Canadá": "#FF0000", "Marrocos": "#C1272D", "Brasil": "#009B3A", "Noruega": "#BA0C2F",
    "Portugal": "#FF0000", "Espanha": "#AA151B", "Paraguai": "#0038A8", "França": "#002395",
    "México": "#006341", "Inglaterra": "#CF081F", "EUA": "#3C3B6E", "Bélgica": "#ED2939",
    "Argentina": "#43A1D5", "Egito": "#CE1126", "Suíça": "#FF0000", "Colômbia": "#FCD116"
}

bandeiras_emoji = {
    "Canadá": "🇨🇦", "Marrocos": "🇲🇦", "Brasil": "🇧🇷", "Noruega": "🇳🇴",
    "Portugal": "🇵🇹", "Espanha": "🇪🇸", "Paraguai": "🇵🇾", "França": "🇫🇷",
    "México": "🇲🇽", "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "EUA": "🇺🇸", "Bélgica": "🇧🇪",
    "Argentina": "🇦🇷", "Egito": "🇪🇬", "Suíça": "🇨🇭", "Colômbia": "🇨🇴"
}

# Inicializar Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_aba(nome_aba, colunas_padrao):
    try:
        df = conn.read(worksheet=nome_aba, ttl=15)
        if df.empty:
            return pd.DataFrame(columns=colunas_padrao)
        return df
    except:
        return pd.DataFrame(columns=colunas_padrao)

df_jogos_sheet = ler_aba("Jogos", ["id", "time1", "flag1", "time2", "flag2", "gols1", "gols2", "passa", "encerrado", "horário"])

# TRAVAS ANTI-ERRO (KEYERROR E TYPEERROR)
if "horário" not in df_jogos_sheet.columns:
    df_jogos_sheet["horário"] = ""
df_jogos_sheet["passa"] = df_jogos_sheet["passa"].astype(object)
df_jogos_sheet["encerrado"] = df_jogos_sheet["encerrado"].astype(object)

df_palpites = ler_aba("Palpites", ["nome", "jogo", "p1", "p2", "passa"])
df_usuarios = ler_aba("Usuarios", ["nome", "avatar"])

jogos_iniciais = [
    {"id": "J1", "time1": "Canadá", "flag1": "https://flagcdn.com/w160/ca.png", "time2": "Marrocos", "flag2": "https://flagcdn.com/w160/ma.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não", "horário": "Sáb., 04/07 14:00"},
    {"id": "J2", "time1": "Paraguai", "flag1": "https://flagcdn.com/w160/py.png", "time2": "França", "flag2": "https://flagcdn.com/w160/fr.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não", "horário": "Sáb., 04/07 18:00"},
    {"id": "J3", "time1": "Brasil", "flag1": "https://flagcdn.com/w160/br.png", "time2": "Noruega", "flag2": "https://flagcdn.com/w160/no.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não", "horário": "Dom., 05/07 17:00"},
    {"id": "J4", "time1": "México", "flag1": "https://flagcdn.com/w160/mx.png", "time2": "Inglaterra", "flag2": "https://flagcdn.com/w160/gb-eng.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não", "horário": "Dom., 05/07 21:00"},
    {"id": "J5", "time1": "Portugal", "flag1": "https://flagcdn.com/w160/pt.png", "time2": "Espanha", "flag2": "https://flagcdn.com/w160/es.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não", "horário": "Seg., 06/07 16:00"},
    {"id": "J6", "time1": "EUA", "flag1": "https://flagcdn.com/w160/us.png", "time2": "Bélgica", "flag2": "https://flagcdn.com/w160/be.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não", "horário": "Seg., 06/07 21:00"},
    {"id": "J7", "time1": "Argentina", "flag1": "https://flagcdn.com/w160/ar.png", "time2": "Egito", "flag2": "https://flagcdn.com/w160/eg.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não", "horário": "Ter., 07/07 13:00"},
    {"id": "J8", "time1": "Suíça", "flag1": "https://flagcdn.com/w160/ch.png", "time2": "Colômbia", "flag2": "https://flagcdn.com/w160/co.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não", "horário": "Ter., 07/07 17:00"}
]

ids_existentes = df_jogos_sheet["id"].tolist() if not df_jogos_sheet.empty else []
novos_jogos = [j for j in jogos_iniciais if j["id"] not in ids_existentes]
if novos_jogos:
    df_jogos_sheet = pd.concat([df_jogos_sheet, pd.DataFrame(novos_jogos)], ignore_index=True)
    conn.update(worksheet="Jogos", data=df_jogos_sheet)
    st.cache_data.clear()

dict_jogos = {}
for _, row in df_jogos_sheet.iterrows():
    dict_jogos[row["id"]] = {
        "time1": row["time1"], "flag1": row["flag1"],
        "time2": row["time2"], "flag2": row["flag2"],
        "gols1": int(row.get("gols1", 0)) if pd.notna(row.get("gols1", 0)) else 0, 
        "gols2": int(row.get("gols2", 0)) if pd.notna(row.get("gols2", 0)) else 0,
        "passa": row.get("passa", ""), 
        "encerrado": str(row.get("encerrado", "Não")) == "Sim",
        "horário": row.get("horário", "Horário a definir")
    }

# --- LÓGICA DE PONTUAÇÃO IMPLACÁVEL (SÓ PLACAR EXATO GANHA) ---
def calcular_pontos(jogo, palpite):
    try:
        p1, p2 = int(palpite["p1"]), int(palpite["p2"])
        r1, r2 = jogo["gols1"], jogo["gols2"]
        
        # Só ganha 5 pontos se o placar for perfeitamente igual ao resultado
        if p1 == r1 and p2 == r2:
            return 5
            
        return 0
    except:
        return 0

# FUNÇÃO PARA LER A IMAGEM LOCAL
def obter_imagem_local_base64(caminho_arquivo):
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, "rb") as arquivo_imagem:
            return base64.b64encode(arquivo_imagem.read()).decode()
    return None

aba1, aba2, aba3 = st.tabs(["📊 Ranking", "✍️ Palpitar", "⚙️ Admin"])

# ABA 1: RANKING
with aba1:
    # Chama o arquivo local do GitHub (ronaldinho.gif)
    imagem_base64 = obter_imagem_local_base64("ronaldinho.gif")
    
    if imagem_base64:
        st.markdown(f"""
        <div style='text-align: center;'>
            <img src="data:image/gif;base64,{imagem_base64}" class="dancing-ronaldinho" alt="Ronaldinho Dançando">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ O arquivo 'ronaldinho.gif' não foi encontrado. Por favor, suba um GIF com esse nome exato no seu GitHub.")
        
    st.markdown("<br>", unsafe_allow_html=True)

    st.header("🏆 Classificação Geral")
    pontos_totais = {}
    
    for _, p in df_palpites.iterrows():
        nome = p["nome"]
        pontos_totais[nome] = pontos_totais.get(nome, 0)
        jogo = dict_jogos.get(p["jogo"])
        if jogo and jogo["encerrado"]:
            pontos_totais[nome] += calcular_pontos(jogo, p)
            
    if pontos_totais:
        dados_ranking = []
        for n, pts in pontos_totais.items():
            user_row = df_usuarios[df_usuarios["nome"] == n]
            avatar = user_row["avatar"].values[0] if not user_row.empty else "👤"
            dados_ranking.append({"Participante": f"{avatar} {n}", "Pontos": pts, "p_nome": n, "p_avatar": avatar})
            
        df_ranking = pd.DataFrame(dados_ranking).sort_values(by="Pontos", ascending=False).reset_index(drop=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        for idx, row in df_ranking.iterrows():
            pos = idx + 1
            if pos == 1:
                st.markdown(f"<div class='top1-glow'>👑 1º LUGAR<br><span style='font-size: 2rem;'>{row['p_avatar']} <b>{row['p_nome']}</b></span><br>{row['Pontos']} pts</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='ranking-normal'><b>{pos}º</b> {row['p_avatar']} {row['p_nome']} — <b>{row['Pontos']} pts</b></div>", unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📲 Enviar Placar Geral para o WhatsApp")
        texto_whatsapp = "🏆 *CLASSIFICAÇÃO DO BOLÃO* 🏆\n\n"
        for idx, row in df_ranking.iterrows():
            texto_whatsapp += f"{idx+1}º {row['p_avatar']} *{row['p_nome']}* — {row['Pontos']} pts\n"
        st.code(texto_whatsapp, language="text")

        st.divider()
        st.subheader("👀 Ver e Copiar Palpites")
        st.caption("Clique no nome do participante abaixo para ver ou copiar os palpites dele.")
        
        usuarios_com_palpite = df_palpites["nome"].unique()
        for nome_participante in usuarios_com_palpite:
            user_info = df_usuarios[df_usuarios["nome"] == nome_participante]
            avatar_part = user_info["avatar"].values[0] if not user_info.empty else "👤"
            
            with st.expander(f"{avatar_part} {nome_participante}"):
                palpites_do_cara = df_palpites[df_palpites["nome"] == nome_participante]
                
                texto_palpites = f"📝 *PALPITES - OITAVAS* 📝\n"
                texto_palpites += f"👤 *Participante:* {avatar_part} *{nome_participante}*\n\n"
                
                for id_jogo, j in dict_jogos.items():
                    p_jogo = palpites_do_cara[palpites_do_cara["jogo"] == id_jogo]
                    f1 = bandeiras_emoji.get(j["time1"], "⚽")
                    f2 = bandeiras_emoji.get(j["time2"], "⚽")
                    
                    if not p_jogo.empty:
                        val_p1 = int(p_jogo.iloc[0]["p1"])
                        val_p2 = int(p_jogo.iloc[0]["p2"])
                        val_passa = p_jogo.iloc[0]["passa"]
                        
                        texto_palpites += f"{f1} {j['time1']} {val_p1} x {val_p2} {j['time2']} {f2}"
                        if val_p1 == val_p2 and val_passa:
                            texto_palpites += f" (Pênaltis: {val_passa})"
                        texto_palpites += "\n"
                
                st.code(texto_palpites, language="text")
                
    else:
        st.info("Aguardando resultados oficiais para calcular a tabela!")

# ABA 2: PALPITES
with aba2:
    st.header("✍️ Dar Palpite")
    nome_usuario = st.text_input("Seu Nome/Apelido:", key="user_nome").strip().title()
    
    if nome_usuario:
        user_row = df_usuarios[df_usuarios["nome"] == nome_usuario]
        avatar_atual = user_row["avatar"].values[0] if not user_row.empty else lista_avatares[0]
        avatar_escolhido = st.selectbox("Escolha seu Avatar:", lista_avatares, index=lista_avatares.index(avatar_atual))
        
        if user_row.empty:
            nova_linha = pd.DataFrame([{"nome": nome_usuario, "avatar": avatar_escolhido}])
            df_usuarios = pd.concat([df_usuarios, nova_linha], ignore_index=True)
            conn.update(worksheet="Usuarios", data=df_usuarios)
            st.cache_data.clear()
        elif avatar_atual != avatar_escolhido:
            df_usuarios.loc[df_usuarios["nome"] == nome_usuario, "avatar"] = avatar_escolhido
            conn.update(worksheet="Usuarios", data=df_usuarios)
            st.cache_data.clear()
            
        st.markdown(f'<div class="avatar-grande-display">{avatar_escolhido}</div>', unsafe_allow_html=True)
        st.divider()
        
        for id_jogo, j in dict_jogos.items():
            if j["encerrado"]: continue
            
            with st.form(key=f"form_{id_jogo}"):
                st.markdown(f'<h4 style="text-align: center; color: #ffffff !important;">{j["time1"]} x {j["time2"]}</h4>', unsafe_allow_html=True)
                st.markdown(f'<p style="text-align: center; color: #8b949e !important; font-size: 0.9rem; margin-top: -15px;">{j["horário"]}</p>', unsafe_allow_html=True)
                
                cor_t1 = cores_paises.get(j["time1"], "#009B3A")
                cor_t2 = cores_paises.get(j["time2"], "#009B3A")
                
                col_t1, col_vs, col_t2 = st.columns([2, 1, 2])
                with col_t1: 
                    st.markdown(f"<div style='text-align: right;'><img src='{j['flag1']}' width='80' style='border-radius: 8px; box-shadow: 0 0 18px {cor_t1};'></div>", unsafe_allow_html=True)
                with col_vs: 
                    st.markdown("<h3 style='text-align: center; margin-top: 15px;'>VS</h3>", unsafe_allow_html=True)
                with col_t2: 
                    st.markdown(f"<div style='text-align: left;'><img src='{j['flag2']}' width='80' style='border-radius: 8px; box-shadow: 0 0 18px {cor_t2};'></div>", unsafe_allow_html=True)
                    
                c1, c2 = st.columns(2)
                with c1: p1 = st.number_input(f"Gols {j['time1']}", min_value=0, step=1)
                with c2: p2 = st.number_input(f"Gols {j['time2']}", min_value=0, step=1)
                    
                st.caption("Pênaltis (Marque apenas se o seu placar for um empate):")
                opcao_sem_penalti = "Sem Pênaltis (Não empatou)"
                passa = st.selectbox("", [opcao_sem_penalti, j['time1'], j['time2']], label_visibility="collapsed")
                    
                submit_palpite = st.form_submit_button("Gravar Palpite", type="primary", use_container_width=True)
                
                if submit_palpite:
                    if p1 == p2 and passa == opcao_sem_penalti:
                        st.error("⚠️ Você colocou um empate! Escolha quem vence nos pênaltis antes de gravar.")
                    elif p1 != p2 and passa != opcao_sem_penalti:
                        st.error("⚠️ O jogo não empatou. Marque 'Sem Pênaltis' para poder gravar.")
                    else:
                        df_palpites = df_palpites[~((df_palpites["nome"] == nome_usuario) & (df_palpites["jogo"] == id_jogo))]
                        passa_final = passa if passa != opcao_sem_penalti else ""
                        novo_p = pd.DataFrame([{"nome": nome_usuario, "jogo": id_jogo, "p1": p1, "p2": p2, "passa": passa_final}])
                        df_palpites = pd.concat([df_palpites, novo_p], ignore_index=True)
                        
                        conn.update(worksheet="Palpites", data=df_palpites)
                        st.cache_data.clear()
                        st.success("Gravado com sucesso no sistema!")
            st.markdown("<br>", unsafe_allow_html=True)
            
        palpites_usuario = df_palpites[df_palpites["nome"] == nome_usuario]
        if not palpites_usuario.empty:
            st.subheader("📲 Meus Palpites para o WhatsApp")
            
            texto_meus_palpites = f"📝 *MEUS PALPITES - OITAVAS* 📝\n"
            texto_meus_palpites += f"👤 *Participante:* {avatar_escolhido} *{nome_usuario}*\n\n"
            
            for id_jogo, j in dict_jogos.items():
                p_jogo = palpites_usuario[palpites_usuario["jogo"] == id_jogo]
                f1 = bandeiras_emoji.get(j["time1"], "⚽")
                f2 = bandeiras_emoji.get(j["time2"], "⚽")
                if not p_jogo.empty:
                    val_p1 = int(p_jogo.iloc[0]["p1"])
                    val_p2 = int(p_jogo.iloc[0]["p2"])
                    val_passa = p_jogo.iloc[0]["passa"]
                    
                    texto_meus_palpites += f"{f1} {j['time1']} {val_p1} x {val_p2} {j['time2']} {f2}"
                    if val_p1 == val_p2 and val_passa:
                        texto_meus_palpites += f" (Pênaltis: {val_passa})"
                    texto_meus_palpites += "\n"
            
            texto_meus_palpites += "\n👉 *Deixe os seus palpites também pelo link!*"
            st.code(texto_meus_palpites, language="text")
    else:
        st.info("Digite o seu nome para exibir os confrontos.")

# ABA 3: ADMIN
with aba3:
    st.header("⚙️ Painel Administrador")
    
    st.subheader("🗑️ Remover Usuário")
    lista_nomes = df_usuarios["nome"].tolist()
    if lista_nomes:
        usuario_remover = st.selectbox("Selecione um participante para expulsar do bolão:", lista_nomes)
        if st.button("Apagar Usuário e Palpites", type="primary"):
            df_usuarios = df_usuarios[df_usuarios["nome"] != usuario_remover]
            df_palpites = df_palpites[df_palpites["nome"] != usuario_remover]
            conn.update(worksheet="Usuarios", data=df_usuarios)
            conn.update(worksheet="Palpites", data=df_palpites)
            st.cache_data.clear()
            st.success(f"Usuário {usuario_remover} removido com sucesso!")
            st.rerun()
        
    st.divider()
    
    st.subheader("📝 Lançar Resultados Reais")
    for id_jogo, j in dict_jogos.items():
        with st.form(key=f"adm_form_{id_jogo}"):
            st.markdown(f"**{j['time1']} x {j['time2']}**")
            c1, c2 = st.columns(2)
            with c1: g1 = st.number_input(f"Gols {j['time1']}", min_value=0, step=1, value=j["gols1"])
            with c2: g2 = st.number_input(f"Gols {j['time2']}", min_value=0, step=1, value=j["gols2"])
                
            opcao_sem_penalti_adm = "Sem Pênaltis"
            st.caption("Pênaltis:")
            passa_real = st.selectbox("", [opcao_sem_penalti_adm, j['time1'], j['time2']], label_visibility="collapsed")
                
            encerrar = st.checkbox("Encerrar jogo e travar palpites", value=j["encerrado"])
            
            submit_adm = st.form_submit_button("Gravar Placar Oficial", use_container_width=True)
            
            if submit_adm:
                passa_final_adm = passa_real if passa_real != opcao_sem_penalti_adm else ""
                
                df_jogos_sheet.loc[df_jogos_sheet["id"] == id_jogo, "gols1"] = g1
                df_jogos_sheet.loc[df_jogos_sheet["id"] == id_jogo, "gols2"] = g2
                df_jogos_sheet.loc[df_jogos_sheet["id"] == id_jogo, "passa"] = passa_final_adm
                df_jogos_sheet.loc[df_jogos_sheet["id"] == id_jogo, "encerrado"] = "Sim" if encerrar else "Não"
                
                conn.update(worksheet="Jogos", data=df_jogos_sheet)
                st.cache_data.clear()
                st.success("Placar oficial atualizado com sucesso!")
