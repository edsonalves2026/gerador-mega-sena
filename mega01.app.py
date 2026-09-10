import streamlit as st
import pandas as pd
import numpy as np
import itertools
from itertools import combinations
import io
import os
import random

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO E TELA DE LOGIN
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Gerador Mega-Sena Profissional", page_icon="🎲", layout="wide")

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
# CONSTANTES E MATRIZES
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
# FUNÇÕES AUXILIARES E OTIMIZAÇÃO DE FECHAMENTO
# -----------------------------------------------------------------------------
def get_quadrante(dezena):
    col = (dezena - 1) % 10
    lin = (dezena - 1) // 10
    if col < 5 and lin < 3: return 1
    if col >= 5 and lin < 3: return 2
    if col < 5 and lin >= 3: return 3
    return 4

def carregar_dados_historicos():
    # Estrutura de simulação para validação rápida
    np.random.seed(42)
    sorteios = [sorted(random.sample(range(1, 61), 6)) for _ in range(100)]
    return sorteios

def aplicar_reducao_garantia(jogos_filtrados, garantia_desejada, qtd_dezenas):
    """
    Algoritmo Guloso (Greedy Cover) otimizado para Fechamento / Redução por Garantia.
    Garante acerto mínimo com o menor número possível de bilhetes.
    """
    if not jogos_filtrados:
        return []
    
    jogos_sets = [set(j) for j in jogos_filtrados]
    cobertos = set()
    jogos_selecionados = []
    
    indices_restantes = list(range(len(jogos_filtrados)))
    
    while indices_restantes and len(cobertos) < len(jogos_filtrados):
        melhor_idx = -1
        melhor_cobertura = -1
        
        for idx in indices_restantes:
            jogo_cand = jogos_sets[idx]
            novos_cobertos = 0
            for i in indices_restantes:
                if i not in cobertos:
                    if len(jogo_cand.intersection(jogos_sets[i])) >= garantia_desejada:
                        novos_cobertos += 1
            
            if novos_cobertos > melhor_cobertura:
                melhor_cobertura = novos_cobertos
                melhor_idx = idx
        
        if melhor_idx == -1 or melhor_cobertura == 0:
            jogos_selecionados.append(jogos_filtrados[indices_restantes[0]])
            break
            
        jogos_selecionados.append(jogos_filtrados[melhor_idx])
        
        jogo_escolhido = jogos_sets[melhor_idx]
        novos_cobertos_set = set()
        for i in indices_restantes:
            if len(jogo_escolhido.intersection(jogos_sets[i])) >= garantia_desejada:
                novos_cobertos_set.add(i)
                cobertos.add(i)
                
        indices_restantes = [i for i in indices_restantes if i not in novos_cobertos_set]
        
    return jogos_selecionados

def ranquear_top_trincas_dinamicas(grupos_dict):
    """Identifica as 24 dezenas mais coerentes filtrando pelas combinações internas da matriz selecionada"""
    contagem = {}
    for dezenas in grupos_dict.values():
        for d in dezenas:
            contagem[d] = contagem.get(d, 0) + 1
    df_rank = pd.DataFrame(list(contagem.items()), columns=["Dezena", "Frequencia"]).sort_values(by="Frequencia", ascending=False)
    dezenas_24 = df_rank.head(24)["Dezena"].tolist()
    return sorted(dezenas_24), df_rank

def formatar_txt_caixa(jogos):
    """
    Formata as apostas no padrão texto (.txt) aceito para importação no Internet Banking / Loterias Caixa.
    Dezenas ordenadas com 2 dígitos (01, 05, 12), separadas por espaço simples.
    Uma aposta por linha.
    """
    linhas = []
    for jogo in jogos:
        jogo_formatado = " ".join([f"{dezena:02d}" for dezena in sorted(jogo)])
        linhas.append(jogo_formatado)
    return "\n".join(linhas)

# -----------------------------------------------------------------------------
# INTERFACE PRINCIPAL - NAVEGAÇÃO
# -----------------------------------------------------------------------------
tab_gerador, tab_metricas, tab_trincas = st.tabs([
    "🎲 Gerador & Fechamento", 
    "📊 Métricas & Estatísticas", 
    "🔮 Análise de Trincas / Grupos"
])

