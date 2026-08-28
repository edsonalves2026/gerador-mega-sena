import streamlit as st
import pandas as pd
import numpy as np
from itertools import combinations
import random
import io
import os

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Gerador Mega-Sena",
    page_icon="🎲",
    layout="centered"
)

# -----------------------------------------------------------------------------
# FUNÇÕES DE PROCESSAMENTO E ESTATÍSTICA
# -----------------------------------------------------------------------------
def carregar_dados_excel(fonte_dados):
    df = pd.read_excel(fonte_dados)
    colunas_dezenas = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    df['dezenas'] = df[colunas_dezenas].values.tolist()
    return df

def obter_24_grupos_fixos():
    return {
        "Grupo_01": [3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 16, 17, 19, 20, 24, 25, 27, 30, 32, 33, 34, 35, 37, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 53, 54, 56, 57, 58, 59, 60],
        "Grupo_02": [1, 2, 4, 5, 6, 8, 10, 11, 13, 14, 17, 21, 22, 23, 24, 26, 27, 28, 29, 30, 32, 33, 35, 36, 38, 40, 41, 42, 44, 45, 46, 48, 49, 50, 51, 52, 53, 54, 56, 59],
        "Grupo_03": [1, 2, 4, 5, 6, 8, 10, 11, 12, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 28, 29, 30, 33, 34, 36, 37, 38, 39, 43, 44, 46, 47, 48, 50, 51, 52, 53, 55, 56, 60],
        "Grupo_04": [1, 2, 3, 5, 7, 8, 9, 15, 16, 17, 18, 20, 22, 23, 26, 27, 28, 31, 32, 33, 34, 35, 37, 38, 39, 41, 42, 43, 45, 48, 49, 50, 51, 52, 53, 54, 55, 57, 58, 59],
        "Grupo_05": [1, 4, 7, 9, 10, 13, 14, 15, 16, 18, 19, 20, 21, 23, 24, 26, 28, 29, 30, 31, 34, 35, 37, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 51, 54, 55, 56, 57, 58, 60],
        "Grupo_06": [2, 3, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 19, 20, 22, 24, 25, 27, 28, 29, 30, 31, 32, 33, 36, 38, 40, 41, 44, 46, 47, 50, 52, 53, 55, 57, 58, 59, 60],
        "Grupo_07": [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 21, 23, 24, 25, 27, 29, 31, 32, 33, 34, 35, 36, 37, 38, 42, 43, 44, 48, 49, 51, 52, 56, 57, 58, 59],
        "Grupo_08": [1, 2, 3, 6, 9, 11, 12, 13, 14, 16, 17, 18, 19, 20, 23, 24, 26, 31, 32, 34, 35, 36, 37, 38, 39, 40, 42, 43, 45, 46, 47, 48, 49, 50, 52, 53, 54, 55, 58, 60],
        "Grupo_09": [1, 3, 4, 5, 6, 7, 8, 9, 11, 13, 15, 17, 19, 21, 22, 23, 25, 27, 28, 29, 30, 31, 34, 35, 36, 37, 39, 41, 45, 46, 48, 50, 51, 53, 54, 56, 57, 58, 59, 60],
        "Grupo_10": [2, 4, 6, 7, 8, 10, 14, 15, 16, 17, 18, 19, 22, 24, 25, 26, 27, 28, 30, 31, 32, 33, 34, 35, 38, 39, 40, 42, 43, 45, 47, 48, 49, 50, 51, 52, 54, 56, 57, 60],
        "Grupo_11": [4, 7, 8, 9, 10, 12, 13, 15, 18, 20, 22, 23, 25, 27, 29, 30, 31, 32, 33, 36, 37, 38, 40, 41, 42, 43, 44, 45, 47, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 60],
        "Grupo_12": [1, 2, 3, 5, 9, 10, 11, 12, 14, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 34, 35, 36, 37, 40, 41, 43, 44, 46, 47, 48, 50, 51, 52, 54, 57, 59, 60],
        "Grupo_13": [1, 3, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 20, 21, 24, 25, 26, 27, 28, 31, 33, 35, 37, 38, 39, 40, 42, 43, 44, 45, 46, 47, 50, 53, 55, 56, 57, 58, 59],
        "Grupo_14": [1, 3, 4, 5, 8, 9, 12, 13, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 29, 31, 32, 33, 34, 36, 39, 40, 41, 42, 44, 46, 47, 48, 49, 53, 54, 55, 56, 59],
        "Grupo_15": [1, 2, 3, 6, 8, 10, 11, 12, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 27, 28, 29, 30, 32, 33, 34, 35, 36, 37, 40, 41, 43, 45, 48, 49, 51, 52, 54, 55, 56, 58],
        "Grupo_16": [2, 3, 4, 5, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 25, 29, 30, 31, 34, 35, 37, 38, 39, 42, 43, 46, 47, 49, 50, 51, 52, 54, 56, 57, 58, 59],
        "Grupo_17": [2, 3, 4, 6, 7, 9, 10, 12, 14, 17, 20, 21, 22, 23, 24, 25, 26, 28, 29, 31, 32, 33, 34, 35, 36, 38, 39, 41, 43, 44, 45, 46, 48, 49, 50, 53, 55, 57, 58, 60],
        "Grupo_18": [2, 5, 6, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 23, 24, 25, 26, 27, 28, 30, 31, 33, 34, 35, 36, 37, 39, 41, 42, 44, 47, 48, 50, 51, 52, 53, 57, 58, 59, 60],
        "Grupo_19": [1, 3, 4, 5, 6, 7, 8, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 30, 32, 33, 34, 35, 37, 38, 40, 41, 42, 44, 47, 48, 49, 50, 51, 54, 55, 59, 60],
        "Grupo_20": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 17, 18, 22, 23, 24, 25, 28, 30, 32, 36, 38, 40, 43, 44, 45, 46, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59],
        "Grupo_21": [1, 2, 5, 7, 8, 9, 10, 11, 14, 15, 16, 19, 20, 23, 24, 25, 26, 27, 28, 29, 30, 32, 33, 34, 35, 38, 39, 41, 42, 44, 45, 46, 48, 49, 51, 52, 54, 57, 58, 60],
        "Grupo_22": [1, 3, 4, 5, 8, 9, 10, 11, 12, 17, 18, 19, 21, 22, 25, 26, 27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 43, 44, 46, 48, 49, 51, 52, 53, 54, 56, 57],
        "Grupo_23": [1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 17, 18, 21, 23, 24, 25, 27, 28, 29, 32, 34, 36, 37, 41, 43, 45, 47, 49, 50, 52, 53, 54, 55, 56, 57, 58, 59, 60],
        "Grupo_24": [4, 5, 6, 7, 10, 11, 12, 15, 16, 17, 18, 19, 20, 22, 24, 25, 27, 28, 30, 31, 32, 33, 34, 35, 36, 37, 38, 40, 42, 45, 46, 47, 48, 50, 51, 52, 53, 55, 56, 60]
    }

