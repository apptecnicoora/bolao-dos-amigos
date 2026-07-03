import streamlit as st
import pandas as pd

# Configuração da página para tema escuro e título
st.set_page_config(page_title="Bolão das Oitavas", page_icon="⚽", layout="wide", initial_sidebar_state="collapsed")

# Estilo CSS para personalizar os componentes
st.markdown("""
<style>
    .reportview-container { background-color: #1c1c1e; color: white; }
    .stNumberInput input { color: white; background-color: #2c2c2e; border: 1px solid #444; }
    .css-1d391kg { padding: 1rem 3rem 10rem; }
    .css-2trqyj { background-color: #2c2c2e; border-radius: 10px; padding: 15px; margin-bottom: 15px; border: 1px solid #444; }
    .avatar-large { font-size: 5rem; text-align: center; }
    .ranking-user { font-weight: bold; }
    .flag-img { vertical-align: middle; margin-right: 10px; }
    h1, h2, h3 { color: white !important; }
</style>
""", unsafe_allow_html=True)

st.title("BOLÃO ONLINE DAS OITAVAS DE FINAL")

# Lista de avatares com emojis grandes
avatares = ["⚽", "🕵️‍♂️", "🦁", "🐼", "😎", "🤠", "🤖", "🧙‍♂️", "🦸‍♂️"]

# Banco de dados simulado com as oitavas (Com Bandeiras e Pênaltis)
if "jogos" not in st.session_state:
    st.session_state.jogos = {
        "J1": {"time1": "Canadá", "flag1": "🇨🇦", "time2": "Marrocos", "flag2": "🇲🇦", "gols1": 0, "gols2": 0, "passa": None, "horario": "Amanhã 14:00", "encerrado": False},
        "J2": {"time1": "Paraguai", "flag1": "🇵🇾", "time2": "França", "flag2": "🇫🇷", "gols1": 0, "gols2": 0, "passa": None, "horario": "Amanhã 18:00", "encerrado": False},
        "J3": {"time1": "Brasil", "flag1": "🇧🇷", "time2": "Noruega", "flag2": "🇳🇴", "gols1": 0, "gols2": 0, "passa": None, "horario": "Dom., 05/07 17:00", "encerrado": False},
        "J4": {"time1": "México", "flag1": "🇲🇽", "time2": "Inglaterra", "flag2": "🏴󠁧󠁢󠁥󠁮ッグランド", "gols1": 0, "gols2": 0, "passa": None, "horario": "Dom., 05/07 21:00", "encerrado": False},
        "J5": {"time1": "Portugal", "flag1": "🇵🇹", "time2": "Espanha", "flag2": "🇪🇸", "gols1": 0, "gols2": 0, "passa": None, "horario": "Seg., 06/07 16:00", "encerrado": False},
        "J6": {"time1": "EUA", "flag1": "🇺🇸", "time2": "Bélgica", "flag2": "🇧🇪", "gols1": 0, "gols2": 0, "passa": None, "horario": "Seg., 06/07 21:00", "encerrado": False},
    }

if "palpites" not in st.session_state:
    st.session_state.palpites = [] # Limpo para novos usuários

if "usuarios" not in st.session_state:
    st.session_state.usuarios = {}

# Regras de Pontuação (Adaptadas para Mata-Mata)
def calcular_pontos(jogo, palpite):
    p1, p2, p_passa = palpite["p1"], palpite["p2"], palpite["passa"]
    r1, r2, r_passa = jogo["gols1"], jogo["gols2"], jogo["passa"]
    
    if p1 == r1 and p2 == r2:
        if r1 == r2: return 5 if p_passa == r_passa else 3 # Acertou placar e quem passou (5) ou errou pênalti (3)
        return 5 # Placar exato
    elif r1 == r2: # Se foi empate real
        if p1 == p2 and p_passa == r_passa: return 3 # Acertou tendência e quem passa
        elif p1 == p2: return 2 # Só tendência
        elif p_passa == r_passa: return 1 # Só quem passa
    elif (p1 > p2 and r1 > r2) or (p1 < p2 and r1 < r2): # Tendência
        return 2
    return 0

# Abas principais
st.divider()
aba_jogos, aba_ranking = st.tabs(["⚽ Partidas e Palpites", "📊 Ranking Geral"])

