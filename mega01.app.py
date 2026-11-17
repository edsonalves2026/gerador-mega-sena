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
from collections import Counter

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
            # ADICIONE ESTAS DUAS LINHAS ABAIXO PARA VOLTAR A ENTRAR COM MEGA-SENA/2026
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
    "Grupo 20": [1, 2, 3, 6, 9, 10, 12, 13, 15, 16, 17, 18, 19, 21, 22, 24, 25, 27, 28, 30, 31, 32, 33, 36, 37, 39, 40, 41, 44, 45, 46, 48, 49, 51, 52, 54, 57, 58, 59, 60],
    "Grupo 21": [2, 3, 4, 5, 8, 9, 11, 12, 14, 16, 17, 19, 20, 21, 23, 25, 26, 27, 29, 31, 32, 34, 35, 36, 38, 40, 42, 43, 44, 47, 48, 50, 51, 53, 55, 56, 57, 59, 60],
    "Grupo 22": [1, 4, 6, 7, 8, 10, 11, 13, 14, 15, 18, 19, 20, 22, 23, 24, 25, 28, 29, 30, 32, 33, 35, 37, 38, 39, 41, 42, 45, 46, 47, 49, 50, 52, 53, 55, 56, 58, 59, 60],
    "Grupo 23": [1, 2, 3, 5, 6, 7, 10, 12, 13, 15, 16, 17, 18, 21, 22, 24, 26, 27, 28, 30, 31, 33, 34, 36, 37, 39, 40, 43, 44, 45, 46, 48, 49, 51, 52, 54, 57, 58, 59, 60],
    "Grupo 24": [2, 3, 4, 8, 9, 11, 12, 14, 16, 17, 19, 20, 21, 23, 25, 26, 29, 30, 31, 32, 34, 35, 36, 38, 39, 41, 42, 43, 44, 47, 48, 50, 52, 53, 55, 56, 57, 58, 59, 60]
}