def reduzir_40_para_24_dezenas(dezenas_40, df_historico):
    ultimos_50 = df_historico[['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']].tail(50).values.flatten()
    todos_jogos = df_historico['dezenas'].tolist()
    pontuacao = {}
    
    for d in dezenas_40:
        freq_recente = np.sum(ultimos_50 == d)
        atraso = 0
        for jogo in reversed(todos_jogos):
            if d in jogo:
                break
            atraso += 1
        score = (freq_recente * 0.7) + (min(atraso, 15) * 0.3)
        pontuacao[d] = score

    dezenas_ordenadas = sorted(pontuacao.items(), key=lambda x: x[1], reverse=True)
    return sorted([d for d, _ in dezenas_ordenadas[:24]])

def calcular_score_decaimento_vetorizado(df_janela, grupos):
    n = len(df_janela)
    pesos = np.linspace(1.0, 2.0, n)
    scores = {}
    sorteados_matriz = np.array(df_janela['dezenas'].tolist())
    
    for nome_g, grupo in grupos.items():
        set_g = set(grupo)
        acertos = np.array([len(set_g.intersection(set(row))) for row in sorteados_matriz])
        pontos_max = (acertos >= 5) * 50 * pesos
        pontos_inter = (acertos == 4) * 20 * pesos
        pontos_media = (acertos / 6) * 10 * pesos
        scores[nome_g] = np.sum(pontos_max + pontos_inter + pontos_media)
        
    return pd.Series(scores).sort_values(ascending=False)