with aba_jogos:
    st.header("Partidas - Oitavas de Final")
    
    # Campo para novo usuário
    nome_usuario = st.text_input("Seu Nome/Apelido para o Bolão:", key="novo_usuario").strip().title()
    if nome_usuario:
        if nome_usuario not in st.session_state.usuarios:
            st.session_state.usuarios[nome_usuario] = {"avatar": avatares[0], "pontos": 0}
        
        # Seleção de Avatar
        avatar_selecao = st.selectbox(f"Escolha seu avatar, {nome_usuario}:", avatares, index=avatares.index(st.session_state.usuarios[nome_usuario]["avatar"]))
        st.session_state.usuarios[nome_usuario]["avatar"] = avatar_selecao
        
        col_partidas, col_espaco = st.columns([2, 1])
        
        with col_partidas:
            for id_jogo, j in st.session_state.jogos.items():
                if j["encerrado"]: continue
                
                with st.container():
                    st.markdown(f'<div class="css-2trqyj">', unsafe_allow_html=True)
                    st.markdown(f"**{j['flag1']} {j['time1']}** vs **{j['flag2']} {j['time2']}**")
                    st.caption(j['horario'])
                    
                    c1, c2 = st.columns(2)
                    with c1: p1 = st.number_input(f"Gols {j['time1']}", min_value=0, step=1, key=f"p1_{id_jogo}_{nome_usuario}")
                    with c2: p2 = st.number_input(f"Gols {j['time2']}", min_value=0, step=1, key=f"p2_{id_jogo}_{nome_usuario}")
                    
                    # Lógica de Pênaltis
                    passa = None
                    if p1 == p2:
                        st.caption("Empate? Quem avança nos pênaltis?")
                        passa = st.radio("Selecione:", [j['time1'], j['time2']], horizontal=True, key=f"passa_{id_jogo}_{nome_usuario}")
                    
                    if st.button("Dar Palpite", key=f"btn_{id_jogo}"):
                        # Remove palpite antigo e adiciona novo
                        st.session_state.palpites = [p for p in st.session_state.palpites if not (p["nome"] == nome_usuario and p["jogo"] == id_jogo)]
                        st.session_state.palpites.append({"nome": nome_usuario, "jogo": id_jogo, "p1": p1, "p2": p2, "passa": passa})
                        st.success(f"Palpite para {j['time1']} x {j['time2']} salvo!")
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Digite seu nome acima para começar a dar palpites.")

with aba_ranking:
    st.header("Ranking Geral - Top Pontuadores")
    
    # Processar Pontuação
    total_pontos = {}
    total_cravadas = {}
    for p in st.session_state.palpites:
        nome = p["nome"]
        total_pontos[nome] = total_pontos.get(nome, 0)
        total_cravadas[nome] = total_cravadas.get(nome, 0)
        
        jogo = st.session_state.jogos[p["jogo"]]
        if jogo["encerrado"]:
            pontos = calcular_pontos(jogo, p)
            total_pontos[nome] += pontos
            if pontos == 5: total_cravadas[nome] += 1
            
    # Exibir Top 3 com avatares grandes
    top_3 = sorted(st.session_state.usuarios.keys(), key=lambda n: total_pontos.get(n, 0), reverse=True)[:3]
    
    if top_3:
        cols_top = st.columns(3)
        for idx, nome in enumerate(top_3):
            with cols_top[idx]:
                avatar = st.session_state.usuarios[nome]["avatar"]
                pontos = total_pontos.get(nome, 0)
                
                st.markdown(f'<div class="avatar-large">{avatar}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="text-align: center;"><b>{idx+1}º. {nome}</b><br>{pontos} pts.</div>', unsafe_allow_html=True)
        st.divider()

    # Tabela Completa
    if total_pontos:
        df_rank = pd.DataFrame([{"Usuário": f"{st.session_state.usuarios[n]['avatar']} {n}", "P pts": total_pontos[n], "Cravadas": total_cravadas[n]} for n in st.session_state.usuarios])
        df_rank = df_rank.sort_values(by="P pts", ascending=False).reset_index(drop=True)
        df_rank.index = df_rank.index + 1
        st.dataframe(df_rank, use_container_width=True)
    else:
        st.info("Nenhum palpite computado ainda.")

# Seção de Admin (Apenas para você lançar os resultados)
st.divider()
st.subheader("⚙️ ADMIN - LANÇAR RESULTADOS OFICIAIS")
for id_jogo, j in st.session_state.jogos.items():
    st.markdown(f"**{j['flag1']} {j['time1']}** vs **{j['flag2']} {j['time2']}**")
    
    col1, col2 = st.columns(2)
    with col1: g1 = st.number_input(f"Gols {j['time1']}", min_value=0, step=1, value=j["gols1"], key=f"admin_g1_{id_jogo}")
    with col2: g2 = st.number_input(f"Gols {j['time2']}", min_value=0, step=1, value=j["gols2"], key=f"admin_g2_{id_jogo}")
    
    passa = None
    if g1 == g2:
        st.caption("Empate! Quem venceu nos pênaltis?")
        passa = st.radio("Vencedor:", [j['time1'], j['time2']], horizontal=True, key=f"admin_passa_{id_jogo}")
        
    enc = st.checkbox("✅ Jogo Encerrado (Computar pontos no Ranking)", value=j["encerrado"], key=f"admin_enc_{id_jogo}")
    
    if st.button("Atualizar Resultado Oficial", key=f"btn_admin_{id_jogo}"):
        st.session_state.jogos[id_jogo]["gols1"] = g1
        st.session_state.jogos[id_jogo]["gols2"] = g2
        st.session_state.jogos[id_jogo]["passa"] = passa
        st.session_state.jogos[id_jogo]["encerrado"] = enc
        st.success("Placar atualizado e ranking recalculado!")
