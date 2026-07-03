import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bolão das Oitavas", page_icon="⚽", layout="centered")

st.title("⚽ Bolão - Oitavas de Final")

# Lista de avatares disponíveis para escolha
lista_avatares = ["😎", "🤠", "🤖", "👽", "🦁", "🐼", "🦊", "🧙‍♂️", "🕵️‍♂️", "🦸‍♂️", "🧑‍💻", "⚽"]

# --- BANCO DE DADOS TEMPORÁRIO ---
if "jogos" not in st.session_state:
    st.session_state.jogos = {
        "J1": {"time1": "Canadá", "time2": "Marrocos", "gols1": 0, "gols2": 0, "penaltis": None, "encerrado": False},
        "J2": {"time1": "Brasil", "time2": "Noruega", "gols1": 0, "gols2": 0, "penaltis": None, "encerrado": False},
        "J3": {"time1": "Portugal", "time2": "Espanha", "gols1": 0, "gols2": 0, "penaltis": None, "encerrado": False},
        "J4": {"time1": "Paraguai", "time2": "França", "gols1": 0, "gols2": 0, "penaltis": None, "encerrado": False},
        "J5": {"time1": "México", "time2": "Inglaterra", "gols1": 0, "gols2": 0, "penaltis": None, "encerrado": False},
        "J6": {"time1": "Estados Unidos", "time2": "Bélgica", "gols1": 0, "gols2": 0, "penaltis": None, "encerrado": False},
    }

# Começamos com a lista de palpites vazia (sem usuários pre-definidos)
if "palpites" not in st.session_state:
    st.session_state.palpites = []
    
# Dicionário para salvar os avatares atrelados aos nomes
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {}

# --- REGRA DE PONTUAÇÃO ---
def calcular_pontos(j_info, palpite):
    r1, r2 = j_info["gols1"], j_info["gols2"]
    p1, p2 = palpite["p1"], palpite["p2"]
    r_penalti = j_info.get("penaltis")
    p_penalti = palpite.get("penaltis")
    
    # Descobrir quem avançou no resultado REAL
    if r1 > r2: real_venc = j_info["time1"]
    elif r2 > r1: real_venc = j_info["time2"]
    else: real_venc = r_penalti
    
    # Descobrir quem avançou no PALPITE
    if p1 > p2: palp_venc = j_info["time1"]
    elif p2 > p1: palp_venc = j_info["time2"]
    else: palp_venc = p_penalti

    # Lógica de Pontos
    if p1 == r1 and p2 == r2:
        if r1 == r2: # Se foi empate no tempo normal
            # 5 pts se acertou placar e quem passou nos pênaltis, 3 pts se errou o pênalti
            return 5 if p_penalti == r_penalti else 3 
        return 5 # 5 pts Cravou o placar exato
    elif real_venc == palp_venc:
        return 2 # 2 pts Acertou apenas a tendência (quem classificou)
    return 0

# --- NAVEGAÇÃO ---
aba1, aba2, aba3 = st.tabs(["📊 Ranking", "✍️ Dar Palpite", "⚙️ Admin (Lançar Resultados)"])

# ABA 1: RANKING
with aba1:
    st.header("🏆 Classificação Atual")
    pontos_totais = {}
    
    # Processar a pontuação de todos
    for p in st.session_state.palpites:
        nome = p["nome"]
        jogo_id = p["jogo"]
        jogo = st.session_state.jogos[jogo_id]
        
        if nome not in pontos_totais:
            pontos_totais[nome] = 0
            
        if jogo["encerrado"]:
            pontos_totais[nome] += calcular_pontos(jogo, p)
            
    if pontos_totais:
        # Montar a tabela com os avatares
        dados_ranking = []
        for n, pts in pontos_totais.items():
            avatar = st.session_state.usuarios.get(n, "👤")
            dados_ranking.append({"Participante": f"{avatar} {n}", "Pontos": pts})
            
        df_ranking = pd.DataFrame(dados_ranking).sort_values(by="Pontos", ascending=False).reset_index(drop=True)
        df_ranking.index = df_ranking.index + 1 # Começar o rank a partir do número 1
        st.dataframe(df_ranking, use_container_width=True)
    else:
        st.info("Nenhum palpite computado nos jogos encerrados ainda. Liderança aberta!")