def calcular_atrasos_historico(df_historico, pool_dezenas):
    historico_reverso = df_historico['dezenas'].tolist()[::-1]
    atrasos = {}
    for d in pool_dezenas:
        atraso = 0
        for sorteio in historico_reverso:
            if d in sorteio:
                break
            atraso += 1
        atrasos[d] = atraso
    return atrasos

def purificar_pool_multi_camada(pool_bruto, df_historico, total_alvo=24, vagas_atrasadas=4):
    df_j15 = df_historico.iloc[-15:]
    df_j50 = df_historico.iloc[-50:]
    
    arr_j15 = np.concatenate(df_j15['dezenas'].values)
    arr_j50 = np.concatenate(df_j50['dezenas'].values)
    arr_geral = np.concatenate(df_historico['dezenas'].values)
    
    freq_j15 = dict(zip(*np.unique(arr_j15, return_counts=True)))
    freq_j50 = dict(zip(*np.unique(arr_j50, return_counts=True)))
    freq_geral = dict(zip(*np.unique(arr_geral, return_counts=True)))
    
    scores_dezenas = {}
    max_j15 = max(freq_j15.values()) if freq_j15 else 1
    max_j50 = max(freq_j50.values()) if freq_j50 else 1
    max_geral = max(freq_geral.values()) if freq_geral else 1
    
    for d in pool_bruto:
        score_15 = (freq_j15.get(d, 0) / max_j15) * 0.50
        score_50 = (freq_j50.get(d, 0) / max_j50) * 0.30
        score_geral = (freq_geral.get(d, 0) / max_geral) * 0.20
        scores_dezenas[d] = score_15 + score_50 + score_geral
        
    dezenas_ordenadas = sorted(pool_bruto, key=lambda d: scores_dezenas[d], reverse=True)
    
    vagas_quentes = total_alvo - vagas_atrasadas
    top_quentes = dezenas_ordenadas[:vagas_quentes]
    restantes = dezenas_ordenadas[vagas_quentes:]
    
    atrasos_dict = calcular_atrasos_historico(df_historico, restantes)
    candidatas_atrasadas = sorted(restantes, key=lambda d: atrasos_dict[d], reverse=True)
    pool_candidatas_atrasadas = candidatas_atrasadas[:vagas_atrasadas * 2]
    
    if len(pool_candidatas_atrasadas) >= vagas_atrasadas:
        pesos_atraso = [atrasos_dict[d] for d in pool_candidatas_atrasadas]
        soma_pesos = sum(pesos_atraso)
        pesos_norm = [p / soma_pesos for p in pesos_atraso] if soma_pesos > 0 else None
        
        top_atrasadas = sorted(np.random.choice(
            pool_candidatas_atrasadas, 
            size=vagas_atrasadas, 
            replace=False, 
            p=pesos_norm
        ).tolist())
    else:
        top_atrasadas = sorted(candidatas_atrasadas[:vagas_atrasadas])
    
    return sorted(top_quentes + top_atrasadas)

def obter_faixa_repetidas_dinamica(df_historico):
    ultimos_5 = df_historico.iloc[-5:]
    repeticoes = []
    for i in range(1, len(ultimos_5)):
        rep = len(set(ultimos_5.iloc[i]['dezenas']).intersection(set(ultimos_5.iloc[i-1]['dezenas'])))
        repeticoes.append(rep)
    
    media = np.mean(repeticoes) if repeticoes else 1.0
    if media <= 1.2:
        return [0, 1]
    elif media <= 2.0:
        return [1, 2]
    else:
        return [1, 2, 3]

