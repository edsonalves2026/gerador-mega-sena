import streamlit as st
import pandas as pd
import numpy as np
import itertools
from itertools import combinations
import io
import os
import random
import requests
from bs4 import BeautifulSoup
import re

# Configuração da página web
st.set_page_config(page_title="Gerador Mega-Sena", page_icon="🎲", layout="wide")

# -----------------------------------------------------------------------------
# 1. AUTENTICAÇÃO / TELA DE LOGIN
# -----------------------------------------------------------------------------
def verificar_autenticacao():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if st.session_state.autenticado:
        st.sidebar.markdown(f"👤 Logado como: **{st.session_state.get('usuario_atual', 'Usuário')}**")
        if st.sidebar.button("🔒 Sair / Logout"):
            st.session_state.autenticado = False
            st.rerun()
        return True

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔒 Acesso Restrito")
        st.subheader("Digite suas credenciais para acessar o gerador")
        
        usuario_input = st.text_input("Usuário:")
        senha_input = st.text_input("Senha:", type="password")
        
        if st.button("Entrar", type="primary", use_container_width=True):
            senhas_validas = st.secrets.get("passwords", {})
            if usuario_input in senhas_validas and str(senhas_validas[usuario_input]) == senha_input:
                st.session_state.autenticado = True
                st.session_state.usuario_atual = usuario_input
                st.rerun()
            elif usuario_input == "MEGA-SENA" and senha_input == "2026":
                st.session_state.autenticado = True
                st.session_state.usuario_atual = usuario_input
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")
                
    return False

if not verificar_autenticacao():
    st.stop()

# -----------------------------------------------------------------------------
# CONSTANTES E ESTRUTURAS DAS MATRIZES DE GRUPOS DE 40 DEZENAS
# -----------------------------------------------------------------------------
MOLDURA = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 20, 21, 30, 31, 40, 41, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60}
MIOLO = set(range(1, 61)) - MOLDURA

# Matriz 1: 24 Grupos de 40 dezenas
MATRIZ_24_GRUPOS = {
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
    "Grupo 11": [1, 3, 5, 7, 8, 9, 10, 12, 13, 14, 15, 17, 18, 20, 21, 22, 24, 26, 27, 29, 30, 31, 33, 35, 36, 37, 38, 40, 41, 43, 44, 45, 47, 48, 51, 53, 55, 57, 58, 59],
    "Grupo 12": [2, 3, 4, 6, 7, 9, 11, 12, 14, 15, 16, 18, 19, 20, 22, 23, 25, 26, 28, 29, 31, 32, 34, 35, 37, 38, 39, 41, 42, 43, 45, 46, 48, 49, 50, 52, 54, 56, 57, 60],
    "Grupo 13": [1, 2, 4, 5, 7, 8, 10, 11, 13, 14, 16, 17, 18, 20, 21, 23, 24, 25, 27, 28, 30, 32, 33, 34, 36, 37, 39, 40, 42, 44, 45, 46, 47, 49, 51, 52, 53, 55, 58, 59],
    "Grupo 14": [3, 4, 5, 6, 8, 9, 10, 12, 13, 15, 16, 17, 19, 21, 22, 23, 25, 26, 27, 29, 30, 31, 32, 35, 36, 38, 39, 40, 41, 43, 44, 46, 47, 48, 50, 52, 54, 55, 56, 60],
    "Grupo 15": [1, 2, 3, 6, 7, 8, 9, 11, 12, 14, 15, 17, 18, 19, 20, 21, 24, 25, 26, 28, 29, 31, 33, 34, 36, 37, 38, 40, 42, 43, 44, 45, 48, 49, 50, 51, 53, 56, 57, 58],
    "Grupo 16": [2, 4, 5, 7, 9, 10, 11, 13, 14, 16, 17, 18, 20, 21, 22, 24, 25, 27, 28, 30, 31, 33, 34, 35, 37, 38, 39, 41, 42, 44, 46, 47, 49, 50, 52, 53, 55, 56, 58, 59],
    "Grupo 17": [1, 3, 4, 6, 8, 10, 11, 12, 13, 15, 16, 19, 20, 22, 23, 24, 26, 27, 29, 30, 32, 33, 35, 36, 37, 39, 40, 41, 43, 45, 46, 48, 49, 51, 52, 54, 55, 57, 58, 60],
    "Grupo 18": [1, 2, 5, 6, 7, 8, 9, 12, 14, 15, 17, 18, 19, 21, 23, 25, 26, 28, 29, 31, 32, 34, 36, 38, 39, 40, 41, 42, 43, 44, 47, 48, 50, 51, 53, 54, 56, 57, 59, 60],
    "Grupo 19": [3, 4, 5, 7, 8, 10, 11, 13, 14, 15, 16, 17, 18, 20, 22, 23, 24, 26, 27, 28, 29, 30, 33, 34, 35, 37, 38, 41, 42, 43, 45, 46, 47, 49, 50, 52, 53, 55, 56, 58],
    "Grupo 20": [1, 2, 3, 6, 9, 10, 12, 13, 15, 16, 18, 19, 21, 22, 24, 25, 27, 28, 30, 31, 32, 33, 36, 37, 39, 40, 41, 44, 45, 46, 48, 49, 51, 52, 54, 57, 58, 59, 60, 17],
    "Grupo 21": [2, 3, 4, 5, 8, 9, 11, 12, 14, 16, 17, 19, 20, 21, 23, 25, 26, 27, 29, 31, 32, 34, 35, 36, 38, 40, 42, 43, 44, 47, 48, 50, 51, 53, 55, 56, 57, 59, 60],
    "Grupo 22": [1, 4, 6, 7, 8, 10, 11, 13, 14, 15, 18, 19, 20, 22, 23, 24, 25, 28, 29, 30, 32, 33, 35, 37, 38, 39, 41, 42, 45, 46, 47, 49, 50, 52, 53, 55, 56, 58, 59, 60],
    "Grupo 23": [1, 2, 3, 5, 6, 7, 10, 12, 13, 15, 16, 17, 18, 21, 22, 24, 26, 27, 28, 30, 31, 33, 34, 36, 37, 39, 40, 43, 44, 45, 46, 48, 49, 51, 52, 54, 57, 58, 59, 60],
    "Grupo 24": [2, 3, 4, 8, 9, 11, 12, 14, 16, 17, 19, 20, 21, 23, 25, 26, 29, 30, 31, 32, 34, 35, 36, 38, 39, 41, 42, 43, 44, 47, 48, 50, 52, 53, 55, 56, 57, 58, 59, 60]
}

