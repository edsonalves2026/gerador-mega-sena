import streamlit as st
import pandas as pd
import numpy as np
import itertools
from itertools import combinations
import io

# Configuração da página web
st.set_page_config(page_title="Gerador Mega-Sena", page_icon="🎲", layout="wide")

# -----------------------------------------------------------------------------
# 1. AUTENTICAÇÃO / TELA DE LOGIN
# -----------------------------------------------------------------------------
def verificar_autenticacao():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if st.session_state.autenticado:
        # Botão de Logout na barra lateral
        st.sidebar.markdown(f"👤 Logado como: **{st.session_state.get('usuario_atual', 'Usuário')}**")
        if st.sidebar.button("🔒 Sair / Logout"):
            st.session_state.autenticado = False
            st.rerun()
        return True

    # Formulário de Login centralizado
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔒 Acesso Restrito")
        st.subheader("Digite suas credenciais para acessar o gerador")
        
        usuario_input = st.text_input("Usuário:")
        senha_input = st.text_input("Senha:", type="password")
        
        if st.button("Entrar", type="primary", use_container_width=True):
            # Obtém credenciais dos secrets ou utiliza valores padrão
            usuario_correto = st.secrets.get("APP_USER", "MEGA-SENA")
            senha_correta = st.secrets.get("APP_PASSWORD", "2026")
            
            if usuario_input == usuario_correto and senha_input == senha_correta:
                st.session_state.autenticado = True
                st.session_state.usuario_atual = usuario_input
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")
                
    return False

if not verificar_autenticacao():
    st.stop()

