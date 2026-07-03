import streamlit as st
import pandas as pd

# Configuração da página focada e otimizada para ecrãs de telemóvel
st.set_page_config(page_title="Bolão das Oitavas", page_icon="⚽", layout="centered")

# Estilização CSS para Mobile-First, Avatares Gigantes e ajuste de design
st.markdown("""
<style>
    /* Força o app a manter a largura ideal de um telemóvel */
    .main .block-container {
        max-width: 460px;
        padding-top: 1rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }
    /* Alinhamento e destaque do card de jogo */
    .container-jogo {
        background-color: #f9f9f9;
        border: 1px solid #eee;
        border-radius: 14px;
        padding: 12px;
        margin-bottom: 15px;
        text-align: center;
    }
    /* Avatar gigante na tela de seleção */
    .avatar-grande-display {
        font-size: 85px;
        text-align: center;
        margin-top: -10px;
        margin-bottom: 10px;
    }
    /* Ajustes para abas no telemóvel não quebrarem linha */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-left: 10px;
        padding-right: 10px;
        font-size: 15px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚽ Bolão das Oitavas")

# Super lista de avatares expandida com várias opções
lista_avatares = [
    "⚽", "🏆", "🥇", "😎", "👑", "🔥", "⚡", "🌟", "🎯", "🦁", 
    "🤖", "🧙‍♂️", "🥷", "🦸‍♂️", "🕵️‍♂️", "🧑‍💻", "🦊", "🦅", "🦍", "🐼", 
    "🦁", "🦈", "🐙", "🐉", "🚀", "🎮", "🥋", "🤠", "🤡", "👻", "👽", "😈"
]

# Banco de dados com links diretos para imagens das bandeiras (Garante exibição em 100% dos telemóveis/PCs)
if "jogos" not in st.session_state:
    st.session_state.jogos = {
        "J1": {"time1": "Canadá", "flag1": "https://flagcdn.com/w160/ca.png", "time2": "Marrocos", "flag2": "https://flagcdn.com/w160/ma.png", "gols1": 0, "gols2": 0, "passa": None, "encerrado": False},
        "J2": {"time1": "Brasil", "flag1": "https://flagcdn.com/w160/br.png", "time2": "Noruega", "flag2": "https://flagcdn.com/w160/no.png", "gols1": 0, "gols2": 0, "passa": None, "encerrado": False},
        "J3": {"time1": "Portugal", "flag1": "https://flagcdn.com/w160/pt.png", "time2": "Espanha", "flag2": "https://flagcdn.com/w160/es.png", "gols1": 0, "gols2": 0, "passa": None, "encerrado": False},
        "J4": {"time1": "Paraguai", "flag1": "https://flagcdn.com/w160/py.png", "time2": "França", "flag2": "https://flagcdn.com/w160/fr.png", "gols1": 0, "gols2": 0, "passa": None, "encerrado": False},
        "J5": {"time1": "México", "flag1": "https://flagcdn.com/w160/mx.png", "time2": "Inglaterra", "flag2": "https://flagcdn.com/w160/gb-eng.png", "gols1": 0, "gols2": 0, "passa": None, "encerrado": False},
        "J6": {"time1": "EUA", "flag1": "https://flagcdn.com/w160/us.png", "time2": "Bélgica", "flag2": "https://flagcdn.com/w160/be.png", "gols1": 0, "gols2": 0, "passa": None, "encerrado": False},
    }

if "palpites" not in st.session_state:
    st.session_state.palpites = []

if "usuarios" not in st.session_state:
    st.session_state.usuarios = {}

# Sistema de cálculo de pontos
def calcular_pontos(jogo, palpite):
    p1, p2, p_passa = palpite["p1"], palpite["p2"], palpite["passa"]
    r1, r2, r_passa = jogo["gols1"], jogo["gols2"], jogo["passa"]
    
    if p1 == r1 and p2 == r2:
        if r1 == r2:
            return 5 if p_passa == r_passa else 3
        return 5
    elif (p1 > p2 and r1 > r2) or (p1 < p2 and r1 < r2) or (p1 == p2 and r1 == r2):
        return 2
    return 0

# Abas adaptadas para mobile
aba1, aba2, aba3 = st.tabs(["📊 Ranking", "✍️ Palpitar", "⚙️ Admin"])

# ABA 1: RANKING + GERADOR DE TEXTO FORMATADO PARA WHATSAPP
with aba1:
    st.header("🏆 Classificação Geral")
    
    pontos_totais = {}
    for p in st.session_state.palpites:
        nome = p["nome"]
        pontos_totais[nome] = pontos_totais.get(nome, 0)
        jogo = st.session_state.jogos[p["jogo"]]
        if jogo["encerrado"]:
            pontos_totais[nome] += calcular_pontos(jogo, p)
            
    if pontos_totais:
        dados_ranking = []
        for n, pts in pontos_totais.items():
            avatar = st.session_state.usuarios.get(n, "👤")
            dados_ranking.append({"Participante": f"{avatar} {n}", "Pontos": pts, "p_nome": n, "p_avatar": avatar})
            
        df_ranking = pd.DataFrame(dados_ranking).sort_values(by="Pontos", ascending=False).reset_index(drop=True)
        df_ranking.index = df_ranking.index + 1
        
        st.dataframe(df_ranking[["Participante", "Pontos"]], use_container_width=True)
        
        # --- BLOCO FORMATADOR WHATSAPP ---
        st.divider()
        st.subheader("📲 Enviar para o WhatsApp")
        st.caption("Toque e copie o texto abaixo para enviar para a galera:")
        
        texto_whatsapp = "🏆 *CLASSIFICAÇÃO DO BOLÃO* 🏆\n\n"
        for idx, row in df_ranking.iterrows():
            texto_whatsapp += f"{idx}º {row['p_avatar']} *{row['p_nome']}* — {row['Pontos']} pts\n"
        texto_whatsapp += "\n⚽ _Faça seus palpites pelo link do nosso sistema!_"
        
        st.code(texto_whatsapp, language="text")
    else:
        st.info("Aguardando o encerramento das partidas para computar os pontos!")

# ABA 2: ÁREA DO PARTICIPANTE (PALPITES COM BANDEIRAS REAIS)
with aba2:
    st.header("✍️ Dar Palpite")
    
    nome_usuario = st.text_input("Seu Nome/Apelido:", key="user_nome").strip().title()
    
    if nome_usuario:
        avatar_atual = st.session_state.usuarios.get(nome_usuario, lista_avatares[0])
        avatar_escolhido = st.selectbox("Escolha seu Avatar:", lista_avatares, index=lista_avatares.index(avatar_atual))
        st.session_state.usuarios[nome_usuario] = avatar_escolhido
        
        # Exibe o Avatar selecionado bem grande
        st.markdown(f'<div class="avatar-grande-display">{avatar_escolhido}</div>', unsafe_allow_html=True)
        st.divider()
        
        # Listagem das partidas
        for id_jogo, j in st.session_state.jogos.items():
            if j["encerrado"]:
                continue
                
            st.markdown(f'<h5>{j["time1"]} x {j["time2"]}</h5>', unsafe_allow_html=True)
            
            # Colunas com as imagens das bandeiras e nomes abaixo
            col_t1, col_vs, col_t2 = st.columns([2, 1, 2])
            with col_t1:
                st.image(j["flag1"], width=75)
            with col_vs:
                st.markdown("<h2 style='text-align: center; margin-top: 5px;'>VS</h2>", unsafe_allow_html=True)
            with col_t2:
                st.image(j["flag2"], width=75)
                
            # Inputs dos placares lado a lado
            c1, c2 = st.columns(2)
            with c1:
                p1 = st.number_input(f"Gols {j['time1']}", min_value=0, step=1, key=f"p1_{id_jogo}_{nome_usuario}")
            with c2:
                p2 = st.number_input(f"Gols {j['time2']}", min_value=0, step=1, key=f"p2_{id_jogo}_{nome_usuario}")
                
            # Desempate por pênalti se houver empate nos campos de texto
            passa = None
            if p1 == p2:
                st.caption("Jogo empatado! Quem avança nos Pênaltis?")
                passa = st.radio("Classifica:", [j['time1'], j['time2']], horizontal=True, key=f"passa_{id_jogo}_{nome_usuario}")
                
            if st.button("Gravar Palpite", key=f"save_{id_jogo}"):
                st.session_state.palpites = [p for p in st.session_state.palpites if not (p["nome"] == nome_usuario and p["jogo"] == id_jogo)]
                st.session_state.palpites.append({"nome": nome_usuario, "jogo": id_jogo, "p1": p1, "p2": p2, "passa": passa})
                st.success("Palpite salvo com sucesso!")
            st.divider()
    else:
        st.info("Por favor, digite o seu nome acima para exibir as partidas.")

# ABA 3: ADMINISTRAÇÃO E RESULTADOS FINAIS
with aba3:
    st.header("⚙️ Painel do Administrador")
    st.write("Digite os resultados finais reais para rodar a apuração do bolão.")
    
    for id_jogo, j in st.session_state.jogos.items():
        st.markdown(f"### {j['time1']} x {j['time2']}")
        
        c1, c2 = st.columns(2)
        with c1:
            g1 = st.number_input(f"Gols Oficiais {j['time1']}", min_value=0, step=1, value=j["gols1"], key=f"adm_g1_{id_jogo}")
        with c2:
            g2 = st.number_input(f"Gols Oficiais {j['time2']}", min_value=0, step=1, value=j["gols2"], key=f"adm_g2_{id_jogo}")
            
        passa_real = None
        if g1 == g2:
            st.caption("Empate no resultado oficial! Quem passou nos pênaltis?")
            passa_real = st.radio("Vencedor nos Pênaltis:", [j['time1'], j['time2']], horizontal=True, key=f"adm_passa_{id_jogo}")
            
        encerrar = st.checkbox("Encerrar jogo e calcular pontuações", value=j["encerrado"], key=f"adm_enc_{id_jogo}")
        
        if st.button("Lançar Placar Final", key=f"adm_btn_{id_jogo}"):
            st.session_state.jogos[id_jogo]["gols1"] = g1
            st.session_state.jogos[id_jogo]["gols2"] = g2
            st.session_state.jogos[id_jogo]["passa"] = passa_real
            st.session_state.jogos[id_jogo]["encerrado"] = encerrar
            st.success("Resultado oficial computado e Ranking atualizado!")
        st.divider()
