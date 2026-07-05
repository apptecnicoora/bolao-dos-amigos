import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import random

# Configuração mobile-first
st.set_page_config(page_title="Bolão Hardcore Oitavas", page_icon="⚽", layout="centered")

# --- CSS CUSTOMIZADO: NEON BRASIL E REMOÇÃO DE BOTÕES +/- ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117 !important; color: #ffffff !important; }
    h1, h2, h3, h4, h5, p, span, label { color: #ffffff !important; }
    .main .block-container { max-width: 480px; padding-top: 1rem; padding-left: 0.8rem; padding-right: 0.8rem; }
    
    /* CARDS NEON BRASIL */
    [data-testid="stForm"], .stExpander {
        background-color: #161a22 !important;
        border: 2px solid #009B3A !important;
        border-radius: 16px !important;
        box-shadow: 0 0 15px rgba(0, 155, 58, 0.4) !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
    }
    
    /* BOTÕES NEON BRASIL */
    .stButton > button {
        background-color: #009B3A !important;
        color: #FFDF00 !important;
        border: 2px solid #FFDF00 !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        width: 100% !important;
        height: 50px !important;
        transition: 0.3s !important;
    }

    /* REMOVER SETAS DOS CAMPOS DE NÚMERO */
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
    input[type=number] {
        -moz-appearance: textfield;
        text-align: center !important;
        font-size: 1.3rem !important;
        font-weight: bold !important;
        background-color: #202632 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    
    .imagem-topo {
        border-radius: 15px;
        border: 3px solid #009B3A;
        box-shadow: 0 0 20px rgba(0, 155, 58, 0.6);
        margin-bottom: 20px;
    }

    .player-draw-box {
        background: linear-gradient(145deg, #1f242e, #161a22);
        border: 2px solid #FFDF00;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- CONEXÃO E CARREGAMENTO DE DADOS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_dados():
    df_j = conn.read(worksheet="Jogos", ttl=10)
    df_p = conn.read(worksheet="Palpites", ttl=10)
    df_u = conn.read(worksheet="Usuarios", ttl=10)
    
    # Trava Anti-KeyError (Horário)
    if "horário" not in df_j.columns: df_j["horário"] = "A definir"
    
    # Trava Anti-TypeError (Admin)
    df_j["passa"] = df_j["passa"].astype(object)
    df_j["encerrado"] = df_j["encerrado"].astype(object)
    
    return df_j, df_p, df_u

df_jogos_sheet, df_palpites, df_usuarios = ler_dados()

# Dicionário de apoio para os nomes das seleções e emojis (WhatsApp)
bandeiras_emoji = {
    "Canadá": "🇨🇦", "Marrocos": "🇲🇦", "Brasil": "🇧🇷", "Noruega": "🇳🇴",
    "Portugal": "🇵🇹", "Espanha": "🇪🇸", "Paraguai": "🇵🇾", "França": "🇫🇷",
    "México": "🇲🇽", "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "EUA": "🇺🇸", "Bélgica": "🇧🇪",
    "Argentina": "🇦🇷", "Egito": "🇪🇬", "Suíça": "🇨🇭", "Colômbia": "🇨🇴"
}

# --- REGRA HARDCORE: SÓ PLACAR EXATO DÁ PONTO ---
def calcular_pontos(jogo, palpite):
    try:
        if int(palpite["p1"]) == int(jogo["gols1"]) and int(palpite["p2"]) == int(jogo["gols2"]):
            return 5
        return 0
    except: return 0

aba1, aba2, aba3 = st.tabs(["🏆 Ranking", "✍️ Palpitar", "⚙️ Admin"])

# --- ABA 1: RANKING E SORTEIO DE JOGADOR ---
with aba1:
    # Imagem do Bruxo no Topo
    st.image("https://s2.glbimg.com/Q281B94oUoIq7O_f7M-5Q4J1kU4=/0x0:2024x1401/984x0/smart/filters:strip_icc()/i.s3.glbimg.com/v1/AUTH_bc8228b6673f488aa253bbcb03c80ec5/internal_photos/bs/2020/P/z/k1UaM1RkymJb4U0pQ8BA/ronaldinho-gaucho-selecao-2006.jpg", use_container_width=True)
    
    # SORTEIO DE JOGADOR (VISÍVEL E CORRIGIDO)
    st.markdown("<div class='player-draw-box'>", unsafe_allow_html=True)
    st.subheader("🎲 Qual Jogador Você é Hoje?")
    if st.button("SORTEAR MEU JOGADOR LENDÁRIO"):
        lendas = [
            ("Lionel Messi", "https://th.bing.com/th/id/OIP.XG0G_XmB1-OaH1eN8rG9_AHaE8"),
            ("Cristiano Ronaldo", "https://th.bing.com/th/id/OIP.L_qR9LzS5Q9x1Y0f8k0BvQHaE8"),
            ("Neymar Jr", "https://th.bing.com/th/id/OIP.ZzG_XmB1-OaH1eN8rG9_AHaE8"),
            ("Ronaldinho Gaúcho", "https://th.bing.com/th/id/OIP.k1UaM1RkymJb4U0pQ8BA")
        ]
        nome, img_link = random.choice(lendas)
        st.markdown(f"### Você tirou o {nome}!")
        st.image(img_link, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.header("🏆 Classificação Geral")
    
    # Processamento do Ranking
    dict_jogos = {row["id"]: row for _, row in df_jogos_sheet.iterrows()}
    pontos_totais = {}
    
    for _, p in df_palpites.iterrows():
        nome = p["nome"]
        pontos_totais[nome] = pontos_totais.get(nome, 0)
        jogo = dict_jogos.get(p["jogo"])
        if jogo and str(jogo["encerrado"]) == "Sim":
            pontos_totais[nome] += calcular_pontos(jogo, p)
            
    if pontos_totais:
        dados_ranking = []
        for n, pts in pontos_totais.items():
            u_row = df_usuarios[df_usuarios["nome"] == n]
            av = u_row["avatar"].values[0] if not u_row.empty else "⚽"
            dados_ranking.append({"Participante": f"{av} {n}", "Pontos": pts})
        
        df_rank = pd.DataFrame(dados_ranking).sort_values(by="Pontos", ascending=False)
        for _, row in df_rank.iterrows():
            st.markdown(f"<div style='background:#161a22; padding:10px; border-radius:8px; border-left:4px solid #009B3A; margin-bottom:5px;'><b>{row['Participante']}</b> — {row['Pontos']} pts</div>", unsafe_allow_html=True)
            
        # WhatsApp Compartilhamento
        st.divider()
        st.subheader("📲 Copiar Ranking")
        txt_wa = "🏆 *RANKING BOLÃO HARDCORE* 🏆\n\n"
        for i, r in df_rank.iterrows(): txt_wa += f"{r['Participante']} — {r['Pontos']} pts\n"
        st.code(txt_wa, language="text")
        
        # Ver Palpites dos Amigos
        st.subheader("👀 Espiar Adversários")
        for user in df_palpites["nome"].unique():
            with st.expander(f"Ver palpites de: {user}"):
                p_user = df_palpites[df_palpites["nome"] == user]
                for _, pu in p_user.iterrows():
                    j = dict_jogos.get(pu["jogo"])
                    st.write(f"{j['time1']} {pu['p1']} x {pu['p2']} {j['time2']}")
    else:
        st.info("Aguardando resultados oficiais!")

# --- ABA 2: PALPITAR ---
with aba2:
    st.header("✍️ Dar Palpite")
    meu_nome = st.text_input("Seu Nome:", key="input_nome").strip().title()
    if meu_nome:
        for id_jogo, j in dict_jogos.items():
            if str(j["encerrado"]) == "Sim": continue
            with st.form(key=f"f_{id_jogo}"):
                st.write(f"**{j['time1']} x {j['time2']}** - {j['horário']}")
                c1, c2 = st.columns(2)
                with c1: p1 = st.number_input(f"Gols {j['time1']}", min_value=0, step=1, key=f"p1_{id_jogo}")
                with c2: p2 = st.number_input(f"Gols {j['time2']}", min_value=0, step=1, key=f"p2_{id_jogo}")
                if st.form_submit_button("GRAVAR PALPITE"):
                    df_palpites = df_palpites[~((df_palpites["nome"] == meu_nome) & (df_palpites["jogo"] == id_jogo))]
                    df_palpites = pd.concat([df_palpites, pd.DataFrame([{"nome": meu_nome, "jogo": id_jogo, "p1": p1, "p2": p2, "passa": ""}])], ignore_index=True)
                    conn.update(worksheet="Palpites", data=df_palpites)
                    st.success("Palpite Gravado!")
    else: st.warning("Digite seu nome para começar.")

# --- ABA 3: ADMIN ---
with aba3:
    st.header("⚙️ Painel Admin")
    for id_jogo, j in dict_jogos.items():
        with st.form(key=f"adm_{id_jogo}"):
            st.write(f"Resultado: **{j['time1']} x {j['time2']}**")
            ac1, ac2 = st.columns(2)
            with ac1: g1 = st.number_input("Gols T1", value=int(j["gols1"]), step=1, key=f"g1_{id_jogo}")
            with ac2: g2 = st.number_input("Gols T2", value=int(j["gols2"]), step=1, key=f"g2_{id_jogo}")
            enc = st.checkbox("Encerrar Jogo", value=(str(j["encerrado"]) == "Sim"), key=f"enc_{id_jogo}")
            if st.form_submit_button("ATUALIZAR PLACAR OFICIAL"):
                df_jogos_sheet.loc[df_jogos_sheet["id"] == id_jogo, "gols1"] = g1
                df_jogos_sheet.loc[df_jogos_sheet["id"] == id_jogo, "gols2"] = g2
                df_jogos_sheet.loc[df_jogos_sheet["id"] == id_jogo, "encerrado"] = "Sim" if enc else "Não"
                conn.update(worksheet="Jogos", data=df_jogos_sheet)
                st.cache_data.clear()
                st.success("Placar Atualizado com Sucesso!")
