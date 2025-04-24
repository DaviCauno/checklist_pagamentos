import streamlit as st
import pandas as pd
import os
import json

# Caminho do arquivo de dados
DATA_FILE = "pagamentos.json"

# Função para carregar os dados (sem cache)
def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return pd.DataFrame(json.load(f))
    else:
        return pd.DataFrame(columns=["Ano", "Categoria", "Mês", "Valor", "Pago"])

# Função para salvar os dados
def salvar_dados(df):
    with open(DATA_FILE, "w") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2)

# Função para adicionar novo pagamento
def adicionar_pagamento(ano, categoria, mes, valor, pago):
    novo = pd.DataFrame({
        "Ano": [ano],
        "Categoria": [categoria],
        "Mês": [mes],
        "Valor": [valor],
        "Pago": [pago]
    })
    df_atual = carregar_dados()
    df_atual = pd.concat([df_atual, novo], ignore_index=True)
    salvar_dados(df_atual)
    return df_atual

# Interface
st.set_page_config(layout="wide")
st.title("📋 Checklist de Pagamentos")

df_pagamentos = carregar_dados()

# Interface para adicionar novo pagamento
with st.expander("➕ Adicionar novo pagamento"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        novo_ano = st.number_input("Ano", min_value=2020, max_value=2100, value=2025, step=1)
    with col2:
        nova_categoria = st.text_input("Categoria")
    with col3:
        novo_mes = st.selectbox("Mês", ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"])
    with col4:
        novo_valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01, format="%.2f")

    pago_flag = st.checkbox("Já está pago?", value=False)

    if st.button("Adicionar"):
        if nova_categoria and novo_mes:
            df_pagamentos = adicionar_pagamento(novo_ano, nova_categoria, novo_mes, novo_valor, pago_flag)
            st.success("Pagamento adicionado com sucesso!")
        else:
            st.warning("Preencha todos os campos.")

# Atualiza lista de anos incluindo o novo, se necessário
anos = sorted(df_pagamentos["Ano"].unique()) if not df_pagamentos.empty else []
ano_selecionado = st.selectbox("Selecione o ano:", anos, key="ano_select") if anos else None

# Exibe checklist se houver ano selecionado
if ano_selecionado:
    df_ano = df_pagamentos[df_pagamentos["Ano"] == ano_selecionado]
    for categoria in sorted(df_ano["Categoria"].unique()):
        st.subheader(f"📌 {categoria}")
        df_categoria = df_ano[df_ano["Categoria"] == categoria]
        for i, row in df_categoria.iterrows():
            pago = st.checkbox(
                f"{row['Mês']} - R$ {row['Valor']:.2f}",
                value=row['Pago'],
                key=f"{row['Ano']}_{row['Categoria']}_{row['Mês']}_{i}"
            )
            df_pagamentos.loc[row.name, "Pago"] = pago
    salvar_dados(df_pagamentos)

st.caption("💾 Dados salvos automaticamente em pagamentos.json")

# Exibe tabela interativa em vez de JSON
st.markdown("---")
st.subheader("📊 Tabela de Pagamentos")
st.dataframe(df_pagamentos, use_container_width=True)
