import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import random
import os
import base64
from datetime import datetime, timezone, timedelta

# Configuração da página - Otimizada para Celular
st.set_page_config(page_title="Bolão das Quartas", page_icon="⚽", layout="centered")

# --- CSS CUSTOMIZADO: TEMA ESCURO COM NEON BRASIL ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117 !important; color: #ffffff !important; }
    h1, h2, h3, h4, h5 { color: #009B3A !important; }
    h1, h2, h3, h4, h5, p, span, label, .stMarkdown { color: #ffffff !important; }
    
    .main .block-container { max-width: 480px; padding-top: 1rem; padding-left: 0.8rem; padding-right: 0.8rem; }
    
    .card-jogo {
        background-color: #161a22;
        border: 2px solid #009B3A;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        box-shadow: 0 0 10px rgba(0, 155, 58, 0.2);
    }
    
    .stButton > button {
        background-color: #009B3A !important;
        color: #FFDF00 !important;
        border: 2px solid #FFDF00 !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        width: 100% !important;
        height: 50px !important;
    }
    
    .top1-glow {
        background: linear-gradient(145deg, #1f242e, #161a22);
        border: 2px solid #FFDF00;
        box-shadow: 0 0 20px 5px rgba(255, 223, 0, 0.5);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .ranking-normal {
        background-color: #161a22;
        border-left: 5px solid #009B3A;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    
    .termometro {
        font-size: 0.8rem;
        text-align: center;
        color: #8b949e;
        background-color: #202632;
        border-radius: 6px;
        padding: 4px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM O GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def ler_aba(nome_aba, colunas_padrao):
    try:
        df = conn.read(worksheet=nome_aba, ttl=5)
        if df is None or df.empty:
            return pd.DataFrame(columns=colunas_padrao)
        return df
    except:
        return pd.DataFrame(columns=colunas_padrao)

# Carrega os dados estruturados
df_jogos = ler_aba("Jogos", ["id", "time1", "flag1", "time2", "flag2", "gols1", "gols2", "passa", "encerrado", "horário"])
df_palpites = ler_aba("Palpites", ["nome", "jogo", "p1", "p2", "passa"])
df_usuarios = ler_aba("Usuarios", ["nome", "avatar"])

# Configurações de fuso horário para Teresina/Brasília
fuso_br = timezone(timedelta(hours=-3))
def jogo_ja_comecou(horario_str):
    try:
        partes = horario_str.split(" ")
        agora = datetime.now(fuso_br)
        data_hora_str = f"{partes[1]} {partes[2]} {agora.year}"
        hora_jogo = datetime.strptime(data_hora_str, "%d/%m %H:%M %Y").replace(tzinfo=fuso_br)
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
    
    return f"<div class='termometro'>📊 <b>Tendência do Grupo:</b> {t1} {pct1}% | Empate {pctE}% | {t2} {pct2}%</div>"

bandeiras_emoji = {
    "Canadá": "🇨🇦", "Marrocos": "🇲🇦", "Brasil": "🇧🇷", "Noruega": "🇳🇴",
    "Portugal": "🇵🇹", "Espanha": "🇪🇸", "Paraguai": "🇵🇾", "França": "🇫🇷",
    "México": "🇲🇽", "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "EUA": "🇺🇸", "Bélgica": "🇧🇪",
    "Argentina": "🇦🇷", "Egito": "🇪🇬", "Suíça": "🇨🇭", "Colômbia": "🇨🇴"
}

cores_paises = {
    "Canadá": "#FF0000", "Marrocos": "#C1272D", "Brasil": "#009B3A", "Noruega": "#BA0C2F",
    "Portugal": "#FF0000", "Espanha": "#AA151B", "Paraguai": "#0038A8", "França": "#002395",
    "México": "#006341", "Inglaterra": "#CF081F", "EUA": "#3C3B6E", "Bélgica": "#ED2939",
    "Argentina": "#43A1D5", "Egito": "#CE1126", "Suíça": "#FF0000", "Colômbia": "#FCD116"
}

# Dicionário de jogos rápido para as quartas
dict_jogos = {}
df_q_jogos_all = df_jogos[df_jogos["id"].str.startswith("Q", na=False)]
for _, row in df_q_jogos_all.iterrows():
    dict_jogos[row["id"]] = {
        "time1": row["time1"], "flag1": row["flag1"],
        "time2": row["time2"], "flag2": row["flag2"],
        "gols1": int(row.get("gols1", 0)) if pd.notna(row.get("gols1", 0)) else 0, 
        "gols2": int(row.get("gols2", 0)) if pd.notna(row.get("gols2", 0)) else 0,
        "passa": row.get("passa", ""), 
        "encerrado": str(row.get("encerrado", "Não")) == "Sim",
        "horário": row.get("horário", "Horário a definir")
    }

# --- MENU DE NAVEGAÇÃO ---
if "pagina" not in st.session_state:
    st.session_state.pagina = "📊 Ranking"

col_nav1, col_nav2, col_nav3 = st.columns(3)
with col_nav1:
    if st.button("📊 Ranking"): st.session_state.pagina = "📊 Ranking"
with col_nav2:
    if st.button("✍️ Palpitar"): st.session_state.pagina = "✍️ Palpitar"
with col_nav3:
    if st.button("⚙️ Admin"): st.session_state.pagina = "⚙️ Admin"

st.divider()

# ==================== PAGINA 1: RANKING ====================
if st.session_state.pagina == "📊 Ranking":
    st.header("🏆 Classificação Geral")
    
    if os.path.exists("ronaldinho.gif"):
        with open("ronaldinho.gif", "rb") as f:
            st.markdown(f"<div style='text-align:center'><img src='data:image/gif;base64,{base64.b64encode(f.read()).decode()}' style='width:100%; border-radius:12px; border:2px solid #009B3A;'></div><br>", unsafe_allow_html=True)
    else:
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e0/Ronaldinho_11022007.jpg", use_container_width=True)

    st.markdown("<div style='background-color:#161a22; padding:15px; border-radius:12px; border:1px solid #FFDF00; text-align:center;'>", unsafe_allow_html=True)
    st.subheader("🎲 Qual craque você é hoje?")
    if st.button("SORTEAR MEU JOGADOR"):
        craques = ["Ronaldinho Gaúcho 🧙‍♂️", "Cássio Ramos 🧱", "Neymar Jr ⚡", "Ronaldo Fenômeno 🔥", "Sócrates 🧠", "Marcelinho Carioca 🎯", "Craque Neto 🦅", "Lionel Messi 👑", "Cristiano Ronaldo 🤖"]
        st.success(f"Você está com a energia de: **{random.choice(craques)}**!")
    st.markdown("</div><br>", unsafe_allow_html=True)

    pontos_totais = {}
    cravadas_totais = {}
    
    for _, p in df_palpites.iterrows():
        if str(p["jogo"]).startswith("Q"):
            nome = p["nome"]
            pontos_totais[nome] = pontos_totais.get(nome, 0)
            cravadas_totais[nome] = cravadas_totais.get(nome, 0)
            
            jogo = dict_jogos.get(p["jogo"])
            if jogo is not None and jogo["encerrado"]:
                if int(p["p1"]) == int(jogo["gols1"]) and int(p["p2"]) == int(jogo["gols2"]):
                    pontos_totais[nome] += 5
                    cravadas_totais[nome] += 1

    if pontos_totais:
        dados_ranking = []
        for n, pts in pontos_totais.items():
            u_row = df_usuarios[df_usuarios["nome"] == n]
            av = u_row["avatar"].values[0] if not u_row.empty else "👤"
            dados_ranking.append({"Nome": n, "Pontos": pts, "Cravadas": cravadas_totais.get(n, 0), "Avatar": av})
            
        df_r = pd.DataFrame(dados_ranking).sort_values(by=["Pontos", "Cravadas"], ascending=[False, False]).reset_index(drop=True)
        
        for idx, row in df_r.iterrows():
            if idx == 0:
                st.markdown(f"<div class='top1-glow'>👑 <b>1º LUGAR</b><br><span style='font-size:1.5rem;'>{row['Avatar']} {row['Nome']}</span><br><b>{row['Pontos']} Pontos</b> ({row['Cravadas']} cravadas)</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='ranking-normal'><b>{idx+1}º</b> {row['Avatar']} {row['Nome']} — <b>{row['Pontos']} pts</b> <span style='font-size:0.8rem; color:#8b949e;'>({row['Cravadas']} cr)</span></div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum resultado computado ainda para as Quartas.")

# ==================== PAGINA 2: PALPITAR ====================
elif st.session_state.pagina == "✍️ Palpitar":
    st.header("✍️ Registrar Seus Palpites")
    
    if "nome_usuario" not in st.session_state: st.session_state.nome_usuario = ""
    nome_input = st.text_input("Digite seu Nome/Apelido:", value=st.session_state.nome_usuario).strip().title()
    
    if nome_input:
        st.session_state.nome_usuario = nome_input
        
        if nome_input not in df_usuarios["nome"].values:
            novo_u = pd.DataFrame([{"nome": nome_input, "avatar": "⚽"}])
            df_usuarios = pd.concat([df_usuarios, novo_u], ignore_index=True)
            conn.update(worksheet="Usuarios", data=df_usuarios)
            
        st.success(f"Conectado como: {nome_input}")
        
        # --- FORMULÁRIO ÚNICO EM BLOCK ---
        with st.form(key="formulario_global_quartas"):
            st.markdown("<p style='color:#FFDF00; text-align:center; font-weight:bold;'>Preencha todos os jogos e clique em 'SALVAR' no final da página:</p>", unsafe_allow_html=True)
            
            df_q_jogos = df_jogos[df_jogos["id"].str.startswith("Q", na=False)]
            dados_do_formulario = []
            
            for _, j in df_q_jogos.iterrows():
                id_j = j["id"]
                
                st.markdown(f"""
                <div class='card-jogo'>
                    <div style='text-align:center; color:#FFDF00; font-weight:bold; font-size:1.1rem;'>📅 {j['horário']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Exibição de Bandeiras e Nomes usando colunas dentro do formulário
                col_t1, col_vs, col_t2 = st.columns([2, 1, 2])
                cor_t1 = cores_paises.get(j["time1"], "#009B3A")
                cor_t2 = cores_paises.get(j["time2"], "#009B3A")
                
                with col_t1:
                    st.markdown(f"<div style='text-align: right;'><img src='{j['flag1']}' width='55' style='border-radius: 4px; box-shadow: 0 0 8px {cor_t1};'><br><b>{j['time1']}</b></div>", unsafe_allow_html=True)
                with col_vs:
                    st.markdown("<h4 style='text-align: center; margin-top: 10px;'>VS</h4>", unsafe_allow_html=True)
                with col_t2:
                    st.markdown(f"<div style='text-align: left;'><img src='{j['flag2']}' width='55' style='border-radius: 4px; box-shadow: 0 0 8px {cor_t2};'><br><b>{j['time2']}</b></div>", unsafe_allow_html=True)
                
                # Termômetro de tendência do grupo
                st.markdown(gerar_termometro(id_j, df_palpites, j["time1"], j["time2"]), unsafe_allow_html=True)
                
                # Inputs de placar
                c1, c2 = st.columns(2)
                with c1: g1 = st.number_input(f"Gols {j['time1']}", min_value=0, step=1, key=f"g1_{id_j}")
                with c2: g2 = st.number_input(f"Gols {j['time2']}", min_value=0, step=1, key=f"g2_{id_j}")
                
                passa = st.selectbox(f"Quem se classifica (Caso dê empate)?", ["Não empatou", j['time1'], j['time2']], key=f"passa_{id_j}")
                st.markdown("<br><hr style='border:1px dashed #30363d'><br>", unsafe_allow_html=True)
                
                dados_do_formulario.append({"id": id_j, "g1": g1, "g2": g2, "passa": passa, "horario": j["horário"], "t1": j["time1"], "t2": j["time2"]})
            
            botao_gravar = st.form_submit_button("💾 SALVAR TODOS OS MEUS PALPITES")
            
            if botao_gravar:
                erros = []
                novos_palpites_lista = []
                
                for item in dados_do_formulario:
                    if jogo_ja_comecou(item["horario"]):
                        continue
                        
                    if item["g1"] == item["g2"] and item["passa"] == "Não empatou":
                        erros.append(f"Faltou escolher quem passa nos pênaltis em {item['t1']} x {item['t2']}!")
                    elif item["g1"] != item["g2"] and item["passa"] != "Não empatou":
                        erros.append(f"O jogo {item['t1']} x {item['t2']} não terminou empatado, ajuste o campo de classificação.")
                    else:
                        passa_final = item["passa"] if item["passa"] != "Não empatou" else ""
                        novos_palpites_lista.append({"nome": nome_input, "jogo": item["id"], "p1": int(item["g1"]), "p2": int(item["g2"]), "passa": passa_final})
                
                if erros:
                    for err in erros: st.error(err)
                else:
                    try:
                        df_p_safe = conn.read(worksheet="Palpites", ttl=0)
                        if df_p_safe is None: df_p_safe = pd.DataFrame(columns=["nome", "jogo", "p1", "p2", "passa"])
                        df_p_safe = df_p_safe[~((df_p_safe["nome"] == nome_input) & (df_p_safe["jogo"].str.startswith("Q")))]
                        
                        df_novos = pd.DataFrame(novos_palpites_lista)
                        df_final = pd.concat([df_p_safe, df_novos], ignore_index=True)
                        
                        conn.update(worksheet="Palpites", data=df_final)
                        st.cache_data.clear()
                        st.balloons()
                        st.success("✅ Todos os seus palpites foram salvos com sucesso!")
                    except:
                        st.error("Erro técnico de conexão. Tente salvar novamente.")
        
        # --- EXIBIÇÃO DOS PALPITES ATUAIS SALVOS + BLOCO WHATSAPP ---
        st.divider()
        df_meus_palpites = df_palpites[(df_palpites["nome"] == nome_input) & (df_palpites["jogo"].str.startswith("Q"))]
        
        if not df_meus_palpites.empty:
            st.subheader("📋 Seus Resultados Escolhidos")
            
            texto_meus_palpites = f"📝 *MEUS PALPITES - QUARTAS* 📝\n"
            texto_meus_palpites += f"👤 *Participante:* {nome_input}\n\n"
            
            for _, p_row in df_meus_palpites.iterrows():
                j_info = dict_jogos.get(p_row["jogo"])
                if j_info:
                    f1 = bandeiras_emoji.get(j_info["time1"], "⚽")
                    f2 = bandeiras_emoji.get(j_info["time2"], "⚽")
                    val_p1 = int(p_row["p1"])
                    val_p2 = int(p_row["p2"])
                    val_passa = p_row["passa"]
                    
                    # Mostra de forma organizada na interface
                    st.markdown(f"**{f1} {j_info['time1']} {val_p1} x {val_p2} {j_info['time2']} {f2}**" + (f" *(Passa: {val_passa})*" if val_passa else ""))
                    
                    # Constrói o texto do WhatsApp
                    texto_meus_palpites += f"{f1} {j_info['time1']} {val_p1} x {val_p2} {j_info['time2']} {f2}"
                    if val_p1 == val_p2 and val_passa:
                        texto_meus_palpites += f" (Pênaltis: {val_passa})"
                    texto_meus_palpites += "\n"
            
            texto_meus_palpites += "\n👉 *Faça seus palpites também pelo link!*"
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📲 Copiar Texto para o WhatsApp")
            st.caption("Clique no botão de copiar no canto direito do bloco abaixo:")
            st.code(texto_meus_palpites, language="text")
    else:
        st.info("Identifique-se inserindo seu nome no topo para liberar a tela de palpites.")

# ==================== PAGINA 3: ADMIN ====================
elif st.session_state.pagina == "⚙️ Admin":
    st.header("⚙️ Painel do Administrador")
    
    df_q_jogos = df_jogos[df_jogos["id"].str.startswith("Q", na=False)]
    
    for _, j in df_q_jogos.iterrows():
        with st.form(key=f"admin_{j['id']}"):
            st.write(f"**Placar Oficial: {j['time1']} x {j['time2']}**")
            adm_g1 = st.number_input(f"Gols {j['time1']}", min_value=0, step=1, value=int(j["gols1"]))
            adm_g2 = st.number_input(f"Gols {j['time2']}", min_value=0, step=1, value=int(j["gols2"]))
            adm_passa = st.selectbox("Quem passou?", ["Sem pênaltis", j['time1'], j['time2']])
            finalizar = st.checkbox("Encerrar partida e computar pontos", value=(str(j["encerrado"]) == "Sim"))
            
            if st.form_submit_button("Confirmar Resultado"):
                try:
                    df_j_safe = conn.read(worksheet="Jogos", ttl=0)
                    passa_adm = adm_passa if adm_passa != "Sem pênaltis" else ""
                    
                    df_j_safe.loc[df_j_safe["id"] == j["id"], "gols1"] = adm_g1
                    df_j_safe.loc[df_j_safe["id"] == j["id"], "gols2"] = adm_g2
                    df_j_safe.loc[df_j_safe["id"] == j["id"], "passa"] = passa_adm
                    df_j_safe.loc[df_j_safe["id"] == j["id"], "encerrado"] = "Sim" if finalizar else "Não"
                    
                    conn.update(worksheet="Jogos", data=df_j_safe)
                    st.cache_data.clear()
                    st.success("Resultado gravado com sucesso!")
                except:
                    st.error("Erro ao atualizar dados.")
