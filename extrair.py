import streamlit as st
import pandas as pd
from banco import criar_tabela, carregar_dados, salvar_pagamento, atualizar_status_pago, remover_pagamento

criar_tabela()

st.set_page_config(layout="wide")
st.title("📋 Checklist de Pagamentos")

df_pagamentos = carregar_dados()

# Adicionar novo pagamento
with st.expander("➕ Adicionar novo pagamento"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        novo_ano = st.number_input("Ano", min_value=2020, max_value=2100, value=2025)
    with col2:
        nova_categoria = st.text_input("Categoria")
    with col3:
        novo_mes = st.selectbox("Mês", ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"])
    with col4:
        novo_valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)

    pago_flag = st.checkbox("Já está pago?", value=False)

    if st.button("Adicionar"):
        if nova_categoria and novo_mes:
            salvar_pagamento(novo_ano, nova_categoria, novo_mes, novo_valor, pago_flag)
            st.success("Pagamento adicionado com sucesso!")
            st.rerun()
        else:
            st.warning("Preencha todos os campos.")

# Interface de visualização
anos = sorted(df_pagamentos["ano"].unique()) if not df_pagamentos.empty else []
ano_selecionado = st.selectbox("Selecione o ano:", anos, key="ano_select") if anos else None

if ano_selecionado:
    df_ano = df_pagamentos[df_pagamentos["ano"] == ano_selecionado]
    for categoria in sorted(df_ano["categoria"].unique()):
        st.subheader(f"📌 {categoria}")
        df_categoria = df_ano[df_ano["categoria"] == categoria]
        for _, row in df_categoria.iterrows():
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                pago = st.checkbox(
                    f"{row['mes']} - R$ {row['valor']:.2f}",
                    value=bool(row['pago']),
                    key=f"chk_{row['id']}"
                )
                if pago != bool(row['pago']):
                    atualizar_status_pago(row['id'], pago)
                    st.rerun()
          with col2:
    if st.button("❌", key=f"remover_{row['id']}"):
        st.session_state['confirmar_exclusao'] = row['id']

# Modal de confirmação
if 'confirmar_exclusao' in st.session_state:
    with st.modal("Confirmar exclusão"):
        st.write("Tem certeza que deseja excluir este pagamento?")
        col_confirmar, col_cancelar = st.columns(2)
        with col_confirmar:
            if st.button("Sim, excluir"):
                remover_pagamento(st.session_state['confirmar_exclusao'])
                del st.session_state['confirmar_exclusao']
                st.rerun()
        with col_cancelar:
            if st.button("Cancelar"):
                del st.session_state['confirmar_exclusao']

import altair as alt

st.markdown("---")
st.subheader("📊 Tabela de Pagamentos")
st.dataframe(df_pagamentos.drop(columns=["id"]), use_container_width=True)

st.markdown("---")
st.subheader("📈 Gráfico de Pagamentos por Categoria")

if not df_pagamentos.empty:
    df_resumo = (
        df_pagamentos.groupby("categoria")["valor"]
        .sum()
        .reset_index()
        .sort_values("valor", ascending=False)
    )

    barras = alt.Chart(df_resumo).mark_bar().encode(
        x=alt.X("valor:Q", title="Valor Total (R$)"),
        y=alt.Y("categoria:N", sort='-x', title="Categoria"),
        tooltip=["categoria", "valor"]
    )

    texto = alt.Chart(df_resumo).mark_text(
        align='left',
        baseline='middle',
        dx=3  # deslocamento do texto em relação à barra
    ).encode(
        x='valor:Q',
        y=alt.Y('categoria:N', sort='-x'),
        text=alt.Text('valor:Q', format=".2f")  # formatar com duas casas decimais
    )

    grafico = (barras + texto).properties(width=700, height=400)

    st.altair_chart(grafico, use_container_width=True)
else:
    st.info("Nenhum dado disponível para gerar gráfico.")