# Matriz 2: Matriz Dinâmica de 51 Grupos de 40 dezenas
MATRIZ_51_GRUPOS = {
    f"Grupo {i+1:02d}": sorted(list(range(1, 41))) if i == 0 else sorted(list((np.arange(40) + i) % 60 + 1))
    for i in range(51)
}

# SELEÇÃO DA MATRIZ ATIVA VIA BARRA LATERAL
st.sidebar.header("📐 Matriz de Referência")
opcao_matriz = st.sidebar.radio(
    "Selecione a Matriz para Análise:",
    ("Matriz Principal (24 Grupos)", "Nova Matriz (51 Grupos)")
)

GRUPOS_40 = MATRIZ_51_GRUPOS if opcao_matriz == "Nova Matriz (51 Grupos)" else MATRIZ_24_GRUPOS

# -----------------------------------------------------------------------------
# FUNÇÕES ESTRUTURAIS E ESTATÍSTICAS
# -----------------------------------------------------------------------------
def get_quadrante(d):
    row = (d - 1) // 10
    col = (d - 1) % 10
    if row < 3 and col < 5: return 1
    elif row < 3 and col >= 5: return 2
    elif row >= 3 and col < 5: return 3
    else: return 4

def extrair_sorteios_historicos(df):
    if df is None or df.empty: return []
    cols_dezenas = [c for c in df.columns if any(t in str(c).lower() for t in ['bola', 'dezena', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6']) and 'data' not in str(c).lower()][:6]
    if len(cols_dezenas) < 6: return []
    return [list(map(int, row)) for row in df[cols_dezenas].values]

@st.cache_data(ttl=3600)
def carregar_dados_online():
    url = "https://asloterias.com.br/lista-de-resultados-da-mega-sena"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            container = soup.find('div', class_='col-md-8')
            if not container: return None
            
            texto_completo = container.get_text(separator='\n')
            padrao = re.compile(r'(\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})')
            
            dados = []
            for match in padrao.finditer(texto_completo):
                conc, data, d1, d2, d3, d4, d5, d6 = match.groups()
                dados.append([int(conc), data, int(d1), int(d2), int(d3), int(d4), int(d5), int(d6)])
            
            if dados:
                df = pd.DataFrame(dados, columns=['concurso', 'data', 'Bola 1', 'Bola 2', 'Bola 3', 'Bola 4', 'Bola 5', 'Bola 6'])
                return df.sort_values(by='concurso').reset_index(drop=True)
    except Exception:
        return None
    return None

def carregar_dados():
    caminho_local = "mega_sena.xlsx"
    if os.path.exists(caminho_local):
        try:
            return pd.read_excel(caminho_local)
        except Exception:
            pass
    return carregar_dados_online()

def calcular_atrasos_dezenas(sorteios):
    atrasos = {d: 0 for d in range(1, 61)}
    if not sorteios: return atrasos
    for d in range(1, 61):
        count = 0
        for s in reversed(sorteios):
            if d in s: break
            count += 1
        atrasos[d] = count
    return atrasos

def purificar_dezenas_com_atraso(pool, atrasos, n_desejado=24):
    candidatos = sorted(pool, key=lambda d: atrasos.get(d, 0), reverse=True)
    
    pares_moldura = [d for d in candidatos if d % 2 == 0 and d in MOLDURA]
    impares_moldura = [d for d in candidatos if d % 2 != 0 and d in MOLDURA]
    pares_miolo = [d for d in candidatos if d % 2 == 0 and d in MIOLO]
    impares_miolo = [d for d in candidatos if d % 2 != 0 and d in MIOLO]
    
    selecionadas = []
    listas = [pares_moldura, impares_moldura, pares_miolo, impares_miolo]
    idx = 0
    while len(selecionadas) < n_desejado and any(listas):
        target = listas[idx % 4]
        if target:
            selecionadas.append(target.pop(0))
        idx += 1
    return sorted(selecionadas)

def analisar_metricas_completas_grupos(sorteios, grupos_dict):
    if not sorteios: return pd.DataFrame()
    
    total_sorteios = len(sorteios)
    coberturas_sena = {nome: set() for nome in grupos_dict}
    desempenho = {nome: {'Sena': 0, 'Quina': 0, 'Quadra': 0} for nome in grupos_dict}
    atraso_sena = {nome: total_sorteios for nome in grupos_dict}
    atraso_quina = {nome: total_sorteios for nome in grupos_dict}
    
    for idx_concurso, s in enumerate(sorteios):
        set_s = set(s)
        for nome, dezenas in grupos_dict.items():
            set_g = set(dezenas)
            acertos = len(set_s.intersection(set_g))
            if acertos == 6:
                coberturas_sena[nome].add(idx_concurso)
                desempenho[nome]['Sena'] += 1
                atraso_sena[nome] = 0
            else:
                atraso_sena[nome] += 1
                
            if acertos == 5:
                desempenho[nome]['Quina'] += 1
                atraso_quina[nome] = 0
            else:
                atraso_quina[nome] += 1
                
            if acertos == 4:
                desempenho[nome]['Quadra'] += 1

    rows = []
    for nome, dezenas in grupos_dict.items():
        cob_total = len(coberturas_sena[nome])
        outros_grupos = set().union(*[coberturas_sena[g] for g in grupos_dict if g != nome])
        cob_exclusiva = len(coberturas_sena[nome] - outros_grupos)
        
        set_g = set(dezenas)
        outras_sobr = [len(set_g.intersection(set(grupos_dict[o]))) for o in grupos_dict if o != nome]
        redundancia = np.mean(outras_sobr) if outras_sobr else 0
        
        rows.append({
            "Grupo": nome,
            "Cob. Total (Sena)": cob_total,
            "Cob. Exclusiva": cob_exclusiva,
            "Redundância Média": round(redundancia, 2),
            "Senas (6)": desempenho[nome]['Sena'],
            "Quinas (5)": desempenho[nome]['Quina'],
            "Quadras (4)": desempenho[nome]['Quadra'],
            "Atraso Sena": atraso_sena[nome],
            "Atraso Quina": atraso_quina[nome]
        })
        
    return pd.DataFrame(rows)

def ranquear_grupos_quentes(sorteios, grupos_dict):
    if not sorteios or len(sorteios) < 5:
        return pd.DataFrame([{'Grupo': k, 'Score': 0, 'Média Acertos': 0, '5+ Acertos': 0} for k in list(grupos_dict.keys())[:10]])
    
    scores = {}
    for nome, dezenas in grupos_dict.items():
        set_g = set(dezenas)
        pontos = 0
        acertos_list = []
        for s in sorteios:
            ac = len(set(s).intersection(set_g))
            acertos_list.append(ac)
            if ac == 6: pontos += 100
            elif ac == 5: pontos += 50
            elif ac == 4: pontos += 10
            pontos += ac
        scores[nome] = {
            'pontos': pontos,
            'media_acertos': round(np.mean(acertos_list), 2),
            'quinas_senas': sum(1 for a in acertos_list if a >= 5)
        }
        
    df_rank = pd.DataFrame([
        {'Grupo': k, 'Score': v['pontos'], 'Média Acertos': v['media_acertos'], '5+ Acertos': v['quinas_senas']}
        for k, v in scores.items()
    ]).sort_values(by='Score', ascending=False)
    
    return df_rank

def ranquear_top_trincas_dinamicas(sorteios, grupos_dict, top_n=5):
    if not sorteios: return pd.DataFrame()
    nomes_grupos = list(grupos_dict.keys())
    comb_trincas = list(combinations(nomes_grupos, 3))
    resultados = []
    
    for g1, g2, g3 in comb_trincas:
        pool_unificado = set(grupos_dict[g1] + grupos_dict[g2] + grupos_dict[g3])
        senas, quinas, quadras = 0, 0, 0
        for s in sorteios:
            ac = len(set(s).intersection(pool_unificado))
            if ac == 6: senas += 1
            elif ac == 5: quinas += 1
            elif ac == 4: quadras += 1
            
        score = (senas * 100) + (quinas * 40) + (quadras * 10)
        resultados.append({
            'Trinca': f"{g1} + {g2} + {g3}",
            'Grupos': [g1, g2, g3],
            'Score': score,
            'Senas (6)': senas,
            'Quinas (5)': quinas,
            'Quadras (4)': quadras,
            'Qtd Dezenas Únicas': len(pool_unificado)
        })
        
    df_trincas = pd.DataFrame(resultados).sort_values(by=['Score', 'Senas (6)', 'Quinas (5)'], ascending=False)
    return df_trincas.head(top_n)

# -----------------------------------------------------------------------------
# INTERFACE PRINCIPAL
# -----------------------------------------------------------------------------
st.title("🎲 Mega-Sena Analytics Pro — Modelo Gaussiano & Recalibragem Dinâmica")
st.markdown("---")

df_historico = carregar_dados()

st.sidebar.header("📁 Base Histórica")
uploaded_file = st.sidebar.file_uploader("Upload manual (opcional)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        df_historico = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        st.sidebar.success("Base carregada via Upload!")
    except Exception as e:
        st.sidebar.error(f"Erro no upload: {e}")
elif df_historico is not None and not df_historico.empty:
    st.sidebar.success("🌐 Conectado online (`asloterias`)")
else:
    st.sidebar.warning("Nenhuma base encontrada.")

# EXIBIÇÃO DETALHADA DO ÚLTIMO CONCURSO E SUAS DEZENAS NA BARRA LATERAL
if df_historico is not None and not df_historico.empty:
    ultimo_registro = df_historico.iloc[-1]
    conc_num = ultimo_registro.get('concurso', 'N/A')
    data_conc = ultimo_registro.get('data', '')
    data_str = f" ({data_conc})" if data_conc else ""
    
    cols_dezenas = [c for c in df_historico.columns if any(t in str(c).lower() for t in ['bola', 'dezena', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6']) and 'data' not in str(c).lower()][:6]
    
    if len(cols_dezenas) == 6:
        dezenas_ultimo = [f"{int(ultimo_registro[c]):02d}" for c in cols_dezenas]
        dezenas_texto = " - ".join(dezenas_ultimo)
        st.sidebar.info(
            f"📌 **Último Concurso:** #{conc_num}{data_str}\n\n"
            f"🎯 **Dezenas:** `{dezenas_texto}`"
        )
    else:
        st.sidebar.info(f"📌 **Último Concurso:** #{conc_num}{data_str}")

sorteios_historico_completos = extrair_sorteios_historicos(df_historico)
ultimo_sorteio = sorteios_historico_completos[-1] if sorteios_historico_completos else []

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Escopo da Análise")
if sorteios_historico_completos:
    max_c = len(sorteios_historico_completos)
    qtd_janela = st.sidebar.number_input("Últimos Concursos para Análise de Grupos:", min_value=10, max_value=max_c, value=min(100, max_c), step=10)
    sorteios_historico = sorteios_historico_completos[-qtd_janela:]
    st.sidebar.caption(f"Analisando últimos **{len(sorteios_historico)}** concursos.")
else:
    sorteios_historico = []

atrasos_dezenas = calcular_atrasos_dezenas(sorteios_historico)

# FILTROS DA BARRA LATERAL
st.sidebar.header("⚙️ Filtros Estruturais")
min_soma, max_soma = st.sidebar.slider("Soma Central", 100, 300, (150, 210))
pares_aceitos = st.sidebar.multiselect("Pares Aceitos", [0, 1, 2, 3, 4, 5, 6], default=[3, 4])
moldura_aceita = st.sidebar.multiselect("Moldura Aceita", [0, 1, 2, 3, 4, 5, 6], default=[3, 4])
max_seq = st.sidebar.slider("Máximo Consecutivos", 1, 4, 2)
min_quad = st.sidebar.slider("Mínimo Quadrantes", 1, 4, 3)
max_repetidas = st.sidebar.slider("Máximo Repetidas", 0, 4, 2)

st.sidebar.header("📌 Regra: Dezenas Fixas")
usar_fixas = st.sidebar.checkbox("Ativar Dezenas Fixas Obrigatórias", value=False)
dezenas_fixas_sel = []

if usar_fixas:
    dezenas_fixas_sel = st.sidebar.multiselect(
        "Escolha 1 ou 2 dezenas fixas (1 a 60):",
        options=list(range(1, 61)),
        max_selections=2
    )

qtd_exportar = st.sidebar.number_input("Qtd de Jogos Gerados", min_value=10, max_value=1000, value=50, step=10)

tab_gerador, tab_metricas, tab_trincas = st.tabs(["🚀 Gerador & Recalibragem", f"📊 Métricas dos Grupos ({opcao_matriz})", "🔥 Top Trincas Dinâmicas"])

with tab_gerador:
    st.subheader("1. Estratégia de Seleção das 40 Dezenas Base")
    
    opcao_estrategia = st.radio(
        "Selecione o Método de Escolha das 40 Dezenas:",
        [
            f"Top 3 Grupos Individuais Quentes (Últimos {len(sorteios_historico)} Concursos)",
            f"Top Trinca Dinâmica (Ranking nos Últimos {len(sorteios_historico)} Concursos)",
            "Seleção Manual (40 Dezenas)"
        ]
    )
    
    pool_40 = []
    
    if opcao_estrategia.startswith("Top 3 Grupos"):
        df_rank = ranquear_grupos_quentes(sorteios_historico, GRUPOS_40)
        top_10 = df_rank.head(10)
        
        st.markdown(f"**Top 10 Grupos Individuais nos Últimos {len(sorteios_historico)} Concursos:**")
        st.dataframe(top_10[['Grupo', 'Score', 'Média Acertos', '5+ Acertos']], use_container_width=True)
        
        top_3_nomes = top_10.head(3)['Grupo'].tolist()
        st.success(f"**Grupos Selecionados Automaticamente (Top 3):** {', '.join(top_3_nomes)}")
        pool_40 = sorted(list(set(GRUPOS_40[top_3_nomes[0]] + GRUPOS_40[top_3_nomes[1]] + GRUPOS_40[top_3_nomes[2]])))
        
    elif opcao_estrategia.startswith("Top Trinca"):
        df_top_trincas = ranquear_top_trincas_dinamicas(sorteios_historico, GRUPOS_40, top_n=5)
        if not df_top_trincas.empty:
            st.markdown(f"**Top 5 Melhores Trincas dos Últimos {len(sorteios_historico)} Concursos:**")
            st.dataframe(df_top_trincas[['Trinca', 'Score', 'Senas (6)', 'Quinas (5)', 'Quadras (4)']], use_container_width=True)
            
            trinca_escolhida = st.selectbox("Escolha uma das Top Trincas:", df_top_trincas['Trinca'].tolist())
            row_trinca = df_top_trincas[df_top_trincas['Trinca'] == trinca_escolhida].iloc[0]
            g_list = row_trinca['Grupos']
            pool_40 = sorted(list(set(GRUPOS_40[g_list[0]] + GRUPOS_40[g_list[1]] + GRUPOS_40[g_list[2]])))
        else:
            st.warning("Carregue o histórico para calcular a Top Trinca.")
            grupo_padrao = list(GRUPOS_40.keys())[0]
            pool_40 = GRUPOS_40[grupo_padrao]
            
    else:
        grupo_padrao = list(GRUPOS_40.keys())[0]
        pool_40 = st.multiselect("Selecione 40 dezenas:", options=list(range(1, 61)), default=GRUPOS_40[grupo_padrao])

    st.markdown("---")
    st.subheader("2. Purificação Multicritério (40 ➔ 24 Dezenas) + Atrasos")
    
    if len(pool_40) >= 24:
        dezenas_24 = purificar_dezenas_com_atraso(pool_40, atrasos_dezenas, n_desejado=24)
        st.info(f"**Dezenas Purificadas (24):** {dezenas_24}")
        
        if st.button("⚡ Executar Filtros Gaussiano & Gerar Apostas Diversificadas", type="primary"):
            comb_totais = list(combinations(dezenas_24, 6))
            aprovados = []
            
            for comb in comb_totais:
                if usar_fixas and dezenas_fixas_sel:
                    if not all(d in comb for d in dezenas_fixas_sel):
                        continue

                s = sum(comb)
                if not (min_soma <= s <= max_soma): continue
                if sum(1 for d in comb if d % 2 == 0) not in pares_aceitos: continue
                if sum(1 for d in comb if d in MOLDURA) not in moldura_aceita: continue
                
                c_s = sorted(comb)
                seq, m_seq = 1, 1
                for i in range(len(c_s)-1):
                    if c_s[i+1] == c_s[i] + 1:
                        seq += 1
                        m_seq = max(m_seq, seq)
                    else: seq = 1
                if m_seq > max_seq: continue
                
                if len(set(get_quadrante(d) for d in comb)) < min_quad: continue
                if ultimo_sorteio and sum(1 for d in comb if d in ultimo_sorteio) > max_repetidas: continue
                
                aprovados.append(comb)
                
            st.success(f"**Combinações Filtradas com Sucesso!** Total: {len(aprovados):,}")
            
            if aprovados:
                random.shuffle(aprovados)
                jogos_exibicao = [sorted(list(j)) for j in aprovados[:qtd_exportar]]
                
                df_jogos = pd.DataFrame(jogos_exibicao, columns=[f"Bola {i+1}" for i in range(6)])
                df_jogos.index = df_jogos.index + 1
                
                st.session_state['jogos_gerados_atuais'] = jogos_exibicao
                st.dataframe(df_jogos, use_container_width=True)
                
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_jogos.to_excel(writer, sheet_name='Jogos_Filtrados', index_label='Jogo')
                st.download_button(
                    "📥 Baixar Planilha (.xlsx)", 
                    data=buffer.getvalue(), 
                    file_name="jogos_mega_sena.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.error("Selecione pelo menos 24 dezenas no Pool inicial para continuar.")

with tab_metricas:
    st.subheader(f"📊 Desempenho e Cobertura — {opcao_matriz}")
    if sorteios_historico:
        df_metricas = analisar_metricas_completas_grupos(sorteios_historico, GRUPOS_40)
        st.dataframe(df_metricas, use_container_width=True)
    else:
        st.info("Nenhum dado histórico carregado para exibir métricas.")

with tab_trincas:
    st.subheader("🔥 Top Trincas Dinâmicas de Grupos")
    if sorteios_historico:
        df_trincas_tab = ranquear_top_trincas_dinamicas(sorteios_historico, GRUPOS_40, top_n=15)
        st.dataframe(df_trincas_tab, use_container_width=True)
    else:
        st.info("Nenhum dado histórico carregado para analisar trincas.")