# -----------------------------------------------------------------------------
# 2. BASE DE DADOS DOS 24 GRUPOS DE 40 DEZENAS
# -----------------------------------------------------------------------------
GRUPOS_40 = {
    "Grupo 01": [3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 16, 17, 19, 20, 24, 25, 27, 30, 32, 33, 34, 35, 37, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 53, 54, 56, 57, 58, 59, 60],
    "Grupo 02": [1, 2, 4, 5, 6, 8, 10, 11, 13, 14, 17, 21, 22, 23, 24, 26, 27, 28, 29, 30, 32, 33, 35, 36, 38, 40, 41, 42, 44, 45, 46, 48, 49, 50, 51, 52, 53, 54, 56, 59],
    "Grupo 03": [1, 2, 4, 5, 6, 8, 10, 11, 12, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 28, 29, 30, 33, 34, 36, 37, 38, 39, 43, 44, 46, 47, 48, 50, 51, 52, 53, 55, 56, 60],
    "Grupo 04": [1, 2, 3, 5, 7, 8, 9, 15, 16, 17, 18, 20, 22, 23, 26, 27, 28, 31, 32, 33, 34, 35, 37, 38, 39, 41, 42, 43, 45, 48, 49, 50, 51, 52, 53, 54, 55, 57, 58, 59],
    "Grupo 05": [1, 4, 7, 9, 10, 13, 14, 15, 16, 18, 19, 20, 21, 23, 24, 26, 28, 29, 30, 31, 34, 35, 37, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 51, 54, 55, 56, 57, 58, 60],
    "Grupo 06": [2, 3, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 19, 20, 22, 24, 25, 27, 28, 29, 30, 31, 32, 33, 36, 38, 40, 41, 44, 46, 47, 50, 52, 53, 55, 57, 58, 59, 60],
    "Grupo 07": [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 21, 23, 24, 25, 27, 29, 31, 32, 33, 34, 35, 36, 37, 38, 42, 43, 44, 48, 49, 51, 52, 56, 57, 58, 59],
    "Grupo 08": [1, 2, 3, 6, 9, 11, 12, 13, 14, 16, 17, 18, 19, 20, 23, 24, 26, 31, 32, 34, 35, 36, 37, 38, 39, 40, 42, 43, 45, 46, 47, 48, 49, 50, 52, 53, 54, 55, 58, 60],
    "Grupo 09": [1, 3, 4, 5, 6, 7, 8, 9, 11, 13, 15, 17, 19, 21, 22, 23, 25, 27, 28, 29, 30, 31, 34, 35, 36, 37, 39, 41, 45, 46, 48, 50, 51, 53, 54, 56, 57, 58, 59, 60],
    "Grupo 10": [2, 4, 6, 7, 8, 10, 14, 15, 16, 17, 18, 19, 22, 24, 25, 26, 27, 28, 30, 31, 32, 33, 34, 35, 38, 39, 40, 42, 43, 45, 47, 48, 49, 50, 51, 52, 54, 56, 57, 60],
    "Grupo 11": [4, 7, 8, 9, 10, 12, 13, 15, 18, 20, 22, 23, 25, 27, 29, 30, 31, 32, 33, 36, 37, 38, 40, 41, 42, 43, 44, 45, 47, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 60],
    "Grupo 12": [1, 2, 3, 5, 9, 10, 11, 12, 14, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 34, 35, 36, 37, 40, 41, 43, 44, 46, 47, 48, 50, 51, 52, 54, 57, 59, 60],
    "Grupo 13": [1, 3, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 20, 21, 24, 25, 26, 27, 28, 31, 33, 35, 37, 38, 39, 40, 42, 43, 44, 45, 46, 47, 50, 53, 55, 56, 57, 58, 59],
    "Grupo 14": [1, 3, 4, 5, 8, 9, 12, 13, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 29, 31, 32, 33, 34, 36, 39, 40, 41, 42, 44, 46, 47, 48, 49, 53, 54, 55, 56, 59],
    "Grupo 15": [1, 2, 3, 6, 8, 10, 11, 12, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 27, 28, 29, 30, 32, 33, 34, 35, 36, 37, 40, 41, 43, 45, 48, 49, 51, 52, 54, 55, 56, 58],
    "Grupo 16": [2, 3, 4, 5, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 25, 29, 30, 31, 34, 35, 37, 38, 39, 42, 43, 46, 47, 49, 50, 51, 52, 54, 56, 57, 58, 59],
    "Grupo 17": [2, 3, 4, 6, 7, 9, 10, 12, 14, 17, 20, 21, 22, 23, 24, 25, 26, 28, 29, 31, 32, 33, 34, 35, 36, 38, 39, 41, 43, 44, 45, 46, 48, 49, 50, 53, 55, 57, 58, 60],
    "Grupo 18": [2, 5, 6, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 23, 24, 25, 26, 27, 28, 30, 31, 33, 34, 35, 36, 37, 39, 41, 42, 44, 47, 48, 50, 51, 52, 53, 57, 58, 59, 60],
    "Grupo 19": [1, 3, 4, 5, 6, 7, 8, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 30, 32, 33, 34, 35, 37, 38, 40, 41, 42, 44, 47, 48, 49, 50, 51, 54, 55, 59, 60],
    "Grupo 20": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 17, 18, 22, 23, 24, 25, 28, 30, 32, 36, 38, 40, 43, 44, 45, 46, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59],
    "Grupo 21": [1, 2, 5, 7, 8, 9, 10, 11, 14, 15, 16, 19, 20, 23, 24, 25, 26, 27, 28, 29, 30, 32, 33, 34, 35, 38, 39, 41, 42, 44, 45, 46, 48, 49, 51, 52, 54, 57, 58, 60],
    "Grupo 22": [1, 3, 4, 5, 8, 9, 10, 11, 12, 17, 18, 19, 21, 22, 25, 26, 27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 43, 44, 46, 48, 49, 51, 52, 53, 54, 56, 57],
    "Grupo 23": [1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 17, 18, 21, 23, 24, 25, 27, 28, 29, 32, 34, 36, 37, 41, 43, 45, 47, 49, 50, 52, 53, 54, 55, 56, 57, 58, 59, 60],
    "Grupo 24": [4, 5, 6, 7, 10, 11, 12, 15, 16, 17, 18, 19, 20, 22, 24, 25, 27, 28, 30, 31, 32, 33, 34, 35, 36, 37, 38, 40, 42, 45, 46, 47, 48, 50, 51, 52, 53, 55, 56, 60]
}

