import streamlit as st
import pandas as pd

# Configuração da página otimizada para celular (layout focado/estreito)
st.set_page_config(page_title="Bolão das Oitavas", page_icon="⚽", layout="centered")

# Estilização CSS customizada para Mobile-First, Bandeiras Grandes e Avatares Evidentes
st.markdown("""
<style>
    /* Ajusta o tamanho máximo para parecer um aplicativo de telemóvel */
    .main .block-container {
        max-width: 480px;
        padding-top: 1.5rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    /* Estilo das Bandeiras Grandes */
    .bandeira-grande {
        font-size: 55px;
        line-height: 1;
        display: inline-block;
        margin: 5px 15px;
    }
    /* Estilo do Card de Jogo */
    .card-jogo {
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 16px;
        padding: 15px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    /* Avatar Gigante na Seleção */
    .avatar-selecao-display {
        font-size: 70px;
        text-align: center;
        margin-bottom: 10px;
    }
    /* Nomes dos times em destaque */
    .time-texto {
        font-size: 18px;
        font-weight: bold;
        color: #212529;
    }
    /* Remove preenchimentos desnecessários para caber tudo na tela do telemóvel */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-left: 8px;
        padding-right: 8px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚽ Bolão das Oitavas")

# Lista de Avatares disponíveis
lista_avatares = ["⚽", "😎", "🦁", "🤖", "🧙‍♂️", "🦊", "🦅", "🏆", "🔥", "👑", "🐼", "👽"]

# Banco de dados simulado com as seleções das oitavas e bandeiras grandes
if "jogos" not in st.session_state:
    st.session_state.jogos = {
        "J1": {"time1": "Canadá", "flag1": "🇨🇦", "time2": "Marrocos", "flag2": "🇲🇦", "gols1": 0, "gols2": 0, "passa": None, "encerrado": False},
        "J2": {"time1": "Brasil", "flag1": "🇧🇷", "time2": "Noruega", "flag2": "🇳🇴", "gols1": 0, "gols2": 0, "passa": None, "encerrado": False},
        "J3": {"time1": "Portugal", "flag1": "🇵🇹", "time2": "Espanha", "flag2": "🇪🇸", "gols1": 0, "gols2": 0, "passa": None, "encerrado": False},
        "J4": {"time1": "Paraguai", "flag1": "🇵🇾", "time2": "França", "flag2": "🇫🇷", "gols1": 0, "gols2": 0, "passa": None, "encerrado": False},
        "J5": {"time1": "México", "flag1": "🇲🇽", "time2": "Inglaterra", "flag2": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "gols1": 0, "gols2": 0, "passa": None, "encerrado": False},
        "J6": {"time1": "EUA", "flag1": "🇺🇸", "time2": "Bélgica", "flag2": "🇧🇪", "gols1": 0, "gols2": 0, "passa": None, "encerrado": False},
    }

if "palpites" not in st.session_state:
    st.session_state.palpites = []

if "usuarios" not in st.session_state:
    st.session_state.usuarios = {}

# Regra de cálculo de pontuação simplificada e precisa para mata-mata
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

# Abas de Navegação criadas pensando no uso pelo telemóvel
aba1, aba2, aba3 = st.tabs(["📊 Ranking", "✍️ Palpitar", "⚙️ Admin"])

# ABA 1: RANKING GERAL E FORMATADOR PARA WHATSAPP
with aba1:
    st.header("🏆 Classificação")
    
    # Processamento de pontuação
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
            dados_ranking.append({"Participante": f"{avatar} {n}", "Pontos": pts, "Pure_Nome": n, "Pure_Avatar": avatar})
            
        df_ranking = pd.DataFrame(dados_ranking).sort_values(by="Pontos", ascending=False).reset_index(drop=True)
        df_ranking.index = df_ranking.index + 1
        
        # Exibição limpa da tabela para ecrãs pequenos
        st.dataframe(df_ranking[["Participante", "Pontos"]], use_container_width=True)
        
        # --- BOTÃO E FORMATADOR PARA WHATSAPP ---
        st.divider()
        st.subheader("📲 Enviar no WhatsApp")
        st.write("Gere o texto formatado com os emojis para colar direto no grupo!")
        
        texto_whatsapp = "🏆 *RANKING ATUALIZADO DO BOLÃO* 🏆\n\n"
        for idx, row in df_ranking.iterrows():
            texto_whatsapp += f"{idx}º {row['Pure_Avatar']} *{row['Pure_Nome']}* — {row['Pontos']} pts\n"
        texto_whatsapp += "\n👉 *Faça seus palpites no nosso link público!*"
        
        st.code(texto_whatsapp, language="text")
        st.caption("Toque e segure no quadro acima para copiar todo o texto e colar no WhatsApp.")
    else:
        st.info("Nenhum palpite computado ainda. Os pontos vão aparecer assim que o Admin encerrar os jogos!")

# ABA 2: ÁREA DE PALPITES COM OS SEUS PEDIDOS
with aba2:
    st.header("✍️ Faça seu Palpite")
    
    # Campo de Identificação e escolha do Avatar
    nome_usuario = st.text_input("Seu Nome/Apelido:", key="user_nome").strip().title()
    
    if nome_usuario:
        avatar_atual = st.session_state.usuarios.get(nome_usuario, lista_avatares[0])
        avatar_escolhido = st.selectbox("Escolha seu Avatar:", lista_avatares, index=lista_avatares.index(avatar_atual))
        st.session_state.usuarios[nome_usuario] = avatar_escolhido
        
        # Display gigante do avatar selecionado
        st.markdown(f'<div class="avatar-selecao-display">{avatar_escolhido}</div>', unsafe_allow_html=True)
        st.divider()
        
        # Listagem dos cards de jogos
        for id_jogo, j in st.session_state.jogos.items():
            if j["encerrado"]:
                continue
                
            st.markdown(f"""
            <div class="card-jogo">
                <div>
                    <span class="bandeira-grande">{j['flag1']}</span>
                    <span style="font-size: 24px; font-weight: bold; position: relative; top: -15px;">VS</span>
                    <span class="bandeira-grande">{j['flag2']}</span>
                </div>
                <div class="time-texto">{j['time1']} x {j['time2']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Inputs lado a lado otimizados para telemóvel
            c1, c2 = st.columns(2)
            with c1:
                p1 = st.number_input(f"Gols {j['time1']}", min_value=0, step=1, key=f"p1_{id_jogo}_{nome_usuario}")
            with c2:
                p2 = st.number_input(f"Gols {j['time2']}", min_value=0, step=1, key=f"p2_{id_jogo}_{nome_usuario}")
                
            # Regra de pênalti ativa caso haja empate nos palpites
            passa = None
            if p1 == p2:
                st.caption("Empate detetado! Quem se classifica nos Pênaltis?")
                passa = st.radio("Avança:", [j['time1'], j['time2']], horizontal=True, key=f"passa_{id_jogo}_{nome_usuario}")
                
            if st.button("Salvar este Palpite", key=f"save_{id_jogo}"):
                st.session_state.palpites = [p for p in st.session_state.palpites if not (p["nome"] == nome_usuario and p["jogo"] == id_jogo)]
                st.session_state.palpites.append({"nome": nome_usuario, "jogo": id_jogo, "p1": p1, "p2": p2, "passa": passa})
                st.success("Palpite gravado!")
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("Insira seu nome acima para liberar a tela de palpites.")

# ABA 3: PAINEL ADMINISTRADOR PARA INSERÇÃO DO RESULTADO REAL FINAL
with aba3:
    st.header("⚙️ Painel de Controle (Admin)")
    st.write("Área para definir o placar final oficial dos jogos e rodar a pontuação.")
    
    for id_jogo, j in st.session_state.jogos.items():
        st.markdown(f"### {j['flag1']} {j['time1']} x {j['time2']} {j['flag2']}")
        
        c1, c2 = st.columns(2)
        with c1:
            g1 = st.number_input(f"Placar Real {j['time1']}", min_value=0, step=1, value=j["gols1"], key=f"adm_g1_{id_jogo}")
        with c2:
            g2 = st.number_input(f"Placar Real {j['time2']}", min_value=0, step=1, value=j["gols2"], key=f"adm_g2_{id_jogo}")
            
        passa_real = None
        if g1 == g2:
            st.caption("Empate no jogo oficial! Quem avançou nos pênaltis?")
            passa_real = st.radio("Vencedor nos Pênaltis:", [j['time1'], j['time2']], horizontal=True, key=f"adm_passa_{id_jogo}")
            
        encerrar = st.checkbox("Fechar inscrições e computar pontos", value=j["encerrado"], key=f"adm_enc_{id_jogo}")
        
        if st.button("Gravar Resultado Oficial", key=f"adm_btn_{id_jogo}"):
            st.session_state.jogos[id_jogo]["gols1"] = g1
            st.session_state.jogos[id_jogo]["gols2"] = g2
            st.session_state.jogos[id_jogo]["passa"] = passa_real
            st.session_state.jogos[id_jogo]["encerrado"] = encerrar
            st.success("Resultado salvo! O ranking foi recalculado.")
        st.divider()
