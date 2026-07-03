import streamlit as st
import pandas as pd

# Configuração inicial da página
st.set_page_config(page_title="Bolão dos Amigos", page_icon="⚽", layout="centered")

st.title("⚽ Bolão Online dos Amigos")
st.markdown("Insira seus palpites, acompanhe os resultados e suba no ranking!")

# --- BANCO DE DADOS TEMPORÁRIO (Simulado em Memória) ---
if "jogos" not in st.session_state:
    st.session_state.jogos = {
        "Jogo 1": {"time1": "Brasil", "time2": "Argentina", "gols1": 2, "gols2": 1, "encerrado": True},
        "Jogo 2": {"time1": "Flamengo", "time2": "Palmeiras", "gols1": 1, "gols2": 1, "encerrado": True},
        "Jogo 3": {"time1": "Real Madrid", "time2": "Barcelona", "gols1": 0, "gols2": 0, "encerrado": False},
    }

if "palpites" not in st.session_state:
    # Dados iniciais para teste
    st.session_state.palpites = [
        {"nome": "Daniel", "jogo": "Jogo 1", "p1": 2, "p2": 1},
        {"nome": "Daniel", "jogo": "Jogo 2", "p1": 2, "p2": 0},
        {"nome": "Pedro", "jogo": "Jogo 1", "p1": 1, "p2": 0},
        {"nome": "Pedro", "jogo": "Jogo 2", "p1": 1, "p2": 1},
        {"nome": "Maria", "jogo": "Jogo 1", "p1": 0, "p2": 2},
        {"nome": "Maria", "jogo": "Jogo 2", "p1": 1, "p2": 1},
    ]

# --- REGRAS DE PONTUAÇÃO ---
VALOR_PLACAR_EXATO = 5
VALOR_ACERTO_VENDEDOR = 2

def calcular_pontos(p1, p2, r1, r2):
    # Se o jogo não terminou, não pontua ainda
    if r1 is None or r2 is None:
        return 0
    # Placar Exato
    if p1 == r1 and p2 == r2:
        return VALOR_PLACAR_EXATO
    # Acertou o Vencedor ou o Empate (mas errou o placar exato)
    if (p1 > p2 and r1 > r2) or (p1 < p2 and r1 < r2) or (p1 == p2 and r1 == r2):
        return VALOR_ACERTO_VENDEDOR
    return 0

# --- NAVEGAÇÃO ENTRE ABAS ---
aba1, aba2, aba3 = st.tabs(["📊 Ranking Geral", "✍️ Dar Palpite", "⚙️ Gerenciar Jogos (Admin)"])

# ABA 1: RANKING GERAL
with aba1:
    st.header("🏆 Classificação Atual")
    
    # Processar pontuação
    pontos_totais = {}
    for p in st.session_state.palpites:
        nome = p["nome"]
        jogo_id = p["jogo"]
        jogo = st.session_state.jogos[jogo_id]
        
        if jogo["encerrado"]:
            pts = calcular_pontos(p["p1"], p["p2"], jogo["gols1"], jogo["gols2"])
            pontos_totais[nome] = pontos_totais.get(nome, 0) + pts
        else:
            pontos_totais[nome] = pontos_totais.get(nome, 0)
            
    if pontos_totais:
        df_ranking = pd.DataFrame(list(pontos_totais.items()), columns=["Participante", "Pontos"])
        df_ranking = df_ranking.sort_values(by="Pontos", ascending=False).reset_index(drop=True)
        st.dataframe(df_ranking, use_container_width=True)
    else:
        st.info("Nenhum ponto computado ainda.")

# ABA 2: DAR PALPITE
with aba2:
    st.header("📝 Seus Palpites")
    nome_usuario = st.text_input("Seu Nome/Apelido:", key="usuario_atual")
    
    if nome_usuario:
        st.subheader(f"Palpites de {nome_usuario}")
        for j_id, j_info in st.session_state.jogos.items():
            if not j_info["encerrado"]:
                st.write(f"**{j_info['time1']} vs {j_info['time2']}**")
                col1, col2 = st.columns(2)
                with col1:
                    p1 = st.number_input(f"Gols {j_info['time1']}", min_value=0, step=1, key=f"p1_{j_id}")
                with col2:
                    p2 = st.number_input(f"Gols {j_info['time2']}", min_value=0, step=1, key=f"p2_{j_id}")
                
                if st.button(f"Salvar Palpite para {j_id}"):
                    # Remove palpite antigo se existir e adiciona o novo
                    st.session_state.palpites = [p for p in st.session_state.palpites if not (p["nome"] == nome_usuario and p["jogo"] == j_id)]
                    st.session_state.palpites.append({"nome": nome_usuario, "jogo": j_id, "p1": p1, "p2": p2})
                    st.success("Palpite salvo com sucesso!")
            else:
                st.text(f"🔒 {j_info['time1']} {j_info['gols1']} x {j_info['gols2']} {j_info['time2']} (Inscrições encerradas)")

# ABA 3: GERENCIAR JOGOS (ADMIN)
with aba3:
    st.header("🛠️ Painel do Administrador")
    st.subheader("Resultados Reais dos Jogos")
    
    for j_id, j_info in st.session_state.jogos.items():
        st.write(f"**{j_info['time1']} vs {j_info['time2']}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            g1 = st.number_input(f"Resultado {j_info['time1']}", min_value=0, step=1, value=j_info["gols1"], key=f"r1_{j_id}")
        with col2:
            g2 = st.number_input(f"Resultado {j_info['time2']}", min_value=0, step=1, value=j_info["gols2"], key=f"r2_{j_id}")
        with col3:
            enc = st.checkbox("Encerrado/Computar Pontos", value=j_info["encerrado"], key=f"enc_{j_id}")
            
        st.session_state.jogos[j_id]["gols1"] = g1
        st.session_state.jogos[j_id]["gols2"] = g2
        st.session_state.jogos[j_id]["encerrado"] = enc
    st.info("Altere os valores acima para ver o Ranking Geral recalcular na hora!")