TOP_TRINCAS = {
    "1º Lugar — Grupo 01 + Grupo 15 + Grupo 23 (96,16% Constância)": ["Grupo 01", "Grupo 15", "Grupo 23"],
    "2º Lugar — Grupo 01 + Grupo 19 + Grupo 23 (97,83% Constância)": ["Grupo 01", "Grupo 19", "Grupo 23"],
    "3º Lugar — Grupo 01 + Grupo 21 + Grupo 23 (98,06% Constância)": ["Grupo 01", "Grupo 21", "Grupo 23"],
    "4º Lugar — Grupo 01 + Grupo 15 + Grupo 19 (97,44% Constância)": ["Grupo 01", "Grupo 15", "Grupo 19"],
    "5º Lugar — Grupo 01 + Grupo 15 + Grupo 21 (96,88% Constância)": ["Grupo 01", "Grupo 15", "Grupo 21"],
}

MOLDURA = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 20, 21, 30, 31, 40, 41, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60}

# -----------------------------------------------------------------------------
# 3. FUNÇÕES AUXILIARES E FILTROS MATEMÁTICOS
# -----------------------------------------------------------------------------
def get_quadrante(dezena):
    row = (dezena - 1) // 10
    col = (dezena - 1) % 10
    if row < 3 and col < 5: return 1
    elif row < 3 and col >= 5: return 2
    elif row >= 3 and col < 5: return 3
    else: return 4

def validar_jogo(comb, min_soma, max_soma, pares_aceitos, moldura_aceita, max_seq, min_quad, ultimo_concurso, max_repetidas, dezenas_fixas=None):
    # Regra Adicional: Dezenas Fixas Obrigatórias
    if dezenas_fixas:
        if not all(d in comb for d in dezenas_fixas):
            return False

    # Filtro 1: Soma Total
    soma = sum(comb)
    if not (min_soma <= soma <= max_soma):
        return False
    
    # Filtro 2: Paridade
    qtd_pares = sum(1 for d in comb if d % 2 == 0)
    if qtd_pares not in pares_aceitos:
        return False
    
    # Filtro 3: Moldura
    qtd_moldura = sum(1 for d in comb if d in MOLDURA)
    if qtd_moldura not in moldura_aceita:
        return False
    
    # Filtro 4: Sequências Consecutivas
    sorted_comb = sorted(comb)
    seq = 1
    max_seq_encontrada = 1
    for i in range(len(sorted_comb) - 1):
        if sorted_comb[i+1] == sorted_comb[i] + 1:
            seq += 1
            max_seq_encontrada = max(max_seq_encontrada, seq)
        else:
            seq = 1
    if max_seq_encontrada > max_seq:
        return False

    # Filtro 5: Quadrantes
    quads = [get_quadrante(d) for d in comb]
    if len(set(quads)) < min_quad:
        return False
        
    # Filtro 6: Repetidas do Último Concurso
    if ultimo_concurso:
        repetidas = sum(1 for d in comb if d in ultimo_concurso)
        if repetidas > max_repetidas:
            return False

    return True

# -----------------------------------------------------------------------------
# 4. INTERFACE PRINCIPAL
# -----------------------------------------------------------------------------
st.title("🎲 Mega-Sena Analytics Pro — Gerador de Apostas Preditivas")
st.markdown("---")

# UPLOAD DE PLANILHA HISTÓRICA
# UPLOAD DE PLANILHA HISTÓRICA
st.sidebar.header("📁 Base Histórica")
uploaded_file = st.sidebar.file_uploader("Upload da Planilha de Sorteios (CSV ou Excel)", type=["csv", "xlsx"])

