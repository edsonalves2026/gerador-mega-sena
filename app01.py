# EXIBIÇÃO DETALHADA DO ÚLTIMO CONCURSO E SUAS DEZENAS NA BARRA LATERAL
if df_historico is not None and not df_historico.empty:
    ultimo_registro = df_historico.iloc[-1]
    conc_num = ultimo_registro.get('concurso', 'N/A')
    data_conc = ultimo_registro.get('data', '')
    data_str = f" ({data_conc})" if data_conc else ""
    
    # Captura dinâmica das 6 dezenas do último sorteio
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
