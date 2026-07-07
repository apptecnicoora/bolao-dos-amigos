import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import random
import os
import json
import urllib.request
import urllib.parse
import base64

# Configuração mobile-first
st.set_page_config(page_title="Bolão das Quartas", page_icon="⚽", layout="centered")

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

st.title("⚽ BOLÃO ONLINE DAS QUARTAS")
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

# --- MOTOR DE BUSCA DA WIKIPEDIA (BLINDADO) ---
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

if "horário" not in df_jogos_sheet.columns:
    df_jogos_sheet["horário"] = ""

df_jogos_sheet["passa"] = df_jogos_sheet["passa"].astype(object)
df_jogos_sheet["encerrado"] = df_jogos_sheet["encerrado"].astype(object)

df_palpites = ler_aba("Palpites", ["nome", "jogo", "p1", "p2", "passa"])
df_usuarios = ler_aba("Usuarios", ["nome", "avatar"])

# --- JOGOS DAS QUARTAS DE FINAL ---
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
    # Carrega apenas os jogos com ID Q (Quartas)
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

# --- REGRA HARDCORE: APENAS PLACAR EXATO GANHA 5 PONTOS ---
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
        st.markdown(f"""
        <div style='text-align: center;'>
            <img src="data:image/gif;base64,{imagem_base64}" class="imagem-topo-app" alt="Ronaldinho Dançando">
        </div>
        """, unsafe_allow_html=True)
    elif os.path.exists("ronaldinho.png"):
        st.image("ronaldinho.png", use_container_width=True)
    elif os.path.exists("ronaldinho.jpg"):
        st.image("ronaldinho.jpg", use_container_width=True)
    else:
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e0/Ronaldinho_11022007.jpg", use_container_width=True)
    
    st.markdown("<div class='player-draw-box'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #ffffff; margin-top: 0;'>🎲 Qual Jogador Você é Hoje?</h3>", unsafe_allow_html=True)
    st.write("Aperte o botão para descobrir sua energia para os palpites!")
    
    if st.button("SORTEAR MEU JOGADOR", use_container_width=True):
        jogadores = [
            ("Ronaldinho Gaúcho (O Bruxo)", "Ronaldinho_Gaúcho"),
            ("Cássio (O Paredão)", "Cássio_Ramos"),
            ("Neymar Jr", "Neymar"),
            ("Cristiano Ronaldo", "Cristiano_Ronaldo"),
            ("Lionel Messi", "Lionel_Messi"),
            ("Pelé (O Rei)", "Pelé"),
            ("Diego Maradona", "Diego_Maradona"),
            ("Ronaldo Fenômeno", "Ronaldo_Nazário"),
            ("Sócrates (O Doutor)", "Sócrates_(futebolista)"),
            ("Marcelinho Carioca", "Marcelinho_Carioca"),
            ("Craque Neto", "Neto_(futebolista)"),
            ("Rivellino", "Roberto_Rivellino"),
            ("Paulinho", "Paulinho_(futebolista)"),
            ("Renato Augusto", "Renato_Augusto"),
            ("Paolo Guerrero", "Paolo_Guerrero"),
            ("Dida", "Dida_(futebolista_nascido_em_1973)"),
            ("Vampeta", "Vampeta"),
            ("Edílson Capetinha", "Edílson"),
            ("Carlos Tevez", "Carlos_Tevez"),
            ("Zinedine Zidane", "Zinedine_Zidane"),
            ("Romário", "Romário"),
            ("Zico", "Zico"),
            ("Kaká", "Kaká"),
            ("Kylian Mbappé", "Kylian_Mbappé"),
            ("Erling Haaland", "Erling_Haaland"),
            ("Kevin De Bruyne", "Kevin_De_Bruyne"),
            ("Robert Lewandowski", "Robert_Lewandowski"),
            ("Zlatan Ibrahimović", "Zlatan_Ibrahimović"),
            ("Gianluigi Buffon", "Gianluigi_Buffon"),
            ("Roberto Carlos", "Roberto_Carlos"),
            ("Johan Cruyff", "Johan_Cruyff"),
            ("Franz Beckenbauer", "Franz_Beckenbauer"),
            ("Michel Platini", "Michel_Platini"),
            ("Thierry Henry", "Thierry_Henry"),
            ("Andrés Iniesta", "Andrés_Iniesta"),
            ("Xavi", "Xavi"),
            ("Sergio Ramos", "Sergio_Ramos"),
            ("Iker Casillas", "Iker_Casillas"),
            ("Luka Modrić", "Luka_Modrić"),
            ("Karim Benzema", "Karim_Benzema"),
            ("Luis Suárez", "Luis_Suárez"),
            ("Gareth Bale", "Gareth_Bale"),
            ("Wayne Rooney", "Wayne_Rooney"),
            ("Ryan Giggs", "Ryan_Giggs"),
            ("Paul Scholes", "Paul_Scholes"),
            ("Steven Gerrard", "Steven_Gerrard"),
            ("Frank Lampard", "Frank_Lampard"),
            ("Didier Drogba", "Didier_Drogba"),
            ("Samuel Eto'o", "Samuel_Eto'o"),
            ("Yaya Touré", "Yaya_Touré"),
            ("Mohamed Salah", "Mohamed_Salah"),
            ("Sadio Mané", "Sadio_Mané"),
            ("Riyad Mahrez", "Riyad_Mahrez"),
            ("George Weah", "George_Weah"),
            ("Eusébio", "Eusébio"),
            ("Lev Yashin", "Lev_Yashin"),
            ("Ferenc Puskás", "Ferenc_Puskás"),
            ("Alfredo Di Stéfano", "Alfredo_Di_Stéfano"),
            ("Garrincha", "Garrincha"),
            ("Jairzinho", "Jairzinho"),
            ("Tostão", "Tostão"),
            ("Gérson", "Gérson"),
            ("Carlos Alberto Torres", "Carlos_Alberto_Torres"),
            ("Cafu", "Cafu"),
            ("Rivaldo", "Rivaldo"),
            ("Bebeto", "Bebeto"),
            ("Cláudio Taffarel", "Cláudio_Taffarel"),
            ("Marcos (Goleiro)", "Marcos_(futebolista)"),
            ("Rogério Ceni", "Rogério_Ceni"),
            ("Alisson Becker", "Alisson_Becker"),
            ("Ederson Moraes", "Ederson_Moraes"),
            ("Virgil van Dijk", "Virgil_van_Dijk"),
            ("Trent Alexander-Arnold", "Trent_Alexander-Arnold"),
            ("Alphonso Davies", "Alphonso_Davies"),
            ("Achraf Hakimi", "Achraf_Hakimi"),
            ("N'Golo Kanté", "N'Golo_Kanté"),
            ("Casemiro", "Casemiro"),
            ("Toni Kroos", "Toni_Kroos"),
            ("Sergio Busquets", "Sergio_Busquets"),
            ("Pedri", "Pedri"),
            ("Jude Bellingham", "Jude_Bellingham"),
            ("Vinícius Júnior", "Vinícius_Júnior"),
            ("Rodrygo", "Rodrygo"),
            ("Phil Foden", "Phil_Foden"),
            ("Bukayo Saka", "Bukayo_Saka"),
            ("Harry Kane", "Harry_Kane"),
            ("Son Heung-min", "Son_Heung-min"),
            ("Antoine Griezmann", "Antoine_Griezmann"),
            ("Olivier Giroud", "Olivier_Giroud"),
            ("Hugo Lloris", "Hugo_Lloris"),
            ("Manuel Neuer", "Manuel_Neuer"),
            ("Thomas Müller", "Thomas_Müller"),
            ("Joshua Kimmich", "Joshua_Kimmich"),
            ("Jamal Musiala", "Jamal_Musiala"),
            ("Leroy Sané", "Leroy_Sané"),
            ("Serge Gnabry", "Serge_Gnabry"),
            ("İlkay Gündoğan", "İlkay_Gündoğan"),
            ("Christian Pulisic", "Christian_Pulisic"),
            ("Keylor Navas", "Keylor_Navas"),
            ("Roberto Baggio", "Roberto_Baggio")
        ]
        
        nome_sorteado, titulo_wiki = random.choice(jogadores)
        
        with st.spinner("Puxando foto oficial..."):
            imagem_sorteada = buscar_imagem_wikipedia(titulo_wiki)
        
        st.success(f"Você tirou: **{nome_sorteado}**")
        st.markdown(f"<img src='{imagem_sorteada}' class='imagem-jogador'>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

    st.header("🏆 Classificação Geral (Quartas)")
    pontos_totais = {}
    
    for _, p in df_palpites.iterrows():
        # Filtra para somar apenas os jogos das quartas (iniciados com Q)
        if str(p["jogo"]).startswith("Q"):
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
        texto_whatsapp = "🏆 *CLASSIFICAÇÃO DO BOLÃO (QUARTAS)* 🏆\n\n"
        for idx, row in df_ranking.iterrows():
            texto_whatsapp += f"{idx+1}º {row['p_avatar']} *{row['p_nome']}* — {row['Pontos']} pts\n"
        st.code(texto_whatsapp, language="text")

        st.divider()
        st.subheader("👀 Espiar Adversários")
        st.caption("Clique no nome do participante abaixo para ver os palpites dele.")
        
        usuarios_com_palpite = df_palpites[df_palpites["jogo"].str.startswith("Q")]["nome"].unique()
        for nome_participante in usuarios_com_palpite:
            user_info = df_usuarios[df_usuarios["nome"] == nome_participante]
            avatar_part = user_info["avatar"].values[0] if not user_info.empty else "👤"
            
            with st.expander(f"{avatar_part} {nome_participante}"):
                palpites_do_cara = df_palpites[df_palpites["nome"] == nome_participante]
                
                texto_palpites = f"📝 *PALPITES - QUARTAS* 📝\n\n"
                
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
        st.info("Aguardando palpites e resultados da fase de Quartas!")

# --- ABA 2: DAR PALPITE ---
with aba2:
    st.header("✍️ Dar Palpite")
    nome_usuario = st.text_input("Seu Nome/Apelido:", key="user_nome").strip().title()
    
    if nome_usuario:
        user_row = df_usuarios[df_usuarios["nome"] == nome_usuario]
        avatar_atual = user_row["avatar"].values[0] if not user_row.empty else lista_avatares[0]
        avatar_escolhido = st.selectbox("Escolha seu Avatar:", lista_avatares, index=lista_avatares.index(avatar_atual))
        
        if user_row.empty:
            st.cache_data.clear()
            try:
                df_usuarios_safe = conn.read(worksheet="Usuarios", ttl=0)
                nova_linha = pd.DataFrame([{"nome": nome_usuario, "avatar": avatar_escolhido}])
                df_usuarios_safe = pd.concat([df_usuarios_safe, nova_linha], ignore_index=True)
                conn.update(worksheet="Usuarios", data=df_usuarios_safe)
            except:
                st.error("Erro ao conectar no banco para salvar usuário. Tente novamente.")
            st.cache_data.clear()
            st.rerun()
            
        elif avatar_atual != avatar_escolhido:
            st.cache_data.clear()
            try:
                df_usuarios_safe = conn.read(worksheet="Usuarios", ttl=0)
                df_usuarios_safe.loc[df_usuarios_safe["nome"] == nome_usuario, "avatar"] = avatar_escolhido
                conn.update(worksheet="Usuarios", data=df_usuarios_safe)
            except:
                st.error("Erro ao conectar no banco para atualizar avatar.")
            st.cache_data.clear()
            st.rerun()
            
        st.markdown(f'<div class="avatar-grande-display">{avatar_escolhido}</div>', unsafe_allow_html=True)
        st.divider()
        
        for id_jogo, j in dict_jogos.items():
            if j["encerrado"]: continue
            
            with st.form(key=f"form_{id_jogo}"):
                # DATA E HORA EM CIMA
                st.markdown(f'<p style="text-align: center; color: #FFDF00 !important; font-size: 1.1rem; font-weight: bold; margin-bottom: 0px;">📅 {j["horário"]}</p>', unsafe_allow_html=True)
                st.markdown(f'<h4 style="text-align: center; color: #ffffff !important; margin-top: 5px;">{j["time1"]} x {j["time2"]}</h4>', unsafe_allow_html=True)
                
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
                        st.cache_data.clear()
                        try:
                            df_palpites_safe = conn.read(worksheet="Palpites", ttl=0)
                        except Exception as e:
                            st.error("Falha na conexão com o banco. O palpite NÃO foi gravado para proteger os dados. Tente novamente.")
                            st.stop()
                            
                        if df_palpites_safe.empty:
                            df_palpites_safe = pd.DataFrame(columns=["nome", "jogo", "p1", "p2", "passa"])
                            
                        df_palpites_safe = df_palpites_safe[~((df_palpites_safe["nome"] == nome_usuario) & (df_palpites_safe["jogo"] == id_jogo))]
                        
                        passa_final = passa if passa != opcao_sem_penalti else ""
                        novo_p = pd.DataFrame([{"nome": nome_usuario, "jogo": id_jogo, "p1": p1, "p2": p2, "passa": passa_final}])
                        
                        df_palpites_safe = pd.concat([df_palpites_safe, novo_p], ignore_index=True)
                        
                        conn.update(worksheet="Palpites", data=df_palpites_safe)
                        st.cache_data.clear()
                        st.success("Gravado com sucesso no sistema!")
                        st.rerun() 
            st.markdown("<br>", unsafe_allow_html=True)
            
        palpites_usuario = df_palpites[df_palpites["nome"] == nome_usuario]
        if not palpites_usuario.empty:
            st.subheader("📲 Meus Palpites para o WhatsApp")
            texto_meus_palpites = f"📝 *MEUS PALPITES - QUARTAS* 📝\n"
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
            st.cache_data.clear()
            try:
                df_usuarios_safe = conn.read(worksheet="Usuarios", ttl=0)
                df_palpites_safe = conn.read(worksheet="Palpites", ttl=0)
                
                df_usuarios_safe = df_usuarios_safe[df_usuarios_safe["nome"] != usuario_remover]
                df_palpites_safe = df_palpites_safe[df_palpites_safe["nome"] != usuario_remover]
                
                conn.update(worksheet="Usuarios", data=df_usuarios_safe)
                conn.update(worksheet="Palpites", data=df_palpites_safe)
                st.cache_data.clear()
                st.success(f"Usuário {usuario_remover} removido com sucesso!")
                st.rerun()
            except:
                st.error("Erro de conexão ao tentar apagar usuário.")
        
    st.divider()
    
    st.subheader("📝 Lançar Resultados Reais")
    for id_jogo, j in dict_jogos.items():
        with st.form(key=f"adm_form_{id_jogo}"):
            st.markdown(f'<p style="text-align: left; color: #FFDF00 !important; font-size: 0.9rem; font-weight: bold; margin-bottom: 0px;">📅 {j["horário"]}</p>', unsafe_allow_html=True)
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
                st.cache_data.clear()
                try:
                    df_jogos_safe = conn.read(worksheet="Jogos", ttl=0)
                except:
                    st.error("Erro na leitura do banco. Placar NÃO foi gravado. Tente novamente.")
                    st.stop()
                    
                passa_final_adm = passa_real if passa_real != opcao_sem_penalti_adm else ""
                
                df_jogos_safe.loc[df_jogos_safe["id"] == id_jogo, "gols1"] = g1
                df_jogos_safe.loc[df_jogos_safe["id"] == id_jogo, "gols2"] = g2
                df_jogos_safe.loc[df_jogos_safe["id"] == id_jogo, "passa"] = passa_final_adm
                df_jogos_safe.loc[df_jogos_safe["id"] == id_jogo, "encerrado"] = "Sim" if encerrar else "Não"
                
                conn.update(worksheet="Jogos", data=df_jogos_safe)
                st.cache_data.clear()
                st.success("Placar oficial atualizado com sucesso!")
                st.rerun()