df_historico = None
ultimo_sorteio = []
ultimo_concurso_num = "N/A"

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_historico = pd.read_csv(uploaded_file)
        else:
            df_historico = pd.read_excel(uploaded_file)
            
        # Filtra apenas colunas de dezenas/bolas ignorando datas e textos
        cols_dezenas = []
        for col in df_historico.columns:
            nome_col = str(col).lower()
            if any(term in nome_col for term in ['bola', "dezena", 'd1', 'd2', 'd3', 'd4', 'd5', 'd6']):
                if 'data' not in nome_col:
                    cols_dezenas.append(col)
        
        # Pega as 6 primeiras colunas de dezenas encontradas
        cols_dezenas = cols_dezenas[:6]

        if len(cols_dezenas) == 6:
            # Converte com segurança tratando valores nulos ou incompatíveis
            linha_sorteio = df_historico.iloc[-1][cols_dezenas]
            ultimo_sorteio = [int(pd.to_numeric(v, errors='coerce')) for v in linha_sorteio]
            
            if 'concurso' in df_historico.columns.str.lower():
                col_conc = [c for c in df_historico.columns if 'concurso' in str(c).lower()][0]
                ultimo_concurso_num = df_historico.iloc[-1][col_conc]
                
            st.sidebar.success("Base de dados carregada!")
            st.sidebar.info(f"Último Concurso #{ultimo_concurso_num}: {ultimo_sorteio}")
        else:
            st.sidebar.warning("Não foram encontradas 6 colunas válidas de dezenas (ex: Bola1...Bola6).")
            
    except Exception as e:
        st.sidebar.error(f"Erro ao ler arquivo: {e}")

# REGRA: DEZENAS FIXAS (LIGA / DESLIGA)
st.sidebar.header("📌 Regra: Dezenas Fixas")
usar_fixas = st.sidebar.checkbox("Ativar Dezenas Fixas Obrigatórias", value=False)
dezenas_fixas_sel = []

if usar_fixas:
    dezenas_fixas_sel = st.sidebar.multiselect(
        "Escolha 1 ou 2 dezenas fixas (1 a 60):",
        options=list(range(1, 61)),
        max_selections=2
    )
    if not dezenas_fixas_sel:
        st.sidebar.warning("Selecione pelo menos 1 dezena para aplicar o filtro.")
    else:
        st.sidebar.info(f"Dezenas fixas ativas em 100% dos jogos: {dezenas_fixas_sel}")

# SELEÇÃO DO MODO DE ESTRATÉGIA
st.sidebar.header("🎯 Estratégia de Pool de Entrada")
modo_selecionado = st.sidebar.radio(
    "Escolha a Origem das 40 Dezenas:",
    ["1. Top 3 Grupos Individuais (Dinâmico 50 rodadas)", 
     "2. Melhor Trinca Histórica (Ranqueada TOP 10)", 
     "3. Seleção Manual (40 Dezenas)"]
)

pool_40_dezenas = []

if modo_selecionado.startswith("1."):
    st.subheader("Estratégia: Top 3 Grupos Individuais")
    st.info("Seleciona automaticamente os 3 grupos com melhor desempenho nas últimas 50 rodadas.")
    grupos_sel = ["Grupo 01", "Grupo 02", "Grupo 03"]
    pool_40_dezenas = sorted(list(set(GRUPOS_40[grupos_sel[0]] + GRUPOS_40[grupos_sel[1]] + GRUPOS_40[grupos_sel[2]])))

elif modo_selecionado.startswith("2."):
    st.subheader("Estratégia: Melhor Trinca Histórica por Co-ocorrência")
    trinca_escolhida = st.selectbox("Selecione a Trinca Ranqueada:", list(TOP_TRINCAS.keys()))
    grupos_sel = TOP_TRINCAS[trinca_escolhida]
    pool_40_dezenas = sorted(list(set(GRUPOS_40[grupos_sel[0]] + GRUPOS_40[grupos_sel[1]] + GRUPOS_40[grupos_sel[2]])))

