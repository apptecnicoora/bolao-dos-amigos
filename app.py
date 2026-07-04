import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuração mobile-first
st.set_page_config(page_title="Bolão das Oitavas", page_icon="⚽", layout="centered")

st.markdown("""
<style>
    .main .block-container { max-width: 460px; padding-top: 1rem; padding-left: 0.8rem; padding-right: 0.8rem; }
    .avatar-grande-display { font-size: 85px; text-align: center; margin-top: -10px; margin-bottom: 10px; }
    .stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("⚽ Bolão das Oitavas")

lista_avatares = [
    "⚽", "🏆", "🥇", "😎", "👑", "🔥", "⚡", "🌟", "🎯", "🦁", 
    "🤖", "🧙‍♂️", "🥷", "🦸‍♂️", "🕵️‍♂️", "🧑‍💻", "🦊", "🦅", "🦍", "🐼", 
    "🦈", "🐙", "🐉", "🚀", "🎮", "🥋", "🤠", "🤡", "👻", "👽", "😈"
]

# Inicializar Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Função para ler dados com segurança contra tabelas vazias
def ler_aba(nome_aba, colunas_padrao):
    try:
        df = conn.read(worksheet=nome_aba, ttl=0)
        if df.empty:
            return pd.DataFrame(columns=colunas_padrao)
        return df
    except:
        return pd.DataFrame(columns=colunas_padrao)

# Carregar dados da Planilha em tempo real
df_jogos_sheet = ler_aba("Jogos", ["id", "time1", "flag1", "time2", "flag2", "gols1", "gols2", "passa", "encerrado"])
df_palpites = ler_aba("Palpites", ["nome", "jogo", "p1", "p2", "passa"])
df_usuarios = ler_aba("Usuarios", ["nome", "avatar"])

# Se os jogos não estiverem na planilha ainda, registar a estrutura inicial
if df_jogos_sheet.empty:
    jogos_iniciais = [
        {"id": "J1", "time1": "Canadá", "flag1": "https://flagcdn.com/w160/ca.png", "time2": "Marrocos", "flag2": "https://flagcdn.com/w160/ma.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não"},
        {"id": "J2", "time1": "Brasil", "flag1": "https://flagcdn.com/w160/br.png", "time2": "Noruega", "flag2": "https://flagcdn.com/w160/no.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não"},
        {"id": "J3", "time1": "Portugal", "flag1": "https://flagcdn.com/w160/pt.png", "time2": "Espanha", "flag2": "https://flagcdn.com/w160/es.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não"},
        {"id": "J4", "time1": "Paraguai", "flag1": "https://flagcdn.com/w160/py.png", "time2": "França", "flag2": "https://flagcdn.com/w160/fr.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não"},
        {"id": "J5", "time1": "México", "flag1": "https://flagcdn.com/w160/mx.png", "time2": "Inglaterra", "flag2": "https://flagcdn.com/w160/gb-eng.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não"},
        {"id": "J6", "time1": "EUA", "flag1": "https://flagcdn.com/w160/us.png", "time2": "Bélgica", "flag2": "https://flagcdn.com/w160/be.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não"},
    ]
    df_jogos_sheet = pd.DataFrame(jogos_iniciais)
    conn.update(worksheet="Jogos", data=df_jogos_sheet)

# Construir dicionário local para renderizar as partidas de forma simples
dict_jogos = {}
for _, row in df_jogos_sheet.iterrows():
    dict_jogos[row["id"]] = {
        "time1": row["time1"], "flag1": row["flag1"],
        "time2": row["time2"], "flag2": row["flag2"],
        "gols1": int(row["gols1"]), "gols2": int(row["gols2"]),
        "passa": row["passa"], "encerrado": str(row["encerrado"]) == "Sim"
    }

# Lógica de cálculo de pontuação
def calcular_pontos(jogo, palpite):
    p1, p2, p_passa = int(palpite["p1"]), int(palpite["p2"]), palpite["passa"]
    r1, r2, r_passa = jogo["gols1"], jogo["gols2"], jogo["passa"]
    if p1 == r1 and p2 == r2:
        if r1 == r2: return 5 if p_passa == r_passa else 3
        return 5
    elif (p1 > p2 and r1 > r2) or (p1 < p2 and r1 < r2) or (p1 == p2 and r1 == r2):
        return 2
    return 0

aba1, aba2, aba3 = st.tabs(["📊 Ranking", "✍️ Palpitar", "⚙️ Admin"])

# ABA 1: RANKING & WHATSAPP
with aba1:
    st.header("🏆 Classificação Geral")
    pontos_totais = {}
    
    for _, p in df_palpites.iterrows():
        nome = p["nome"]
        pontos_totais[nome] = pontos_totais.get(nome, 0)
        jogo = dict_jogos.get(p["jogo"])
        if juego and jogo["encerrado"]:
            pontos_totais[nome] += calcular_pontos(jogo, p)
            
    if pontos_totais:
        dados_ranking = []
        for n, pts in pontos_totais.items():
            user_row = df_usuarios[df_usuarios["nome"] == n]
            avatar = user_row["avatar"].values[0] if not user_row.empty else "👤"
            dados_ranking.append({"Participante": f"{avatar} {n}", "Pontos": pts, "p_nome": n, "p_avatar": avatar})
            
        df_ranking = pd.DataFrame(dados_ranking).sort_values(by="Pontos", ascending=False).reset_index(drop=True)
        df_ranking.index = df_ranking.index + 1
        st.dataframe(df_ranking[["Participante", "Pontos"]], use_container_width=True)
        
        st.divider()
        st.subheader("📲 Enviar para o WhatsApp")
        texto_whatsapp = "🏆 *CLASSIFICAÇÃO DO BOLÃO* 🏆\n\n"
        for idx, row in df_ranking.iterrows():
            texto_whatsapp += f"{idx}º {row['p_avatar']} *{row['p_nome']}* — {row['Pontos']} pts\n"
        st.code(texto_whatsapp, language="text")
    else:
        st.info("Aguardando resultados para calcular a tabela!")

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
        elif avatar_atual != avatar_escolhido:
            df_usuarios.loc[df_usuarios["nome"] == nome_usuario, "avatar"] = avatar_escolhido
            conn.update(worksheet="Usuarios", data=df_usuarios)
            
        st.markdown(f'<div class="avatar-grande-display">{avatar_escolhido}</div>', unsafe_allow_html=True)
        st.divider()
        
        for id_jogo, j in dict_jogos.items():
            if j["encerrado"]: continue
            
            st.markdown(f'<h5>{j["time1"]} x {j["time2"]}</h5>', unsafe_allow_html=True)
            col_t1, col_vs, col_t2 = st.columns([2, 1, 2])
            with col_t1: st.image(j["flag1"], width=75)
            with col_vs: st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
            with col_t2: st.image(j["flag2"], width=75)
                
            c1, c2 = st.columns(2)
            with c1: p1 = st.number_input(f"Gols {j['time1']}", min_value=0, step=1, key=f"p1_{id_jogo}_{nome_usuario}")
            with c2: p2 = st.number_input(f"Gols {j['time2']}", min_value=0, step=1, key=f"p2_{id_jogo}_{nome_usuario}")
                
            passa = ""
            if p1 == p2:
                st.caption("Empate! Quem avança nos Pênaltis?")
                passa = st.radio("Classifica:", [j['time1'], j['time2']], horizontal=True, key=f"passa_{id_jogo}_{nome_usuario}")
                
            if st.button("Gravar Palpite", key=f"save_{id_jogo}"):
                df_palpites = df_palpites[~((df_palpites["nome"] == nome_usuario) & (df_palpites["jogo"] == id_jogo))]
                novo_p = pd.DataFrame([{"nome": nome_usuario, "jogo": id_jogo, "p1": p1, "p2": p2, "passa": passa}])
                df_palpites = pd.concat([df_palpites, novo_p], ignore_index=True)
                conn.update(worksheet="Palpites", data=df_palpites)
                st.success("Gravado com sucesso no Google Sheets!")
            st.divider()
    else:
        st.info("Digite o seu nome para exibir os confrontos.")

# ABA 3: ADMIN
with aba3:
    st.header("⚙️ Painel Administrador")
    for id_jogo, j in dict_jogos.items():
        st.markdown(f"### {j['time1']} x {j['time2']}")
        c1, c2 = st.columns(2)
        with c1: g1 = st.number_input(f"Gols Reais {j['time1']}", min_value=0, step=1, value=j["gols1"], key=f"adm_g1_{id_jogo}")
        with c2: g2 = st.number_input(f"Gols Reais {j['time2']}", min_value=0, step=1, value=j["gols2"], key=f"adm_g2_{id_jogo}")
            
        passa_real = ""
        if g1 == g2:
            passa_real = st.radio("Vencedor nos Pênaltis:", [j['time1'], j['time2']], horizontal=True, key=f"adm_passa_{id_jogo}")
            
        encerrar = st.checkbox("Encerrar jogo", value=j["encerrado"], key=f"adm_enc_{id_jogo}")
        
        if st.button("Lançar Placar Oficial", key=f"adm_btn_{id_jogo}"):
            df_jogos_sheet.loc[df_jogos_sheet["id"] == id_jogo, ["gols1", "gols2", "passa", "encerrado"]] = [g1, g2, passa_real, "Sim" if encerrar else "Não"]
            conn.update(worksheet="Jogos", data=df_jogos_sheet)
            st.success("Planilha atualizada e pontos consolidados!")
        st.divider()