MATRIZ_51_GRUPOS = {
     "Grupo 01": [1, 3, 5, 6, 9, 12, 13, 14, 17, 18, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30, 33, 35, 36, 37, 38, 39, 41, 43, 44, 45, 46, 47, 49, 50, 51, 53, 55, 56, 57, 60],
    "Grupo 02": [1, 2, 5, 6, 7, 8, 9, 11, 14, 17, 18, 21, 22, 23, 25, 26, 27, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 54, 59, 60],
    "Grupo 03": [1, 2, 3, 5, 7, 8, 11, 12, 13, 14, 17, 18, 20, 21, 23, 25, 26, 27, 28, 29, 30, 33, 34, 36, 39, 40, 41, 42, 43, 44, 45, 46, 50, 52, 54, 55, 56, 57, 59, 60],
    "Grupo 04": [1, 2, 3, 6, 7, 8, 9, 11, 12, 13, 20, 21, 22, 23, 26, 27, 28, 29, 30, 33, 34, 35, 36, 37, 38, 40, 42, 43, 45, 46, 47, 49, 51, 52, 53, 54, 55, 56, 57, 59],
    "Grupo 05": [2, 3, 4, 6, 7, 8, 10, 11, 14, 15, 16, 19, 20, 21, 24, 26, 27, 30, 31, 32, 34, 35, 36, 37, 39, 40, 42, 43, 44, 47, 48, 49, 50, 52, 54, 55, 57, 58, 59, 60],
    "Grupo 06": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 16, 17, 18, 19, 20, 22, 24, 25, 30, 31, 32, 34, 35, 37, 38, 40, 41, 42, 47, 48, 49, 51, 52, 53, 54, 55, 57, 58, 59],
    "Grupo 07": [2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14, 17, 18, 20, 22, 25, 28, 29, 30, 34, 35, 37, 38, 39, 40, 41, 42, 44, 47, 49, 50, 51, 52, 53, 54, 55, 56, 57, 59, 60],
    "Grupo 08": [1, 5, 8, 9, 12, 13, 14, 15, 16, 17, 18, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 33, 36, 38, 39, 40, 41, 43, 44, 45, 46, 48, 50, 51, 52, 53, 54, 56, 59, 60],
    "Grupo 09": [1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 13, 15, 16, 19, 20, 23, 24, 28, 29, 30, 31, 32, 33, 34, 35, 37, 40, 42, 45, 46, 47, 48, 49, 52, 54, 55, 56, 57, 58, 59],
    "Grupo 10": [1, 3, 5, 6, 8, 12, 13, 15, 16, 17, 18, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 35, 36, 37, 40, 41, 43, 45, 46, 47, 48, 49, 52, 54, 55, 56, 57, 59],
    "Grupo 11": [1, 3, 6, 8, 9, 12, 13, 14, 15, 16, 20, 22, 23, 24, 28, 29, 30, 31, 33, 35, 37, 38, 39, 40, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 59, 60],
    "Grupo 12": [3, 5, 6, 8, 9, 14, 15, 16, 17, 18, 20, 21, 22, 24, 25, 26, 27, 30, 31, 35, 36, 37, 38, 39, 40, 41, 43, 44, 47, 48, 49, 50, 51, 52, 53, 54, 55, 57, 59, 60],
    "Grupo 13": [1, 2, 5, 6, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18, 22, 23, 24, 25, 28, 29, 31, 33, 34, 35, 37, 38, 39, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 53, 56, 60],
    "Grupo 14": [1, 2, 3, 4, 5, 7, 8, 10, 11, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 36, 40, 41, 42, 43, 45, 46, 48, 52, 54, 55, 57, 58, 59],
    "Grupo 15": [2, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18, 21, 24, 25, 26, 27, 28, 29, 31, 34, 35, 36, 37, 39, 40, 41, 42, 43, 44, 47, 48, 49, 50, 52, 54, 56, 59, 60],
    "Grupo 16": [1, 2, 3, 5, 7, 9, 11, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 30, 31, 33, 34, 36, 38, 39, 41, 42, 43, 44, 45, 46, 48, 50, 51, 53, 55, 57, 60],
    "Grupo 17": [2, 3, 5, 6, 7, 9, 11, 12, 13, 15, 16, 17, 18, 20, 21, 22, 24, 25, 26, 27, 28, 29, 30, 31, 34, 35, 36, 37, 38, 41, 42, 43, 47, 48, 49, 51, 53, 55, 56, 57],
    "Grupo 18": [1, 2, 3, 4, 6, 7, 9, 10, 11, 14, 15, 16, 19, 20, 22, 23, 24, 30, 31, 32, 33, 34, 35, 37, 38, 39, 42, 44, 45, 46, 47, 48, 49, 50, 51, 53, 55, 57, 58, 60],
    "Grupo 19": [1, 2, 3, 6, 7, 11, 12, 13, 14, 15, 16, 20, 21, 23, 24, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36, 37, 39, 42, 43, 44, 45, 46, 47, 48, 49, 50, 55, 56, 57, 60],
    "Grupo 20": [1, 2, 3, 5, 7, 8, 9, 11, 12, 13, 15, 16, 17, 18, 20, 22, 23, 24, 25, 28, 29, 30, 31, 33, 34, 38, 40, 41, 42, 45, 46, 48, 51, 52, 53, 54, 55, 56, 57, 59],
    "Grupo 21": [2, 3, 7, 8, 9, 11, 12, 13, 14, 15, 16, 20, 21, 22, 24, 26, 27, 28, 29, 30, 31, 34, 36, 38, 39, 40, 42, 43, 44, 48, 50, 51, 52, 53, 54, 55, 56, 57, 59, 60],
    "Grupo 22": [2, 3, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 24, 25, 28, 29, 30, 31, 32, 34, 38, 39, 41, 42, 44, 48, 50, 51, 53, 55, 56, 57, 58, 60],
    "Grupo 23": [1, 2, 3, 4, 7, 9, 10, 11, 12, 13, 15, 16, 19, 20, 21, 22, 23, 24, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 38, 42, 43, 45, 46, 48, 51, 53, 55, 56, 57, 58],
    "Grupo 24": [1, 2, 3, 5, 6, 7, 8, 11, 14, 15, 16, 17, 18, 20, 23, 24, 25, 30, 31, 33, 34, 35, 37, 39, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 52, 54, 55, 57, 59, 60],
    "Grupo 25": [4, 5, 6, 8, 9, 10, 12, 13, 14, 17, 18, 19, 21, 22, 25, 26, 27, 28, 29, 32, 35, 36, 37, 38, 39, 40, 41, 43, 44, 47, 49, 50, 51, 52, 53, 54, 56, 58, 59, 60],
    "Grupo 26": [1, 3, 4, 5, 8, 9, 10, 12, 13, 17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30, 32, 33, 36, 38, 40, 41, 43, 45, 46, 51, 52, 53, 54, 55, 56, 57, 58, 59],
    "Grupo 27": [2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 22, 24, 28, 29, 31, 32, 34, 35, 37, 38, 39, 40, 42, 44, 47, 48, 49, 50, 51, 52, 53, 54, 56, 58, 59, 60],
    "Grupo 28": [1, 3, 4, 5, 6, 8, 9, 10, 14, 17, 18, 19, 20, 22, 23, 25, 30, 32, 33, 35, 37, 38, 39, 40, 41, 44, 45, 46, 47, 49, 50, 51, 52, 53, 54, 55, 57, 58, 59, 60],
    "Grupo 29": [1, 3, 4, 6, 8, 10, 12, 13, 14, 19, 20, 21, 23, 26, 27, 28, 29, 30, 32, 33, 35, 36, 37, 39, 40, 43, 44, 45, 46, 47, 49, 50, 52, 54, 55, 56, 57, 58, 59, 60],
    "Grupo 30": [1, 2, 4, 5, 7, 9, 10, 11, 12, 13, 14, 17, 18, 19, 21, 22, 23, 25, 26, 27, 28, 29, 32, 33, 34, 36, 38, 39, 41, 42, 43, 44, 45, 46, 50, 51, 53, 56, 58, 60],
    "Grupo 31": [1, 2, 4, 6, 7, 8, 9, 10, 11, 15, 16, 19, 21, 22, 23, 24, 26, 27, 31, 32, 33, 34, 35, 36, 37, 38, 40, 42, 43, 45, 46, 47, 48, 49, 51, 52, 53, 54, 58, 59],
    "Grupo 32": [1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 17, 18, 19, 23, 25, 28, 29, 32, 33, 34, 35, 37, 39, 40, 41, 42, 44, 45, 46, 47, 49, 50, 52, 54, 56, 58, 59, 60],
    "Grupo 33": [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 17, 18, 19, 20, 22, 23, 25, 28, 29, 30, 32, 33, 34, 35, 37, 38, 41, 42, 45, 46, 47, 49, 51, 53, 55, 56, 57, 58],
    "Grupo 34": [2, 3, 4, 6, 7, 9, 10, 11, 12, 13, 14, 19, 20, 21, 22, 26, 27, 28, 29, 30, 32, 34, 35, 36, 37, 38, 39, 42, 43, 44, 47, 49, 50, 51, 53, 55, 56, 57, 58, 60],
    "Grupo 35": [1, 2, 3, 4, 5, 6, 7, 10, 11, 14, 17, 18, 19, 20, 21, 23, 25, 26, 27, 30, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 49, 50, 55, 57, 58, 60],
    "Grupo 36": [1, 2, 4, 7, 8, 10, 11, 12, 13, 14, 15, 16, 19, 21, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 36, 39, 40, 42, 43, 44, 45, 46, 48, 50, 52, 54, 56, 58, 59, 60],
    "Grupo 37": [1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 13, 14, 19, 20, 22, 23, 28, 29, 30, 32, 33, 34, 38, 39, 40, 42, 44, 45, 46, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60],
    "Grupo 38": [2, 3, 4, 5, 7, 8, 9, 10, 11, 14, 17, 18, 19, 20, 21, 22, 25, 26, 27, 30, 32, 34, 36, 38, 39, 40, 41, 42, 43, 44, 50, 51, 52, 53, 54, 55, 57, 58, 59, 60],
    "Grupo 39": [1, 2, 4, 5, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 22, 23, 24, 25, 31, 32, 33, 34, 38, 39, 40, 41, 42, 44, 45, 46, 48, 50, 51, 52, 53, 54, 58, 59, 60],
    "Grupo 40": [2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 17, 18, 19, 20, 21, 25, 26, 27, 28, 29, 30, 32, 34, 35, 36, 37, 40, 41, 42, 43, 47, 49, 52, 54, 55, 56, 57, 58, 59],
    "Grupo 41": [2, 4, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 21, 22, 24, 25, 26, 27, 28, 29, 31, 32, 34, 36, 38, 40, 41, 42, 43, 48, 51, 52, 53, 54, 56, 58, 59],
    "Grupo 42": [1, 4, 6, 9, 10, 12, 13, 14, 15, 16, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 35, 36, 37, 38, 39, 43, 44, 45, 46, 47, 48, 49, 50, 51, 53, 56, 58, 60],
    "Grupo 43": [1, 4, 5, 6, 8, 9, 10, 12, 13, 15, 16, 17, 18, 19, 22, 23, 24, 25, 28, 29, 31, 32, 33, 35, 37, 38, 40, 41, 45, 46, 47, 48, 49, 51, 52, 53, 54, 56, 58, 59],
    "Grupo 44": [2, 4, 5, 6, 7, 9, 10, 11, 14, 15, 16, 17, 18, 19, 21, 22, 24, 25, 26, 27, 31, 32, 34, 35, 36, 37, 38, 39, 41, 42, 43, 44, 47, 48, 49, 50, 51, 53, 58, 60],
    "Grupo 45": [1, 2, 4, 5, 6, 7, 10, 11, 12, 13, 15, 16, 17, 18, 19, 21, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34, 35, 36, 37, 41, 42, 43, 45, 46, 47, 48, 49, 56, 58],
    "Grupo 46": [1, 4, 5, 6, 8, 10, 14, 15, 16, 17, 18, 19, 21, 23, 24, 25, 26, 27, 31, 32, 33, 35, 36, 37, 39, 40, 41, 43, 44, 45, 46, 47, 48, 49, 50, 52, 54, 58, 59, 60],
    "Grupo 47": [1, 3, 4, 5, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 36, 39, 41, 43, 44, 45, 46, 48, 50, 55, 56, 57, 58, 60],
    "Grupo 48": [1, 3, 4, 5, 6, 9, 10, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 30, 31, 32, 33, 35, 36, 37, 38, 41, 43, 45, 46, 47, 48, 49, 51, 53, 55, 57, 58],
    "Grupo 49": [3, 4, 5, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 24, 25, 28, 29, 30, 31, 32, 35, 37, 39, 40, 41, 44, 47, 48, 49, 50, 52, 54, 55, 56, 57, 58, 59, 60],
    "Grupo 50": [3, 4, 6, 8, 9, 10, 12, 13, 15, 16, 19, 20, 21, 22, 24, 26, 27, 28, 29, 30, 31, 32, 35, 36, 37, 38, 40, 43, 47, 48, 49, 51, 52, 53, 54, 55, 56, 57, 58, 59],
    "Grupo 51": [1, 3, 4, 8, 9, 10, 14, 15, 16, 19, 20, 21, 22, 23, 24, 26, 27, 30, 31, 32, 33, 36, 38, 39, 40, 43, 44, 45, 46, 48, 50, 51, 52, 53, 54, 55, 57, 58, 59, 60]
}

