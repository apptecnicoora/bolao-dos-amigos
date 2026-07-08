import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import random
import os
import json
import urllib.request
import urllib.parse
import base64
from datetime import datetime, timedelta, timezone

# Configuração mobile-first
st.set_page_config(page_title="Bolão das Quartas", page_icon="⚽", layout="centered")

# --- CSS CUSTOMIZADO: TEMA ESCURO COM NEON BRASIL ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117 !important; color: #ffffff !important; }
    h1, h2, h3, h4, h5 { color: #009B3A !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.05); }
    h1, h2, h3, h4, h5, p, span, label, .stMarkdown { color: #ffffff !important; }
    
    .main .block-container { max-width: 480px; padding-top: 1rem; padding-left: 0.8rem; padding-right: 0.8rem; }
    
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
    
    .termometro {
        font-size: 0.8rem;
        text-align: center;
        color: #8b949e;
        margin-top: -5px;
        margin-bottom: 15px;
        background-color: #202632;
        border-radius: 8px;
        padding: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚽ BOLÃO ONLINE DAS QUARTAS")
st.markdown("Confira os horários dos jogos, dê seus palpites e acompanhe o Ranking!")

# --- UTILITÁRIO DE TEMPO E BLOQUEIO ---
fuso_br = timezone(timedelta(hours=-3)) 

def jogo_ja_comecou(horario_str):
    agora = datetime.now(fuso_br)
    try:
        partes = horario_str.split(" ")
        data_hora_str = f"{partes[1]} {partes[2]} {agora.year}"
        hora_jogo = datetime.strptime(data_hora_str, "%d/%m %H:%M %Y")
        hora_jogo = hora_jogo.replace(tzinfo=fuso_br)
        return agora >= hora_jogo
    except:
        return False 

# --- UTILITÁRIO DE TERMÔMETRO DAS APOSTAS ---
def gerar_termometro(id_jogo, df_palpites, t1, t2):
    palpites = df_palpites[df_palpites["jogo"] == id_jogo]
    total = len(palpites)
    if total == 0:
        return f"<div class='termometro'>📊 Termômetro: Seja o primeiro a palpitar!</div>"
    
    v1, v2, emp = 0, 0, 0
    for _, p in palpites.iterrows():
        try:
            g1, g2 = int(p["p1"]), int(p["p2"])
            if g1 > g2: v1 += 1
            elif g2 > g1: v2 += 1
            else: emp += 1
        except: pass
        
    pct1 = int((v1/total)*100)
    pct2 = int((v2/total)*100)
    pctE = int((emp/total)*100)
    
    return f"<div class='termometro'>📊 <b>Tendência:</b> {t1} {pct1}% | Empate {pctE}% | {t2} {pct2}%</div>"

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

@st.cache_data(ttl=3600)
def obter_imagem_local_base64(caminho_arquivo):
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, "rb") as arquivo_imagem:
            return base64.b64encode(arquivo_imagem.read()).decode()
    return None

@st.cache_data(ttl=3600)
def buscar_imagem_wikipedia(nome_artigo):
    try:
        nome_codificado = urllib.parse.quote(nome_artigo.replace(' ', '_'))
        url = f"https://pt.wikipedia.org/w/api.php?action=query&titles={nome_codificado}&prop=pageimages&format=json&pithumbsize=600"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            dados = json.loads(response.read().decode())
            paginas = dados.get('query', {}).get('pages', {})
            for page_id in paginas:
                if 'thumbnail' in paginas[page_id]:
                    return paginas[page_id]['thumbnail']['source']
        
        url_en = f"https://en.wikipedia.org/w/api.php?action=query&titles={nome_codificado}&prop=pageimages&format=json&pithumbsize=600"
        req_en = urllib.request.Request(url_en, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_en, timeout=3) as response_en:
            dados_en = json.loads(response_en.read().decode())
            paginas_en = dados_en.get('query', {}).get('pages', {})
            for page_id in paginas_en:
                if 'thumbnail' in paginas_en[page_id]:
                    return paginas_en[page_id]['thumbnail']['source']
    except:
        pass
    return "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"


# --- INICIALIZAR CONEXÃO E LER DADOS (COM BLINDAGEM) ---
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_aba(nome_aba, colunas_padrao):
    try:
        df = conn.read(worksheet=nome_aba, ttl=10)
        if df.empty:
            return pd.DataFrame(columns=colunas_padrao)
        return df
    except Exception as e:
        st.error(f"⚠️ Google Sheets falhou ao carregar a aba {nome_aba}. Por favor, recarregue a página.")
        st.stop()

df_jogos_sheet = ler_aba("Jogos", ["id", "time1", "flag1", "time2", "flag2", "gols1", "gols2", "passa", "encerrado", "horário"])

if "horário" not in df_jogos_sheet.columns: df_jogos_sheet["horário"] = ""
df_jogos_sheet["passa"] = df_jogos_sheet["passa"].astype(object)
df_jogos_sheet["encerrado"] = df_jogos_sheet["encerrado"].astype(object)

df_palpites = ler_aba("Palpites", ["nome", "jogo", "p1", "p2", "passa"])
df_usuarios = ler_aba("Usuarios", ["nome", "avatar"])

jogos_iniciais = [
    {"id": "Q1", "time1": "França", "flag1": "https://flagcdn.com/w160/fr.png", "time2": "Marrocos", "flag2": "https://flagcdn.com/w160/ma.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não", "horário": "Qui., 09/07 17:00"},
    {"id": "Q2", "time1": "Espanha", "flag1": "https://flagcdn.com/w160/es.png", "time2": "Bélgica", "flag2": "https://flagcdn.com/w160/be.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não", "horário": "Sex., 10/07 16:00"},
    {"id": "Q3", "time1": "Noruega", "flag1": "https://flagcdn.com/w160/no.png", "time2": "Inglaterra", "flag2": "https://flagcdn.com/w160/gb-eng.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não", "horário": "Sáb., 11/07 18:00"},
    {"id": "Q4", "time1": "Argentina", "flag1": "https://flagcdn.com/w160/ar.png", "time2": "Suíça", "flag2": "https://flagcdn.com/w160/ch.png", "gols1": 0, "gols2": 0, "passa": "", "encerrado": "Não", "horário": "Sáb., 11/07 22:00"}
]

ids_existentes = df_jogos_sheet["id"].tolist() if not df_jogos_sheet.empty else []
novos_jogos = [j for j in jogos_iniciais if j["id"] not in ids_existentes]
if novos_jogos:
    df_jogos_sheet = pd.concat([df_jogos_sheet, pd.DataFrame(novos_jogos)], ignore_index=True)
    conn.update(worksheet="Jogos", data=df_jogos_sheet)
    st.cache_data.clear()

dict_jogos = {}
for _, row in df_jogos_sheet.iterrows():
    if str(row["id"]).startswith("Q"):
        dict_jogos[row["id"]] = {
            "time1": row["time1"], "flag1": row["flag1"],
            "time2": row["time2"], "flag2": row["flag2"],
            "gols1": int(row.get("gols1", 0)) if pd.notna(row.get("gols1", 0)) else 0, 
            "gols2": int(row.get("gols2", 0)) if pd.notna(row.get("gols2", 0)) else 0,
            "passa": row.get("passa", ""), 
            "encerrado": str(row.get("encerrado", "Não")) == "Sim",
            "horário": row.get("horário", "Horário a definir")
        }

def calcular_pontos(jogo, palpite):
    try:
        p1, p2 = int(palpite["p1"]), int(palpite["p2"])
        r1, r2 = jogo["gols1"], jogo["gols2"]
        if p1 == r1 and p2 == r2: return 5
        return 0
    except: return 0

aba1, aba2, aba3 = st.tabs(["📊 Ranking", "✍️ Palpitar", "⚙️ Admin"])

# --- ABA 1: RANKING E SORTEIO DO JOGADOR ---
with aba1:
    imagem_base64 = obter_imagem_local_base64("ronaldinho.gif")
    if imagem_base64:
        st.markdown(f"<div style='text-align: center;'><img src='data:image/gif;base64,{imagem_base64}' class='imagem-topo-app'></div>", unsafe_allow_html=True)
    elif os.path.exists("ronaldinho.png"): st.image("ronaldinho.png", use_container_width=True)
    elif os.path.exists("ronaldinho.jpg"): st.image("ronaldinho.jpg", use_container_width=True)
    else: st.image("https://upload.wikimedia.org/wikipedia/commons/e/e0/Ronaldinho_11022007.jpg", use_container_width=True)
    
    st.markdown("<div class='player-draw-box'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #ffffff; margin-top: 0;'>🎲 Qual Jogador Você é Hoje?</h3>", unsafe_allow_html=True)
    
    if st.button("SORTEAR MEU JOGADOR", use_container_width=True):
        jogadores = [
            ("Ronaldinho Gaúcho", "Ronaldinho_Gaúcho"), ("Cássio", "Cássio_Ramos"), 
            ("Neymar Jr", "Neymar"), ("Cristiano Ronaldo", "Cristiano_Ronaldo"), 
            ("Lionel Messi", "Lionel_Messi"), ("Pelé", "Pelé"), 
            ("Marcelinho Carioca", "Marcelinho_Carioca"), ("Sócrates", "Sócrates_(futebolista)")
        ]
        nome_sorteado, titulo_wiki = random.choice(jogadores)
        imagem_sorteada = buscar_imagem_wikipedia(titulo_wiki)
        st.success(f"Você tirou: **{nome_sorteado}**")
        st.markdown(f"<img src='{imagem_sorteada}' class='imagem-jogador'>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.header("🏆 Classificação Geral (Quartas)")
    pontos_totais, cravadas_totais = {}, {}
    
    for _, p in df_palpites.iterrows():
        if str(p["jogo"]).startswith("Q"):
            nome = p["nome"]
            pontos_totais[nome] = pontos_totais.get(nome, 0)
            cravadas_totais[nome] = cravadas_totais.get(nome, 0)
            jogo = dict_jogos.get(p["jogo"])
            if jogo and jogo["encerrado"]:
                pontos = calcular_pontos(jogo, p)
                pontos_totais[nome] += pontos
                if pontos == 5: cravadas_totais[nome] += 1
            
    if pontos_totais:
        dados_ranking = []
        for n, pts in pontos_totais.items():
            user_row = df_usuarios[df_usuarios["nome"] == n]
            avatar = user_row["avatar"].values[0] if not user_row.empty else "👤"
            dados_ranking.append({"Participante": f"{avatar} {n}", "Pontos": pts, "Cravadas": cravadas_totais[n], "p_nome": n, "p_avatar": avatar})
            
        df_ranking = pd.DataFrame(dados_ranking).sort_values(by=["Pontos", "Cravadas"], ascending=[False, False]).reset_index(drop=True)
        
        for idx, row in df_ranking.iterrows():
            pos = idx + 1
            if pos == 1:
                st.markdown(f"<div class='top1-glow'>👑 1º LUGAR<br><span style='font-size: 2rem;'>{row['p_avatar']} <b>{row['p_nome']}</b></span><br>{row['Pontos']} pts <br><span style='font-size: 0.9rem; color: #FFDF00;'>({row['Cravadas']} Cravadas)</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='ranking-normal'><b>{pos}º</b> {row['p_avatar']} {row['p_nome']} — <b>{row['Pontos']} pts</b></div>", unsafe_allow_html=True)
        
        st.divider()
        st.subheader("👀 Espiar Adversários")
        usuarios_com_palpite = df_palpites[df_palpites["jogo"].str.startswith("Q")]["nome"].unique()
        for nome_participante in usuarios_com_palpite:
            user_info = df_usuarios[df_usuarios["nome"] == nome_participante]
            avatar_part = user_info["avatar"].values[0] if not user_info.empty else "👤"
            with st.expander(f"{avatar_part} {nome_participante}"):
                palpites_do_cara = df_palpites[df_palpites["nome"] == nome_participante]
                texto_palpites = f"📝 *PALPITES - QUARTAS* 📝\n\n"
                for id_jogo, j in dict_jogos.items():
                    p_jogo = palpites_do_cara[palpites_do_cara["jogo"] == id_jogo]
                    if not p_jogo.empty:
                        val_p1, val_p2, val_passa = int(p_jogo.iloc[0]["p1"]), int(p_jogo.iloc[0]["p2"]), p_jogo.iloc[0]["passa"]
                        texto_palpites += f"{j['time1']} {val_p1} x {val_p2} {j['time2']}"
                        if val_p1 == val_p2 and val_passa: texto_palpites += f" (Pênaltis: {val_passa})"
                        texto_palpites += "\n"
                st.code(texto_palpites, language="text")
    else:
        st.info("Aguardando resultados da fase de Quartas!")

# --- ABA 2: DAR PALPITE ---
with aba2:
    st.header("✍️ Dar Palpite")
    
    if "nome_salvo" not in st.session_state: st.session_state.nome_salvo = ""
    nome_usuario = st.text_input("Seu Nome/Apelido:", value=st.session_state.nome_salvo, key="user_nome").strip().title()
    
    if nome_usuario:
        st.session_state.nome_salvo = nome_usuario
        user_row = df_usuarios[df_usuarios["nome"] == nome_usuario]
        avatar_atual = user_row["avatar"].values[0] if not user_row.empty else lista_avatares[0]
        
        # Formulário para salvar avatar sem dar refresh doido na tela
        with st.form("form_avatar"):
            c1, c2 = st.columns([3, 1])
            with c1: avatar_escolhido = st.selectbox("Escolha seu Avatar:", lista_avatares, index=lista_avatares.index(avatar_atual))
            with c2: 
                st.markdown("<br>", unsafe_allow_html=True)
                salvar_avatar = st.form_submit_button("Salvar")
                
            if salvar_avatar:
                try:
                    df_usuarios_safe = conn.read(worksheet="Usuarios", ttl=0)
                    if nome_usuario not in df_usuarios_safe["nome"].values:
                        nova_linha = pd.DataFrame([{"nome": nome_usuario, "avatar": avatar_escolhido}])
                        df_usuarios_safe = pd.concat([df_usuarios_safe, nova_linha], ignore_index=True)
                    else:
                        df_usuarios_safe.loc[df_usuarios_safe["nome"] == nome_usuario, "avatar"] = avatar_escolhido
                    conn.update(worksheet="Usuarios", data=df_usuarios_safe)
                    st.cache_data.clear()
                    st.success("Avatar salvo!")
                except: pass
            
        st.markdown(f'<div class="avatar-grande-display">{avatar_escolhido}</div>', unsafe_allow_html=True)
        st.divider()
        
        for id_jogo, j in dict_jogos.items():
            if j["encerrado"]: continue
            
            # REMOVIDO: clear_on_submit=True (Para não apagar os dados se o usuário esquecer o penalti)
            with st.form(key=f"form_{id_jogo}"):
                st.markdown(f'<p style="text-align: center; color: #FFDF00 !important; font-size: 1.1rem; font-weight: bold; margin-bottom: 0px;">📅 {j["horário"]}</p>', unsafe_allow_html=True)
                st.markdown(gerar_termometro(id_jogo, df_palpites, j["time1"], j["time2"]), unsafe_allow_html=True)
                st.markdown(f'<h4 style="text-align: center; color: #ffffff !important; margin-top: 5px;">{j["time1"]} x {j["time2"]}</h4>', unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1: p1 = st.number_input(f"Gols {j['time1']}", min_value=0, step=1)
                with c2: p2 = st.number_input(f"Gols {j['time2']}", min_value=0, step=1)
                    
                st.caption("Pênaltis (Marque apenas se o seu placar for um empate):")
                opcao_sem_penalti = "Sem Pênaltis (Não empatou)"
                passa = st.selectbox("", [opcao_sem_penalti, j['time1'], j['time2']], label_visibility="collapsed")
                
                bloqueado = jogo_ja_comecou(j["horário"])
                if bloqueado:
                    submit_palpite = st.form_submit_button("Apostas Encerradas (Horário passou)", disabled=True, use_container_width=True)
                else:
                    submit_palpite = st.form_submit_button("Gravar Palpite", type="primary", use_container_width=True)
                
                if submit_palpite and not bloqueado:
                    if p1 == p2 and passa == opcao_sem_penalti:
                        st.error("⚠️ Você colocou um empate! Escolha quem vence nos pênaltis antes de gravar.")
                    elif p1 != p2 and passa != opcao_sem_penalti:
                        st.error("⚠️ O jogo não empatou. Marque 'Sem Pênaltis'.")
                    else:
                        st.cache_data.clear()
                        try:
                            df_palpites_safe = conn.read(worksheet="Palpites", ttl=0)
                            if df_palpites_safe.empty: df_palpites_safe = pd.DataFrame(columns=["nome", "jogo", "p1", "p2", "passa"])
                            df_palpites_safe = df_palpites_safe[~((df_palpites_safe["nome"] == nome_usuario) & (df_palpites_safe["jogo"] == id_jogo))]
                            passa_final = passa if passa != opcao_sem_penalti else ""
                            novo_p = pd.DataFrame([{"nome": nome_usuario, "jogo": id_jogo, "p1": p1, "p2": p2, "passa": passa_final}])
                            df_palpites_safe = pd.concat([df_palpites_safe, novo_p], ignore_index=True)
                            conn.update(worksheet="Palpites", data=df_palpites_safe)
                            st.cache_data.clear()
                            st.balloons()
                            st.success("✅ Palpite gravado no banco de dados!")
                        except:
                            st.error("Falha na conexão com o banco. Tente novamente.")
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("Digite o seu nome para exibir os confrontos.")

# --- ABA 3: ADMIN ---
with aba3:
    st.header("⚙️ Painel Administrador")
    
    st.subheader("📝 Lançar Resultados Reais")
    for id_jogo, j in dict_jogos.items():
        with st.form(key=f"adm_form_{id_jogo}"):
            st.markdown(f"**{j['time1']} x {j['time2']}**")
            c1, c2 = st.columns(2)
            with c1: g1 = st.number_input(f"Gols {j['time1']}", min_value=0, step=1, value=j["gols1"])
            with c2: g2 = st.number_input(f"Gols {j['time2']}", min_value=0, step=1, value=j["gols2"])
                
            opcao_sem_penalti_adm = "Sem Pênaltis"
            passa_real = st.selectbox("Pênaltis:", [opcao_sem_penalti_adm, j['time1'], j['time2']])
            encerrar = st.checkbox("Encerrar jogo e travar palpites", value=j["encerrado"])
            submit_adm = st.form_submit_button("Gravar Placar Oficial", use_container_width=True)
            
            if submit_adm:
                st.cache_data.clear()
                try:
                    df_jogos_safe = conn.read(worksheet="Jogos", ttl=0)
                    passa_final_adm = passa_real if passa_real != opcao_sem_penalti_adm else ""
                    df_jogos_safe.loc[df_jogos_safe["id"] == id_jogo, "gols1"] = g1
                    df_jogos_safe.loc[df_jogos_safe["id"] == id_jogo, "gols2"] = g2
                    df_jogos_safe.loc[df_jogos_safe["id"] == id_jogo, "passa"] = passa_final_adm
                    df_jogos_safe.loc[df_jogos_safe["id"] == id_jogo, "encerrado"] = "Sim" if encerrar else "Não"
                    conn.update(worksheet="Jogos", data=df_jogos_safe)
                    st.cache_data.clear()
                    st.success("Placar atualizado!")
                except:
                    st.error("Erro na leitura do banco. Placar NÃO foi gravado. Tente novamente.")