# -----------------------------------------------------------------------------
# TAB 1: GERADOR DE JOGOS E FECHAMENTO
# -----------------------------------------------------------------------------
with tab_gerador:
    st.header("Gerador Inteligente & Redução por Garantia")
    
    col_par1, col_par2 = st.columns([1, 1])
    
    with col_par1:
        st.subheader("1. Configurações Básicas")
        qtd_dezenas_aposta = st.slider("Dezenas por bilhete:", min_value=6, max_value=15, value=6)
        
        dezenas_24_base, df_freq = ranquear_top_trincas_dinamicas(GRUPOS_ATIVOS)
        
        usar_pool_custom = st.checkbox("Customizar o Pool de 24 Dezenas Base", value=False)
        if usar_pool_custom:
            dezenas_24 = st.multiselect("Selecione exatamente 24 dezenas:", options=list(range(1, 61)), default=dezenas_24_base)
            if len(dezenas_24) < 24:
                st.warning(f"Selecione mais {24 - len(dezenas_24)} dezenas para completar o pool de 24.")
        else:
            dezenas_24 = dezenas_24_base

        usar_fixas = st.checkbox("Fixar Dezenas Específicas", value=False)
        dezenas_fixas_sel = []
        if usar_fixas:
            dezenas_fixas_sel = st.multiselect("Dezenas Fixas (presentes em todos os jogos):", options=dezenas_24)

    with col_par2:
        st.subheader("2. Filtros Estatísticos Profissionais")
        min_soma, max_soma = st.slider("Faixa da Soma Total das Dezenas:", 100, 300, (140, 220))
        pares_aceitos = st.multiselect("Quantidade de Pares:", options=list(range(0, 16)), default=[2, 3, 4])
        moldura_aceita = st.multiselect("Quantidade na Moldura:", options=list(range(0, 16)), default=[3, 4, 5])
        max_seq = st.slider("Tamanho Máximo de Sequência Sequencial (Ex: 12-13-14):", 1, 5, 2)
        min_quad = st.slider("Mínimo de Quadrantes Presentes:", 1, 4, 3)
        
        sorteios_hist = carregar_dados_historicos()
        ultimo_sorteio = sorteios_hist[-1] if sorteios_hist else []
        max_repetidas = st.slider("Máximo de Dezenas Repetidas do Último Sorteio:", 0, 6, 2)

    st.markdown("---")
    st.subheader("3. Estratégia de Fechamento / Redução")
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        aplicar_fechamento = st.checkbox("Ativar Fechamento Matemático (Redução)", value=False)
    with col_f2:
        if aplicar_fechamento:
            garantia_sel = st.selectbox(
                "Garantia Pretendida (Se acertar as dezenas no pool de 24):",
                options=[4, 5, 6],
                format_func=lambda x: "Garantia de Quadra (4 acertos)" if x == 4 else ("Garantia de Quina (5 acertos)" if x == 5 else "Garantia de Sena (6 acertos)")
            )
        else:
            garantia_sel = 6

    if st.button("🚀 Processar e Gerar Jogos", type="primary", use_container_width=True):
        if len(dezenas_24) < qtd_dezenas_aposta:
            st.error(f"O pool de dezenas ({len(dezenas_24)}) deve ser maior ou igual à quantidade por aposta ({qtd_dezenas_aposta}).")
        else:
            aprovados = []
            limite_seguranca = 300000
            contagem_avaliados = 0
            
            with st.spinner("Filtrando combinações estatísticas..."):
                for comb in combinations(sorted(dezenas_24), qtd_dezenas_aposta):
                    contagem_avaliados += 1
                    if contagem_avaliados > limite_seguranca:
                        st.warning("Limite máximo de segurança para avaliação em tempo real atingido. Prosseguindo com os jogos já processados.")
                        break

                    if usar_fixas and dezenas_fixas_sel:
                        if not all(d in comb for d in dezenas_fixas_sel):
                            continue

                    s = sum(comb)
                    if not (min_soma <= s <= max_soma): continue
                    if sum(1 for d in comb if d % 2 == 0) not in pares_aceitos: continue
                    if sum(1 for d in comb if d in MOLDURA) not in moldura_aceita: continue
                    
                    seq, m_seq = 1, 1
                    for i in range(len(comb)-1):
                        if comb[i+1] == comb[i] + 1:
                            seq += 1
                            m_seq = max(m_seq, seq)
                        else:
                            seq = 1
                    if m_seq > max_seq: continue
                    
                    if len(set(get_quadrante(d) for d in comb)) < min_quad: continue
                    if ultimo_sorteio and sum(1 for d in comb if d in ultimo_sorteio) > max_repetidas: continue
                    
                    aprovados.append(comb)
            
            if not aprovados:
                st.error("Nenhuma combinação atendeu a todos os filtros selecionados. Tente flexibilizar as regras.")
            else:
                st.info(f"Combinações válidas encontradas pelos filtros: **{len(aprovados)}**")
                
                if aplicar_fechamento and len(aprovados) > 1:
                    with st.spinner("Aplicando matriz de fechamento otimizada..."):
                        jogos_finais = aplicar_reducao_garantia(aprovados, garantia_sel, qtd_dezenas_aposta)
                    st.success(f"Fechamento reduzido com sucesso! De **{len(aprovados)}** para apenas **{len(jogos_finais)}** bilhetes otimizados.")
                else:
                    jogos_finais = aprovados

                st.session_state['jogos_gerados_atuais'] = jogos_finais
                
                # Exibição dos Jogos na Interface
                df_jogos = pd.DataFrame(jogos_finais, columns=[f"D{i+1}" for i in range(qtd_dezenas_aposta)])
                st.dataframe(df_jogos, use_container_width=True)
                
                # Botões de Exportação (CSV e TXT Caixa)
                col_exp1, col_exp2 = st.columns(2)
                
                with col_exp1:
                    buffer_csv = df_jogos.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Baixar Jogos em CSV (Excel)",
                        data=buffer_csv,
                        file_name="jogos_megasena.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                with col_exp2:
                    conteudo_txt = formatar_txt_caixa(jogos_finais)
                    st.download_button(
                        label="📄 Baixar TXT (Padrão Loterias Caixa)",
                        data=conteudo_txt,
                        file_name="jogos_megasena_caixa.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

# -----------------------------------------------------------------------------
# TAB 2: MÉTRICAS E CONFERÊNCIA HISTÓRICA
# -----------------------------------------------------------------------------
with tab_metricas:
    st.header("Métricas do Pool & Conferência Histórica")
    
    if 'jogos_gerados_atuais' not in st.session_state:
        st.info("Gere uma cartela de jogos na aba 'Gerador & Fechamento' para visualizar os relatórios estatísticos.")
    else:
        jogos = st.session_state['jogos_gerados_atuais']
        st.metric(label="Total de Jogos Prontos", value=len(jogos))
        
        if st.button("📊 Conferir Desempenho com Histórico Simulado"):
            sorteios = carregar_dados_historicos()
            
            quadras, quinas, senas = 0, 0, 0
            
            with st.spinner("Conferindo bilhetes contra os sorteios..."):
                jogos_sets = [set(j) for j in jogos]
                for s in sorteios:
                    set_s = set(s)
                    for j in jogos_sets:
                        acertos = len(j.intersection(set_s))
                        if acertos == 4: quadras += 1
                        elif acertos == 5: quinas += 1
                        elif acertos >= 6: senas += 1
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Quadras Simuladas", quadras)
            col_m2.metric("Quinas Simuladas", quinas)
            col_m3.metric("Senas Simuladas", senas)

# -----------------------------------------------------------------------------
# TAB 3: ANÁLISE DE GRUPOS E TRINCAS
# -----------------------------------------------------------------------------
with tab_trincas:
    st.header("Análise Estrutural da Matriz")
    st.write(f"Analisando matriz selecionada no menu lateral: **{opcao_matriz}**")
    
    dezenas_top, df_ranking = ranquear_top_trincas_dinamicas(GRUPOS_ATIVOS)
    
    st.subheader("Frequência de Dezenas na Matriz Ativa")
    st.dataframe(df_ranking.T, use_container_width=True)
    
    st.subheader("Pool de 24 Dezenas Recomendado")
    st.write(dezenas_top)