st.sidebar.header("📐 Matriz de Referência")
opcao_matriz = st.sidebar.radio(
    "Selecione a Matriz para Análise:",
    ("Matriz Principal (24 Grupos)", "Nova Matriz (51 Grupos)")
)

GRUPOS_ATIVOS = MATRIZ_51_GRUPOS if opcao_matriz == "Nova Matriz (51 Grupos)" else MATRIZ_24_GRUPOS

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

# --- FUNÇÃO DE MOMENTUM (REPRODUTÍVEL COM SEED) ---
def calcular_momentum_inteligente(sorteios_recentes, janela_recente=30):
    if not sorteios_recentes:
        return {d: 10.0 for d in range(1, 61)}
        
    freq_recente = {d: 0 for d in range(1, 61)}
    ultima_aparicao = {d: -1 for d in range(1, 61)}
    
    total_sorteios = len(sorteios_recentes)
    janela_inicio = max(0, total_sorteios - janela_recente)
    
    for idx, s in enumerate(sorteios_recentes):
        for d in s:
            if 1 <= d <= 60:
                ultima_aparicao[d] = idx
                if idx >= janela_inicio:
                    freq_recente[d] += 1
                
    pontuacao = {}
    # Usa uma seed baseada no último concurso para que o fator sorte seja fixo por análise
    seed_val = hash(tuple(sorteios_recentes[-1])) if sorteios_recentes else 42
    rng = random.Random(seed_val)
    
    for d in range(1, 61):
        base_forca = freq_recente[d] * 15 
        fadiga = -20 if freq_recente[d] == 5 else (-40 if freq_recente[d] >= 6 else 0)
            
        atraso = (total_sorteios - 1) - ultima_aparicao[d]
        
        bonus_timing = 0
        if atraso == 0:
            bonus_timing = 25  # Repetição imediata
        elif 4 <= atraso <= 7:
            bonus_timing = 40  # Ponto de virada
        elif atraso >= 15:
            bonus_timing = -10 
            
        fator_sorte = rng.random() * 5
        pontuacao[d] = max(1.0, base_forca + fadiga + bonus_timing + fator_sorte)
        
    return pontuacao