def validar_apostas_vetorizadas(matriz_apostas, ultimo_concurso, faixa_repetidas):
    somas = np.sum(matriz_apostas, axis=1)
    mask_soma = (somas >= 140) & (somas <= 220)
    
    pares = np.sum(matriz_apostas % 2 == 0, axis=1)
    mask_paridade = (pares >= 2) & (pares <= 4)
    
    moldura_set = {1,2,3,4,5,6,7,8,9,10,11,20,21,30,31,40,41,50,51,52,53,54,55,56,57,58,59,60}
    qtd_moldura = np.sum(np.isin(matriz_apostas, list(moldura_set)), axis=1)
    mask_moldura = (qtd_moldura >= 2) & (qtd_moldura <= 5)
    
    qtd_repetidos = np.sum(np.isin(matriz_apostas, ultimo_concurso), axis=1)
    mask_repetidos = np.isin(qtd_repetidos, faixa_repetidas)
    
    diferencas = np.diff(matriz_apostas, axis=1)
    mask_consecutivos = (np.sum(diferencas == 1, axis=1) <= 1)
    
    q1 = np.sum((matriz_apostas >= 1) & (matriz_apostas <= 15), axis=1)
    q2 = np.sum((matriz_apostas >= 16) & (matriz_apostas <= 30), axis=1)
    q3 = np.sum((matriz_apostas >= 31) & (matriz_apostas <= 45), axis=1)
    q4 = np.sum((matriz_apostas >= 46) & (matriz_apostas <= 60), axis=1)
    
    quadrantes_matriz = np.column_stack([q1, q2, q3, q4])
    zeros_count = np.sum(quadrantes_matriz == 0, axis=1)
    max_quadrante = np.max(quadrantes_matriz, axis=1)
    mask_quadrantes = (zeros_count <= 1) & (max_quadrante <= 3)
    
    return mask_soma & mask_paridade & mask_moldura & mask_repetidos & mask_consecutivos & mask_quadrantes

def gerar_texto_exportacao(apostas, pool, faixa_repetidas, modo_nome):
    output = io.StringIO()
    output.write("==================================================\n")
    output.write(f"     MEGA-SENA - JOGOS GERADOS ({modo_nome})\n")
    output.write("==================================================\n\n")
    output.write(f"POOL SELECIONADO COM ROTAÇÃO (24 DEZENAS):\n")
    output.write(f"{sorted(pool)}\n\n")
    output.write(f"FAIXA DE REPETIDAS ACEITA: {faixa_repetidas}\n")
    output.write("==================================================\n")
    output.write(f"APOSTAS SIMPLES VALIDADAS ({len(apostas)} JOGOS):\n")
    output.write("==================================================\n\n")
    
    for idx, aposta in enumerate(apostas, 1):
        aposta_fmt = " - ".join(f"{num:02d}" for num in sorted(aposta))
        output.write(f"Jogo {idx:02d}: {aposta_fmt}\n")
        
    output.write("\n==================================================\n")
    output.write("Filtros Aplicados: Soma (140-220), Paridade (2-4P),\n")
    output.write("Moldura (2-5), Repetição Dinâmica, Consecutivos (<=1 par)\n")
    output.write("e Quadrantes (máx 1 zerado, máx 3 por qdt).\n")
    output.write("==================================================\n")
    
    return output.getvalue()

# -----------------------------------------------------------------------------
# INTERFACE DO STREAMLIT
# -----------------------------------------------------------------------------
st.title("🎲 Gerador Otimizado Mega-Sena")

# Painel Lateral para Opções
st.sidebar.header("⚙️ Configurações")
modo_selecionado = st.sidebar.radio(
    "Escolha o Modo de Geração:",
    ("Automático (Análise de Grupos)", "Manual (Sua Escolha de 40 Dezenas)")
)

qtd_jogos = st.sidebar.number_input("Quantidade de Jogos:", min_value=1, max_value=200, value=30, step=1)