# ABA 2: DAR PALPITE
with aba2:
    st.header("📝 Seus Palpites")
    
    col_nome, col_avatar = st.columns([3, 1])
    with col_nome:
        nome_usuario = st.text_input("Seu Nome:", key="usuario_atual").strip().title()
    with col_avatar:
        avatar_escolhido = st.selectbox("Avatar:", lista_avatares)
    
    if nome_usuario:
        st.session_state.usuarios[nome_usuario] = avatar_escolhido
        st.divider()
        
        for j_id, j_info in st.session_state.jogos.items():
            if not j_info["encerrado"]:
                st.write(f"**{j_info['time1']} x {j_info['time2']}**")
                
                # Resgatar palpite já salvo, se existir, para não perder os dados
                palpite_existente = next((p for p in st.session_state.palpites if p["nome"] == nome_usuario and p["jogo"] == j_id), None)
                val_p1 = palpite_existente["p1"] if palpite_existente else 0
                val_p2 = palpite_existente["p2"] if palpite_existente else 0
                val_penalti = palpite_existente.get("penaltis") if palpite_existente else None

                col1, col2 = st.columns(2)
                with col1:
                    p1 = st.number_input(f"Gols {j_info['time1']}", min_value=0, step=1, value=val_p1, key=f"p1_{j_id}_{nome_usuario}")
                with col2:
                    p2 = st.number_input(f"Gols {j_info['time2']}", min_value=0, step=1, value=val_p2, key=f"p2_{j_id}_{nome_usuario}")
                
                # Se houver empate no palpite, abre a opção de pênaltis
                p_penalti = None
                if p1 == p2:
                    idx_penalti = 0
                    if val_penalti == j_info['time2']: idx_penalti = 1
                    st.caption("Empate! Quem avança nos pênaltis?")
                    p_penalti = st.radio("Selecione:", [j_info['time1'], j_info['time2']], index=idx_penalti, horizontal=True, key=f"pen_{j_id}_{nome_usuario}")
                
                if st.button("Salvar Palpite", key=f"btn_{j_id}"):
                    # Substitui o palpite antigo pelo novo
                    st.session_state.palpites = [p for p in st.session_state.palpites if not (p["nome"] == nome_usuario and p["jogo"] == j_id)]
                    st.session_state.palpites.append({
                        "nome": nome_usuario, 
                        "jogo": j_id, 
                        "p1": p1, 
                        "p2": p2,
                        "penaltis": p_penalti
                    })
                    st.success(f"Palpite salvo para {j_info['time1']} x {j_info['time2']}!")
                st.divider()
            else:
                st.text(f"🔒 {j_info['time1']} {j_info['gols1']} x {j_info['gols2']} {j_info['time2']} (Jogo Encerrado)")

# ABA 3: ADMINISTRAÇÃO E GABARITO
with aba3:
    st.header("🛠️ Resultado Oficial")
    st.write("Insira o placar real final para o sistema recalcular os pontos.")
    
    for j_id, j_info in st.session_state.jogos.items():
        st.write(f"**{j_info['time1']} x {j_info['time2']}**")
        
        col1, col2 = st.columns(2)
        with col1:
            g1 = st.number_input(f"Gols Reais {j_info['time1']}", min_value=0, step=1, value=j_info["gols1"], key=f"r1_{j_id}")
        with col2:
            g2 = st.number_input(f"Gols Reais {j_info['time2']}", min_value=0, step=1, value=j_info["gols2"], key=f"r2_{j_id}")
        
        # Pênaltis reais se o jogo terminar empatado
        r_penalti = None
        if g1 == g2:
            st.caption("Empate! Quem venceu nos pênaltis?")
            r_penalti = st.radio("Vencedor:", [j_info['time1'], j_info['time2']], horizontal=True, key=f"rpen_{j_id}")
            
        enc = st.checkbox("✅ Jogo Encerrado (Computar pontos no Ranking)", value=j_info["encerrado"], key=f"enc_{j_id}")
        
        if st.button("Atualizar Placar Oficial", key=f"btn_admin_{j_id}"):
            st.session_state.jogos[j_id]["gols1"] = g1
            st.session_state.jogos[j_id]["gols2"] = g2
            st.session_state.jogos[j_id]["penaltis"] = r_penalti
            st.session_state.jogos[j_id]["encerrado"] = enc
            st.success("Placar atualizado e ranking recalculado!")
        st.divider()
