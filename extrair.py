import streamlit as st
import pandas as pd
from banco import criar_tabela, carregar_dados, salvar_pagamento, atualizar_status_pago, remover_pagamento
from email_utils import enviar_email_novo_pagamento  # Importando a função de envio de e-mail

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

            # Envia o e-mail de confirmação sempre que um pagamento for adicionado
            enviar_email_novo_pagamento(novo_ano, nova_categoria, novo_mes, novo_valor, pago_flag)

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
            col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

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
                st.markdown(f"✅ {'Sim' if row['pago'] else 'Não'}")

            with col3:
                confirm_key = f"confirm_remove_{row['id']}"
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False

                if not st.session_state[confirm_key]:
                    if st.button("Remover", key=f"remove_{row['id']}"):
                        st.session_state[confirm_key] = True
                else:
                    st.warning("Tem certeza que deseja remover?")
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("✅ Confirmar", key=f"confirm_{row['id']}"):
                            remover_pagamento(row['id'])
                            st.success("Pagamento removido.")
                            st.rerun()
                    with col_cancel:
                        if st.button("❌ Cancelar", key=f"cancel_{row['id']}"):
                            st.session_state[confirm_key] = False

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