dezenas_manuais_input = []
if modo_selecionado == "Manual (Sua Escolha de 40 Dezenas)":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Dezenas Selecionadas")
    dezenas_manuais_input = st.sidebar.multiselect(
        "Escolha exatamente 40 dezenas:",
        options=list(range(1, 61)),
        default=[1, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 22, 23, 25,
                 27, 28, 30, 31, 33, 34, 35, 37, 38, 40, 41, 42, 44, 45, 47, 49, 50, 52, 55, 58]
    )

# Identificação da Planilha
arquivo_padrao = "mega_sena.xlsx"
fonte_excel = None

if os.path.exists(arquivo_padrao):
    st.success("Planilha local 'mega_sena.xlsx' carregada com sucesso!")
    fonte_excel = arquivo_padrao
else:
    uploaded_file = st.file_uploader("Selecione a planilha Excel (.xlsx)", type=["xlsx"])
    if uploaded_file is not None:
        fonte_excel = uploaded_file

# Botão de Execução Principais
if fonte_excel is not None:
    if st.button("Gerar Palpites"):
        if modo_selecionado.startswith("Manual") and len(dezenas_manuais_input) != 40:
            st.error(f"Selecione exatamente 40 dezenas. Atualmente você escolheu {len(dezenas_manuais_input)}.")
        else:
            with st.spinner("Processando histórico e aplicando filtros estatísticos..."):
                df_historico = carregar_dados_excel(fonte_excel)
                ultimo_concurso = df_historico.iloc[-1]['dezenas']
                
                if modo_selecionado.startswith("Manual"):
                    modo_nome = "MODO MANUAL"
                    pool_bruto = reduzir_40_para_24_dezenas(dezenas_manuais_input, df_historico)
                    st.info("Modo Manual: 40 dezenas reduzidas para as 24 mais promissoras.")
                else:
                    modo_nome = "MODO AUTOMÁTICO"
                    grupos = obter_24_grupos_fixos()
                    janela_50 = df_historico.iloc[-50:]
                    ranking_grupos = calcular_score_decaimento_vetorizado(janela_50, grupos)
                    top_5_grupos = ranking_grupos.head(5).index.tolist()
                    pool_bruto = sorted(list(set().union(*[grupos[g] for g in top_5_grupos])))
                    st.success(f"Top 5 Grupos Selecionados: {', '.join(top_5_grupos)}")

                # Purificação e Filtros
                pool_purificado = purificar_pool_multi_camada(
                    pool_bruto=pool_bruto,
                    df_historico=df_historico,
                    total_alvo=24,
                    vagas_atrasadas=4
                )
                
                faixa_repetidas = obter_faixa_repetidas_dinamica(df_historico)
                
                todas_combinacoes = np.array(list(combinations(pool_purificado, 6)))
                mask_validos = validar_apostas_vetorizadas(todas_combinacoes, ultimo_concurso, faixa_repetidas)
                apostas_filtradas = todas_combinacoes[mask_validos]
                
                np.random.shuffle(apostas_filtradas)
                apostas_finais = apostas_filtradas[:qtd_jogos].tolist()
                
                # Exibição
                st.info(f"Pool Final (24 Dezenas): {sorted(pool_purificado)}")
                st.subheader(f"Jogos Gerados ({len(apostas_finais)}):")
                
                texto_jogos = ""
                for idx, aposta in enumerate(apostas_finais, 1):
                    aposta_fmt = " - ".join(f"{num:02d}" for num in sorted(aposta))
                    texto_jogos += f"Jogo {idx:02d}: {aposta_fmt}\n"
                
                st.code(texto_jogos, language="text")
                
                # Exportação
                conteudo_txt = gerar_texto_exportacao(apostas_finais, pool_purificado, faixa_repetidas, modo_nome)
                st.download_button(
                    label="📥 Baixar Arquivo de Jogos (.txt)",
                    data=conteudo_txt,
                    file_name="jogos_mega_sena.txt",
                    mime="text/plain"
                )
else:
    st.info("Aguardando carregamento da planilha para liberar a geração.")
