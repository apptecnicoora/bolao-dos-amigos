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
        padding: 15px;
        margin-bottom: 20px;
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

# --- MENU DE NAVEGAÇÃO SUPERSTÁVEL ---
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
    
    # Imagem do topo em Base64 segura
    if os.path.exists("ronaldinho.gif"):
        with open("ronaldinho.gif", "rb") as f:
            st.markdown(f"<div style='text-align:center'><img src='data:image/gif;base64,{base64.b64encode(f.read()).decode()}' style='width:100%; border-radius:12px; border:2px solid #009B3A;'></div><br>", unsafe_allow_html=True)
    else:
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e0/Ronaldinho_11022007.jpg", use_container_width=True)

    # Lógica do Sorteio Instantâneo (Sem APIs externas para não quebrar)
    st.markdown("<div style='background-color:#161a22; padding:15px; border-radius:12px; border:1px solid #FFDF00; text-align:center;'>", unsafe_allow_html=True)
    st.subheader("🎲 Qual craque você é hoje?")
    if st.button("SORTEAR MEU JOGADOR"):
        craques = ["Ronaldinho Gaúcho 🧙‍♂️", "Cássio Ramos 🧱", "Neymar Jr ⚡", "Ronaldo Fenômeno 🔥", "Sócrates 🧠", "Marcelinho Carioca 🎯", "Craque Neto 🦅", "Lionel Messi 👑", "Cristiano Ronaldo 🤖"]
        st.success(f"Você está com a energia de: **{random.choice(craques)}**!")
    st.markdown("</div><br>", unsafe_allow_html=True)

    # Processamento do Ranking
    pontos_totais = {}
    cravadas_totais = {}
    
    df_q_jogos = df_jogos[df_jogos["id"].str.startswith("Q", na=False)]
    dict_status_jogos = {row["id"]: row for _, row in df_q_jogos.iterrows()}
    
    for _, p in df_palpites.iterrows():
        if str(p["jogo"]).startswith("Q"):
            nome = p["nome"]
            pontos_totais[nome] = pontos_totais.get(nome, 0)
            cravadas_totais[nome] = cravadas_totais.get(nome, 0)
            
            jogo = dict_status_jogos.get(p["jogo"])
            if jogo is not None and str(jogo["encerrado"]) == "Sim":
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
        
        # Garante o cadastro do usuário de forma leve
        if nome_input betting_not_in_db := (nome_input not in df_usuarios["nome"].values):
            novo_u = pd.DataFrame([{"nome": nome_input, "avatar": "⚽"}])
            df_usuarios = pd.concat([df_usuarios, novo_u], ignore_index=True)
            conn.update(worksheet="Usuarios", data=df_usuarios)
            
        st.success(f"Conectado como: {nome_input}")
        
        # --- FORMULÁRIO ÚNICO EM BLOCK ---
        with st.form(key="formulario_global_quartas"):
            st.markdown("<p style='color:#FFDF00;'>Preencha todos os jogos abaixo e clique em Salvar no final da página:</p>", unsafe_allow_html=True)
            
            df_q_jogos = df_jogos[df_jogos["id"].str.startswith("Q", na=False)]
            dados_do_formulario = []
            
            for _, j in df_q_jogos.iterrows():
                id_j = j["id"]
                st.markdown(f"""
                <div class='card-jogo'>
                    <div style='text-align:center; color:#FFDF00; font-weight:bold;'>📅 {j['horário']}</div>
                    <h4 style='text-align:center; margin:5px 0;'>{j['time1']} x {j['time2']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Campos de entrada lado a lado
                c1, c2 = st.columns(2)
                with c1: g1 = st.number_input(f"Gols {j['time1']}", min_value=0, step=1, key=f"g1_{id_j}")
                with c2: g2 = st.number_input(f"Gols {j['time2']}", min_value=0, step=1, key=f"g2_{id_j}")
                
                passa = st.selectbox(f"Quem se classifica em {j['time1']} x {j['time2']}?", ["Não empatou", j['time1'], j['time2']], key=f"passa_{id_j}")
                st.markdown("<hr style='border:1px dashed #30363d'>", unsafe_allow_html=True)
                
                dados_do_formulario.append({"id": id_j, "g1": g1, "g2": g2, "passa": passa, "horario": j["horário"], "t1": j["time1"], "t2": j["time2"]})
            
            botao_gravar = st.form_submit_button("💾 SALVAR TODOS OS MEUS PALPITES")
            
            if botao_gravar:
                erros = []
                novos_palpites_lista = []
                
                for item in dados_do_formulario:
                    if jogo_ja_comecou(item["horario"]):
                        continue # Pula jogos que já iniciaram para proteger o sistema
                        
                    if item["g1"] == item["g2"] and item["passa"] == "Não empatou":
                        erros.append(f"Faltou escolher quem passa nos pênaltis em {item['t1']} x {item['t2']}!")
                    elif item["g1"] != item["g2"] and item["passa"] != "Não empatou":
                        erros.append(f"O jogo {item['t1']} x {item['t2']} não terminou empatado, ajuste o campo de pênaltis.")
                    else:
                        passa_final = item["passa"] if item["passa"] != "Não empatou" else ""
                        novos_palpites_lista.append({"nome": nome_input, "jogo": item["id"], "p1": int(item["g1"]), "p2": int(item["g2"]), "passa": passa_final})
                
                if erros:
                    for err in erros: st.error(err)
                else:
                    # Gravação em lote unificada anti-wipe
                    try:
                        df_p_safe = conn.read(worksheet="Palpites", ttl=0)
                        if df_p_safe is None: df_p_safe = pd.DataFrame(columns=["nome", "jogo", "p1", "p2", "passa"])
                        
                        # Remove os registros antigos desse usuário para as quartas
                        df_p_safe = df_p_safe[~((df_p_safe["nome"] == nome_input) & (df_p_safe["jogo"].str.startswith("Q")))]
                        
                        # Adiciona o bloco novo de uma vez só
                        df_novos = pd.DataFrame(novos_palpites_lista)
                        df_final = pd.concat([df_p_safe, df_novos], ignore_index=True)
                        
                        conn.update(worksheet="Palpites", data=df_final)
                        st.cache_data.clear()
                        st.balloons()
                        st.success("✅ Todos os seus palpites foram salvos com sucesso! Campos limpos para o próximo.")
                    except:
                        st.error("Erro técnico de gravação. Tente novamente.")
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