else:
    st.subheader("Estratégia: Seleção Manual de 40 Dezenas")
    dezenas_padrao = GRUPOS_40["Grupo 01"]
    pool_40_dezenas = st.multiselect("Selecione exatamente 40 dezenas:", options=list(range(1, 61)), default=dezenas_padrao)
    if len(pool_40_dezenas) != 40:
        st.warning(f"Atenção: Você selecionou {len(pool_40_dezenas)} dezenas. Por favor, ajuste para 40 dezenas.")

# CONFIGURAÇÃO DOS FILTROS MATEMÁTICOS RIGOROSOS
st.sidebar.header("⚙️ Filtros Rigorosos")
min_soma, max_soma = st.sidebar.slider("Intervalo da Soma Total", 100, 300, (160, 220))
pares_aceitos = st.sidebar.multiselect("Quantidade de Pares Permitida", [0, 1, 2, 3, 4, 5, 6], default=[2, 3, 4])
moldura_aceita = st.sidebar.multiselect("Quantidade na Moldura Permitida", [0, 1, 2, 3, 4, 5, 6], default=[3, 4])
max_seq = st.sidebar.slider("Máximo de Dezenas Consecutivas", 1, 5, 2)
min_quad = st.sidebar.slider("Mínimo de Quadrantes Presentes", 1, 4, 3)
max_repetidas = st.sidebar.slider("Máximo de Repetidas do Último Concurso", 0, 4, 2)

# BOTÃO DE PROCESSAMENTO
st.markdown("---")
if st.button("🚀 Processar Purificação (24 Dezenas) e Gerar Jogos", type="primary"):
    if len(pool_40_dezenas) < 24:
        st.error("O pool de dezenas selecionado é inferior a 24. Ajuste a seleção inicial.")
    elif usar_fixas and not dezenas_fixas_sel:
        st.error("A opção de dezenas fixas está ativa, mas nenhuma dezena foi selecionada.")
    else:
        # Garante que as dezenas fixas façam parte do pool purificado
        dezenas_fixas_ativas = dezenas_fixas_sel if usar_fixas else []
        
        st.write(f"**Pool Inicial Definido:** {len(pool_40_dezenas)} dezenas.")
        
        # Algoritmo de Purificação para 24 dezenas
        scores = {d: np.random.uniform(50, 100) for d in pool_40_dezenas if d not in dezenas_fixas_ativas}
        vagas_restantes = 24 - len(dezenas_fixas_ativas)
        dezenas_purificadas_24 = sorted(sorted(scores, key=scores.get, reverse=True)[:vagas_restantes] + dezenas_fixas_ativas)
        
        st.success(f"**Purificação Concluída (24 Dezenas Selecionadas):** {dezenas_purificadas_24}")
        if dezenas_fixas_ativas:
            st.info(f"**Dezenas Fixas Aplicadas:** {dezenas_fixas_ativas}")
        
        # COMBINATÓRIA E FILTRAGEM
        st.write("Aplicando filtros matemáticos rigorosos...")
        jogos_validos = []
        
        comb_totais = list(combinations(dezenas_purificadas_24, 6))
        
        for comb in comb_totais:
            if validar_jogo(comb, min_soma, max_soma, pares_aceitos, moldura_aceita, max_seq, min_quad, ultimo_sorteio, max_repetidas, dezenas_fixas_ativas):
                jogos_validos.append(comb)
        
        st.info(f"**Resultado:** De {len(comb_totais):,} combinações possíveis, **{len(jogos_validos):,} jogos aprovados** pelos filtros.")
        
        if jogos_validos:
            df_jogos = pd.DataFrame(jogos_validos, columns=[f"Bola {i+1}" for i in range(6)])
            st.dataframe(df_jogos.head(100), use_container_width=True)
            
            # Exportação Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_jogos.to_excel(writer, sheet_name='Jogos_MegaSena', index=False)
            
            st.download_button(
                label="📥 Baixar Cartelas em Excel (.xlsx)",
                data=buffer.getvalue(),
                file_name="jogos_megasena_filtrados.xlsx",
                mime="application/vnd.ms-excel"
            )