# --- FUNÇÃO DE PURIFICAÇÃO COM BALANCEAMENTO REAL POR QUADRANTE ---
def purificar_com_momentum(pool, pontuacao_momentum, n_desejado=24):
    candidatos = sorted(pool, key=lambda d: pontuacao_momentum.get(d, 0), reverse=True)
    por_q = {1: [], 2: [], 3: [], 4: []}
    for d in candidatos:
        por_q[get_quadrante(d)].append(d)

    # Meta exata de 6 dezenas por quadrante (já que 24/4 = 6)
    alvo_por_q = {q: n_desejado // 4 for q in range(1, 5)}
    resto = n_desejado - sum(alvo_por_q.values())
    
    # Distribui o resto para os quadrantes com mais opções
    for q in sorted(range(1, 5), key=lambda q: len(por_q[q]), reverse=True)[:resto]:
        alvo_por_q[q] += 1

    selecionadas = []
    for q in range(1, 5):
        selecionadas.extend(por_q[q][:alvo_por_q[q]])

    # Fallback caso algum quadrante não tenha o suficiente no pool
    if len(selecionadas) < n_desejado:
        restantes = [d for d in candidatos if d not in selecionadas]
        selecionadas.extend(restantes[:n_desejado - len(selecionadas)])

    # Ajuste de paridade (corrige os dois lados: muitos pares ou muitos ímpares)
    pares = [d for d in selecionadas if d % 2 == 0]
    impares = [d for d in selecionadas if d % 2 != 0]
    alvo_pares = n_desejado // 2
    
    if len(pares) > alvo_pares + 2:
        for d in candidatos:
            if d % 2 != 0 and d not in selecionadas:
                pior_par = min(pares, key=lambda x: pontuacao_momentum.get(x, 0))
                selecionadas.remove(pior_par)
                selecionadas.append(d)
                break
    elif len(pares) < alvo_pares - 2:
        for d in candidatos:
            if d % 2 == 0 and d not in selecionadas:
                pior_impar = min(impares, key=lambda x: pontuacao_momentum.get(x, 0))
                selecionadas.remove(pior_impar)
                selecionadas.append(d)
                break

    return sorted(selecionadas)

def aplicar_diversificacao(comb_aprovadas, limite_max=50):
    if not comb_aprovadas: return []
    selecionados = []
    restantes = list(comb_aprovadas)
    random.shuffle(restantes)
    while restantes and len(selecionados) < limite_max:
        escolhido = restantes.pop(0)
        selecionados.append(escolhido)
        set_e = set(escolhido)
        novos_restantes = []
        for c in restantes:
            overlap = len(set_e.intersection(set(c)))
            if overlap < 4: # Evita clones
                novos_restantes.append(c)
        restantes = novos_restantes
    return selecionados

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

def ranquear_grupos_por_compatibilidade(dezenas_quentes, grupos_dict, n_dezenas_aposta):
    q = set(dezenas_quentes)
    rows = []
    for nome, dezenas in grupos_dict.items():
        g = set(dezenas)
        inter = g & q
        rows.append({
            "Grupo": nome,
            "Dezenas Quentes no Grupo": len(inter),
            "Cobertura da Aposta": round(len(inter) / max(n_dezenas_aposta, 1), 3),
            "Score Compatibilidade": len(inter) * 10 + len(inter) / max(n_dezenas_aposta, 1),
        })
    return pd.DataFrame(rows).sort_values("Score Compatibilidade", ascending=False).reset_index(drop=True)

def ranquear_top_trincas_dinamicas(sorteios, grupos_dict, top_n=5):
    if not sorteios: return pd.DataFrame()
    nomes_grupos = list(grupos_dict.keys())
    comb_trincas = list(combinations(nomes_grupos, 3))
    resultados = []
    
    for g1, g2, g3 in comb_trincas:
        todas_dezenas = grupos_dict[g1] + grupos_dict[g2] + grupos_dict[g3]
        contagem = Counter(todas_dezenas)
        # Mantém as 40 mais frequentes da união dos 3 grupos
        pool_ordenado = sorted(contagem.keys(), key=lambda d: (contagem[d], d), reverse=True)
        pool_unificado = set(pool_ordenado[:40])
        
        senas, quinas, quadras = 0, 0, 0
        soma_acertos = 0
        
        for s in sorteios:
            ac = len(set(s).intersection(pool_unificado))
            soma_acertos += ac
            if ac == 6: senas += 1
            elif ac == 5: quinas += 1
            elif ac == 4: quadras += 1
            
        score = (senas * 1000000) + (quinas * 1000) + (quadras * 10) + soma_acertos
        resultados.append({
            'Trinca': f"{g1} + {g2} + {g3}",
            'Grupos': [g1, g2, g3],
            'Score': score,
            'Senas (6)': senas,
            'Quinas (5)': quinas,
            'Quadras (4)': quadras,
            'Qtd Dezenas Únicas': len(pool_unificado),
            'Dezenas_Selecionadas': sorted(list(pool_unificado))
        })
        
    df_trincas = pd.DataFrame(resultados).sort_values(
        by=['Senas (6)', 'Quinas (5)', 'Quadras (4)', 'Score'], 
        ascending=False
    )
    return df_trincas.head(top_n)

def gerar_conferencia_acertos_grupos(sorteios, grupos_dict):
    if not sorteios:
        return pd.DataFrame()

    resultados = []

    for nome, dezenas in grupos_dict.items():
        set_g = set(dezenas)
        senas = 0
        quinas = 0
        quadras = 0
        
        atraso_atual = {'4': 0, '5': 0, '6': 0}
        maior_atraso = {'4': 0, '5': 0, '6': 0}
        soma_atrasos = {'4': 0, '5': 0, '6': 0}
        contagem_atrasos = {'4': 0, '5': 0, '6': 0}
        
        atraso_temp = {'4': 0, '5': 0, '6': 0}
        
        for s in sorteios:
            acertos = len(set_g.intersection(set(s)))
            
            if acertos >= 4:
                quadras += 1
                if acertos >= 5: quinas += 1
                if acertos == 6: senas += 1
                
                for nivel in ['4', '5', '6']:
                    if acertos >= int(nivel):
                        if atraso_temp[nivel] > maior_atraso[nivel]:
                            maior_atraso[nivel] = atraso_temp[nivel]
                        soma_atrasos[nivel] += atraso_temp[nivel]
                        contagem_atrasos[nivel] += 1
                        atraso_temp[nivel] = 0
                    else:
                        atraso_temp[nivel] += 1
            else:
                for nivel in ['4', '5', '6']:
                    atraso_temp[nivel] += 1
                    
        atraso_atual['4'] = atraso_temp['4']
        atraso_atual['5'] = atraso_temp['5']
        atraso_atual['6'] = atraso_temp['6']
        
        media_4 = round(soma_atrasos['4'] / contagem_atrasos['4'], 1) if contagem_atrasos['4'] > 0 else 0
        media_5 = round(soma_atrasos['5'] / contagem_atrasos['5'], 1) if contagem_atrasos['5'] > 0 else 0
        media_6 = round(soma_atrasos['6'] / contagem_atrasos['6'], 1) if contagem_atrasos['6'] > 0 else 0

        pontos = (senas * 100) + (quinas * 50) + (quadras * 10)

        resultados.append({
            "Grupo": nome,
            "Pontos": pontos,
            "Senas (6)": senas,
            "Quinas (5)": quinas,
            "Quadras (4)": quadras,
            "Atraso (4)": atraso_atual['4'],
            "Atraso (5)": atraso_atual['5'],
            "Atraso (6)": atraso_atual['6'],
            "Maior Atraso (4)": maior_atraso['4'],
            "Maior Atraso (5)": maior_atraso['5'],
            "Maior Atraso (6)": maior_atraso['6'],
            "Média (4)": media_4,
            "Média (5)": media_5,
            "Média (6)": media_6
        })

    df = pd.DataFrame(resultados)
    return df.sort_values(by="Pontos", ascending=False).reset_index(drop=True)


# -----------------------------------------------------------------------------
# SEÇÃO DA BARRA LATERAL (MODO ONLINE/OFFLINE E MATRIZES)
# -----------------------------------------------------------------------------
st.sidebar.header("📁 Base Histórica")

modo_operacao = st.sidebar.radio(
    "Modo de Operação:",
    ["🌐 Conectado Online", "📂 Modo Offline (Planilha Excel)"],
    index=0
)

df_historico = None

if modo_operacao == "🌐 Conectado Online":
    df_historico = carregar_dados()
    if df_historico is not None and not df_historico.empty:
        st.sidebar.success("🌐 Conectado online (`asloterias`)")
    else:
        st.sidebar.warning("Não foi possível carregar online. Tente o modo offline.")
else:
    uploaded_file = st.sidebar.file_uploader("Upload manual da planilha", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            df_historico = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
            st.sidebar.success("Base carregada via Upload!")
        except Exception as e:
            st.sidebar.error(f"Erro no upload: {e}")
    else:
            st.sidebar.info("Carregue uma planilha Excel ou CSV para iniciar no modo offline.")

sorteios_historico_completos_bruto = extrair_sorteios_historicos(df_historico) if df_historico is not None and not df_historico.empty else []

if df_historico is not None and not df_historico.empty and sorteios_historico_completos_bruto:
    lista_concursos_disponiveis = []
    for idx_c, _ in enumerate(sorteios_historico_completos_bruto):
        conc_num = df_historico.iloc[idx_c].get('concurso', idx_c + 1)
        data_conc = df_historico.iloc[idx_c].get('data', '')
        label_c = f"Concurso #{conc_num}" + (f" ({data_conc})" if data_conc else "")
        lista_concursos_disponiveis.append((conc_num, idx_c, label_c))
    
    labels_opcoes = [item[2] for item in lista_concursos_disponiveis]
    escolha_concurso_str = st.sidebar.selectbox(
        "🎯 Definir Concurso de Referência (Corte):",
        options=labels_opcoes,
        index=len(labels_opcoes) - 1
    )
    
    indice_selecionado = next(item[1] for item in lista_concursos_disponiveis if item[2] == escolha_concurso_str)
    sorteios_historico_completos = sorteios_historico_completos_bruto[:indice_selecionado + 1]
    
    ultimo_registro = df_historico.iloc[indice_selecionado]
    conc_num = ultimo_registro.get('concurso', 'N/A')
    data_conc = ultimo_registro.get('data', '')
    data_str = f" ({data_conc})" if data_conc else ""
    
    cols_dezenas = [c for c in df_historico.columns if any(t in str(c).lower() for t in ['bola', 'dezena', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6']) and 'data' not in str(c).lower()][:6]
    
    if len(cols_dezenas) == 6:
        dezenas_ultimo = [f"{int(ultimo_registro[c]):02d}" for c in cols_dezenas]
        dezenas_texto = " - ".join(dezenas_ultimo)
        st.sidebar.info(
            f"📌 **Concurso Referência:** #{conc_num}{data_str}\n\n"
            f"🎯 **Dezenas:** `{dezenas_texto}`"
        )
    else:
        st.sidebar.info(f"📌 **Concurso Referência:** #{conc_num}{data_str}")
else:
    sorteios_historico_completos = []

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

# MOMENTUM INTELIGENTE CALCULADO AQUI
momentum_scores = calcular_momentum_inteligente(sorteios_historico, janela_recente=30)

# FILTROS ESTRUTURAIS
st.sidebar.header("⚙️ Filtros Estruturais")
min_soma, max_soma = st.sidebar.slider("Soma Central", 100, 300, (160, 210))
pares_aceitos = st.sidebar.multiselect("Pares Aceitos", [0, 1, 2, 3, 4, 5, 6], default=[2, 3, 4])
moldura_aceita = st.sidebar.multiselect("Moldura Aceita", [0, 1, 2, 3, 4, 5, 6], default=[3, 4])
max_seq = st.sidebar.slider("Máximo Consecutivos", 1, 4, 2)
min_quad = st.sidebar.slider("Mínimo Quadrantes", 1, 4, 3)
max_repetidas = st.sidebar.slider("Máximo Repetidas", 0, 4, 2)

st.sidebar.header("🛡️ Diversificação de Jogos")
ativar_diversificacao = st.sidebar.checkbox("Ativar Diversificação Matemática", value=True)
st.sidebar.caption("Evita que os jogos gerados sejam clones entre si (baixa sobreposição).")

qtd_exportar = st.sidebar.number_input("Qtd de Jogos Gerados", min_value=10, max_value=1000, value=50, step=10)

# -----------------------------------------------------------------------------
# ABAS DO SISTEMA
# -----------------------------------------------------------------------------
tab_gerador, tab_metricas, tab_trincas, tab_conferencia = st.tabs([
    "🚀 Gerador & Recalibragem", 
    f"📊 Métricas dos Grupos ({opcao_matriz})", 
    "🔥 Top Trincas Dinâmicas",
    "📋 Conferência de Acertos dos Grupos"
])

with tab_gerador:
    # Correção 10: Subheader dinâmico
    st.subheader(f"1. Estratégia de Seleção das Dezenas Base ({opcao_matriz})")
    
    opcao_estrategia = st.radio(
        "Selecione o Método de Escolha das Dezenas Base:",
        [
            f"Top Grupos (Compatibilidade com Dezenas Quentes)",
            f"Top Trinca Dinâmica (Ranking nos Últimos {len(sorteios_historico)} Concursos)",
            "🧠 Seleção Inteligente via Auditoria (Ciclos e Atrasos)",
            "Seleção Manual de Dezenas"
        ]
    )
    
    pool_40 = []
    
    # Correção 1: Top Grupos agora usa Compatibilidade
    if opcao_estrategia.startswith("Top Grupos"):
        # Pega as top 24 dezenas (ou quantidade equivalente) com maior momentum
        top_momento = sorted(momentum_scores.keys(), key=lambda d: momentum_scores[d], reverse=True)[:24]
        
        df_comp = ranquear_grupos_por_compatibilidade(top_momento, GRUPOS_ATIVOS, 6)
        
        st.markdown("**Top Grupos por Compatibilidade com as Dezenas Quentes:**")
        st.dataframe(df_comp.head(5), use_container_width=True)
        
        grupo_escolhido = df_comp.iloc[0]['Grupo']
        st.success(f"**Grupo Selecionado Automaticamente:** {grupo_escolhido} (maior cobertura)")
        
        # O pool agora tem EXATAMENTE as dezenas do grupo (40 dezenas), e não a união de 3 grupos
        pool_40 = sorted(GRUPOS_ATIVOS[grupo_escolhido])
        
    elif opcao_estrategia.startswith("Top Trinca"):
        df_top_trincas = ranquear_top_trincas_dinamicas(sorteios_historico, GRUPOS_ATIVOS, top_n=5)
        if not df_top_trincas.empty:
            st.markdown(f"**Top 5 Melhores Trincas (União Top 40) dos Últimos {len(sorteios_historico)} Concursos:**")
            st.dataframe(df_top_trincas.drop(columns=['Dezenas_Selecionadas']), use_container_width=True)
            
            trinca_escolhida = st.selectbox("Escolha uma das Top Trincas:", df_top_trincas['Trinca'].tolist())
            row_trinca = df_top_trincas[df_top_trincas['Trinca'] == trinca_escolhida].iloc[0]
            pool_40 = row_trinca['Dezenas_Selecionadas']
        else:
            st.warning("Carregue o histórico para calcular a Top Trinca.")
            grupo_padrao = list(GRUPOS_ATIVOS.keys())[0]
            pool_40 = GRUPOS_ATIVOS[grupo_padrao]

    elif opcao_estrategia.startswith("🧠 Seleção Inteligente"):
        st.info("💡 O sistema buscará os grupos com o maior **Atraso de Sena (6)** em relação à sua **Média Histórica**, indicando os grupos que estão 'devendo' um acerto.")
        
        df_auditoria = gerar_conferencia_acertos_grupos(sorteios_historico, GRUPOS_ATIVOS)
        
        grupos_devendo = df_auditoria[df_auditoria['Atraso (6)'] > df_auditoria['Média (6)']]
        
        if grupos_devendo.empty:
            grupos_devendo = df_auditoria.sort_values(by='Atraso (6)', ascending=False)
            
        top_3_devendo = grupos_devendo.head(3)['Grupo'].tolist()
        
        st.success(f"**Grupos Selecionados via Ciclos (Maior Atraso de Sena):** {', '.join(top_3_devendo)}")
        
        st.dataframe(
            df_auditoria[df_auditoria['Grupo'].isin(top_3_devendo)][
                ['Grupo', 'Senas (6)', 'Atraso (6)', 'Maior Atraso (6)', 'Média (6)']
            ], 
            use_container_width=True, hide_index=True
        )
        
        pool_40 = sorted(list(set(GRUPOS_ATIVOS[top_3_devendo[0]] + GRUPOS_ATIVOS[top_3_devendo[1]] + GRUPOS_ATIVOS[top_3_devendo[2]])))
            
    else:
        grupo_padrao = list(GRUPOS_ATIVOS.keys())[0]
        pool_40 = st.multiselect("Selecione as dezenas base:", options=list(range(1, 61)), default=GRUPOS_ATIVOS[grupo_padrao])

    st.markdown("---")
    st.subheader("2. Purificação Multicritério (Base ➔ 24 Dezenas) + Momentum")
    
    if len(pool_40) >= 24:
        # PURIFICAÇÃO BALANCEADA
        dezenas_24 = purificar_com_momentum(pool_40, momentum_scores, n_desejado=24)
        
        st.info(f"**Dezenas Purificadas pelo Momentum (24):** {dezenas_24}")
        
        with st.expander("🔎 Ver Score de Momentum das 24 Dezenas Selecionadas"):
            df_mom = pd.DataFrame([
                {"Dezena": d, "Score Momentum": round(momentum_scores[d], 2), "Quadrante": get_quadrante(d)} 
                for d in dezenas_24
            ]).sort_values(by="Score Momentum", ascending=False)
            st.dataframe(df_mom, use_container_width=True, hide_index=True)
        
        if st.button("⚡ Executar Filtros Gaussiano & Gerar Apostas Diversificadas", type="primary"):
            comb_totais = list(combinations(dezenas_24, 6))
            aprovados = []
            
            for comb in comb_totais:
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
                
            st.success(f"**Combinações Que Passaram nos Filtros:** {len(aprovados):,}")
            
            if aprovados:
                if ativar_diversificacao:
                    jogos_finais = aplicar_diversificacao(aprovados, limite_max=qtd_exportar)
                    st.info(f"🛡️ **Diversificação Aplicada:** Reduzido para os melhores {len(jogos_finais)} jogos evitando clones.")
                else:
                    st.info("🏆 Aplicando Ranqueamento Estatístico para escolher os melhores jogos...")
                    
                    top_momentum_dezenas = sorted(dezenas_24, key=lambda d: momentum_scores[d], reverse=True)[:8]
                    
                    def calcular_peso_jogo(jogo):
                        peso = 0
                        peso += len(set(jogo).intersection(set(ultimo_sorteio))) * 50
                        for d in jogo:
                            if d in top_momentum_dezenas:
                                peso += 20
                        meio_soma = (min_soma + max_soma) / 2
                        peso += max(0, 30 - abs(sum(jogo) - meio_soma))
                        return peso

                    aprovados.sort(key=calcular_peso_jogo, reverse=True)
                    jogos_finais = aprovados[:qtd_exportar]
                
                jogos_exibicao = [sorted(list(j)) for j in jogos_finais]
                
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

    # CONFERÊNCIA HISTÓRICA DOS JOGOS GERADOS
    if 'jogos_gerados_atuais' in st.session_state and st.session_state['jogos_gerados_atuais']:
        st.markdown("---")
        st.subheader("🔍 Conferência Histórica dos Jogos Gerados")
        
        if st.button("🔎 Verificar Premiações no Histórico Completo"):
            premiacoes_encontradas = []
            
            for idx_jogo, jogo in enumerate(st.session_state['jogos_gerados_atuais'], start=1):
                set_jogo = set(jogo)
                
                for idx_conc, sorteio in enumerate(sorteios_historico_completos):
                    set_sorteio = set(sorteio)
                    acertos = len(set_jogo.intersection(set_sorteio))
                    
                    if acertos >= 4:
                        conc_num = df_historico.iloc[idx_conc].get('concurso', idx_conc + 1) if df_historico is not None else idx_conc + 1
                        
                        if acertos == 6:
                            tipo = "Sena (6 acertos)"
                        elif acertos == 5:
                            tipo = "Quina (5 acertos)"
                        else:
                            tipo = "Quadra (4 acertos)"
                            
                        premiacoes_encontradas.append({
                            "Jogo Gerado Nº": idx_jogo,
                            "Dezenas do Jogo": ", ".join(f"{d:02d}" for d in sorted(jogo)),
                            "Tipo de Prêmio": tipo,
                            "Concurso": conc_num,
                            "Dezenas Sorteadas": ", ".join(f"{d:02d}" for d in sorted(sorteio))
                        })

            if premiacoes_encontradas:
                df_premios = pd.DataFrame(premiacoes_encontradas)
                df_premios.index = df_premios.index + 1
                st.success(f"🎉 Foram encontradas **{len(premiacoes_encontradas)}** ocorrências de premiações históricas para os jogos gerados!")
                st.dataframe(df_premios, use_container_width=True)
            else:
                st.info("ℹ️ Nenhum dos jogos gerados nesta rodada obteve 4, 5 ou 6 acertos no histórico consultado.")

with tab_metricas:
    st.subheader(f"📊 Desempenho e Cobertura — {opcao_matriz}")
    if sorteios_historico:
        df_metricas = analisar_metricas_completas_grupos(sorteios_historico, GRUPOS_ATIVOS)
        st.dataframe(df_metricas, use_container_width=True)
    else:
        st.info("Nenhum dado histórico carregado para exibir métricas.")

with tab_trincas:
    st.subheader("🔥 Top Trincas Dinâmicas de Grupos")
    if sorteios_historico:
        df_trincas_tab = ranquear_top_trincas_dinamicas(sorteios_historico, GRUPOS_ATIVOS, top_n=15)
        if not df_trincas_tab.empty:
            st.dataframe(df_trincas_tab.drop(columns=['Dezenas_Selecionadas']), use_container_width=True)
        else:
            st.info("Sem dados suficientes.")
    else:
        st.info("Nenhum dado histórico carregado para analisar trincas.")

with tab_conferencia:
    st.subheader(f"📋 Auditoria de Acertos — {opcao_matriz}")
    st.info("Esta tabela simula o desempenho de cada grupo em todos os concursos carregados no período de análise selecionado.")
    
    if sorteios_historico:
        df_conferencia = gerar_conferencia_acertos_grupos(sorteios_historico, GRUPOS_ATIVOS)
        
        st.dataframe(
            df_conferencia, 
            use_container_width=True,
            column_config={
                "Pontos": st.column_config.NumberColumn(format="%d 🏆"),
                "Média (6)": st.column_config.NumberColumn(format="%.1f"),
                "Média (5)": st.column_config.NumberColumn(format="%.1f"),
                "Média (4)": st.column_config.NumberColumn(format="%.1f")
            }
        )
        
        buffer_conf = io.BytesIO()
        with pd.ExcelWriter(buffer_conf, engine='openpyxl') as writer:
            df_conferencia.to_excel(writer, index=False, sheet_name='Auditoria_Grupos')
        st.download_button(
            label="📥 Baixar Auditoria Completa (.xlsx)",
            data=buffer_conf.getvalue(),
            file_name="auditoria_grupos_mega_sena.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_auditoria"
        )
    else:
        st.warning("Carregue o histórico de concursos na barra lateral para gerar a auditoria.")
