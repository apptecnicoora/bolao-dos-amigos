import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import random
import base64
import os

# Configuração mobile-first
st.set_page_config(page_title="Bolão das Oitavas", page_icon="⚽", layout="centered")

# --- CSS CUSTOMIZADO: TEMA ESCURO COM NEON BRASIL ---
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
    
    [data-testid="stForm"], .stExpander {
        background-color: #161a22 !important;
        border: 2px solid #009B3A !important;
        border-radius: 16px !important;
        box-shadow: 0 0 15px rgba(0, 155, 58, 0.4) !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
    }
    
    .stButton > button {
        background-color: #009B3A !important;
        color: #FFDF00 !important;
        border: 2px solid #FFDF00 !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        width: 100% !important;
        height: 50px !important;
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
    input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
    input[type=number] {
        -moz-appearance: textfield;
        text-align: center !important;
        font-size: 1.3rem !important;
        font-weight: bold !important;
        background-color: #202632 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    
    .avatar-grande-display { font-size: 85px; text-align: center; margin-top: -10px; margin-bottom: 10px; }
    
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

    .player-draw-box {
        background: linear-gradient(145deg, #1f242e, #161a22);
        border: 2px solid #FFDF00;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 0 15px rgba(255, 223, 0, 0.2);
    }
    
    .imagem-jogador {
        border-radius: 12px;
        border: 2px solid #009B3A;
        margin-top: 15px;
        width: 100%;
        box-shadow: 0 0 15px rgba(0, 155, 58, 0.4);
    }

    .imagem-topo-app {
        border-radius: 15px;
        border: 3px solid #009B3A;
        box-shadow: 0 0 20px rgba(0, 155, 58, 0.6);
        margin-bottom: 25px;
        width: 100%;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚽ BOLÃO ONLINE DAS OITAVAS")
st.markdown("Confira os horários dos jogos, dê seus palpites e acompanhe o Ranking!")

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

# --- FUNÇÃO PARA LER A IMAGEM LOCAL DO GITHUB ---
def obter_imagem_local_base64(caminho_arquivo):
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, "rb") as arquivo_imagem:
            return base64.b64encode(arquivo_imagem.read()).decode()
    return None

# --- INICIALIZAR CONEXÃO E LER DADOS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_aba(nome_aba, colunas_padrao):
    try:
        df = conn.read(worksheet=nome_aba, ttl=10)
        if df.empty:
            return pd.DataFrame(columns=colunas_padrao)
        return df
    except:
        return pd.DataFrame(columns=colunas_padrao)

df_jogos_sheet = ler_aba("Jogos", ["id", "time1", "flag1", "time2", "flag2", "gols1", "gols2", "passa", "encerrado", "horário"])

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

# --- REGRA HARDCORE: APENAS PLACAR EXATO GANHA 5 PONTOS ---
def calcular_pontos(jogo, palpite):
    try:
        p1 = int(palpite["p1"])
        p2 = int(palpite["p2"])
        r1 = jogo["gols1"]
        r2 = jogo["gols2"]
        
        if p1 == r1 and p2 == r2:
            return 5
            
        return 0
    except:
        return 0

aba1, aba2, aba3 = st.tabs(["📊 Ranking", "✍️ Palpitar", "⚙️ Admin"])

# --- ABA 1: RANKING E SORTEIO DO JOGADOR ---
with aba1:
    
    # IMAGEM FIXA DO RONALDINHO NO TOPO PUXANDO DO SEU GITHUB LOCAL
    imagem_base64 = obter_imagem_local_base64("ronaldinho.gif")
    
    if imagem_base64:
        st.markdown(f"""
        <div style='text-align: center;'>
            <img src="data:image/gif;base64,{imagem_base64}" class="imagem-topo-app" alt="Ronaldinho Dançando">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ O arquivo 'ronaldinho.gif' não foi encontrado. Verifique se o arquivo está na mesma pasta do código no GitHub.")
    
    # CAIXA DE SORTEIO VISÍVEL NO TOPO COM LINKS SEGUROS DA WIKIPEDIA
    st.markdown("<div class='player-draw-box'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #ffffff; margin-top: 0;'>🎲 Qual Jogador Você é Hoje?</h3>", unsafe_allow_html=True)
    st.write("Aperte o botão para descobrir sua energia para os palpites!")
    
    if st.button("SORTEAR MEU JOGADOR", use_container_width=True):
        jogadores = [
            ("Ronaldinho Gaúcho (O Bruxo)", "https://upload.wikimedia.org/wikipedia/commons/e/e0/Ronaldinho_11022007.jpg"),
            ("Cássio (O Paredão)", "https://upload.wikimedia.org/wikipedia/commons/8/8e/C%C3%A1ssio_Ramos_2018.jpg"),
            ("Neymar Jr (Ousadia e Alegria)", "https://upload.wikimedia.org/wikipedia/commons/b/bb/Neymar_Jr._with_Al_Hilal%2C_3_October_2023_-_03_%28cropped%29.jpg"),
            ("Cristiano Ronaldo (A Máquina)", "https://upload.wikimedia.org/wikipedia/commons/d/d7/Cristiano_Ronaldo_playing_for_Al_Nassr_FC_against_Persepolis%2C_September_2023_%28cropped%29.jpg"),
            ("Lionel Messi (O Gênio)", "https://upload.wikimedia.org/wikipedia/commons/b/b4/Lionel-Messi-Argentina-2022-FIFA-World-Cup_%28cropped%29.jpg")
        ]
        nome_sorteado, imagem_sorteada = random.choice(jogadores)
        
        st.success(f"Você tirou: **{nome_sorteado}**")
        st.markdown(f"<img src='{imagem_sorteada}' class='imagem-jogador'>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

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
        st.subheader("📲 Enviar Placar para o WhatsApp")
        texto_whatsapp = "🏆 *CLASSIFICAÇÃO DO BOLÃO (MODO HARDCORE)* 🏆\n\n"
        for idx, row in df_ranking.iterrows():
            texto_whatsapp += f"{idx+1}º {row['p_avatar']} *{row['p_nome']}* — {row['Pontos']} pts\n"
        st.code(texto_whatsapp, language="text")

        st.divider()
        st.subheader("👀 Espiar Adversários")
        st.caption("Clique no nome do participante abaixo para ver os palpites dele.")
        
        usuarios_com_palpite = df_palpites["nome"].unique()
        for nome_participante in usuarios_com_palpite:
            user_info = df_usuarios[df_usuarios["nome"] == nome_participante]
            avatar_part = user_info["avatar"].values[0] if not user_info.empty else "👤"
            
            with st.expander(f"{avatar_part} {nome_participante}"):
                palpites_do_cara = df_palpites[df_palpites["nome"] == nome_participante]
                
                texto_palpites = f"📝 *PALPITES - {nome_participante}* 📝\n\n"
                
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

# --- ABA 2: DAR PALPITE ---
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

# --- ABA 3: ADMIN ---
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
