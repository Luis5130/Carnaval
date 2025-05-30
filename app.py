import streamlit as st
import pandas as pd
import plotly.express as px # Import plotly.express para gráficos mais simples
import plotly.graph_objects as go # Para gráficos mais customizados
import numpy as np

# --- Carregar dados ---
@st.cache_data
def carregar_dados():
    """
    Carrega os dados para a aplicação a partir de um arquivo CSV.
    Certifique-se de que o arquivo 'dados_carnaval_2025.csv' esteja na mesma pasta do 'app.py'.
    """
    try:
        # Substitua "dados_carnaval_2025.csv" pelo nome exato do seu arquivo CSV
        df = pd.read_csv("dados_carnaval_2025.csv")

        # As colunas já virão formatadas da query, mas se precisar de ajustes, faça aqui:
        # Exemplo: converter tempo_de_resposta_horas para string formatada para exibição
        # df['tempo_de_resposta_horas_formatado'] = df['tempo_de_resposta_horas'].apply(lambda x: f"{x:.2f} horas" if pd.notnull(x) else None)

        # Se houver colunas de data/hora que precisarão ser tratadas como datetime no Python
        # df['dt_checkin'] = pd.to_datetime(df['dt_checkin'])
        # df['dt_checkout'] = pd.to_datetime(df['dt_checkout'])

        return df
    except FileNotFoundError:
        st.error("Arquivo 'dados_carnaval_2025.csv' não encontrado. Por favor, certifique-se de que o arquivo está na mesma pasta do 'app.py'.")
        st.stop()
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o CSV: {e}")
        st.stop()

# Carrega os dados uma vez
df = carregar_dados()

st.title("Carnaval 2025: Análise de Conversão e Respostas")

# --- Comece a construir seu dashboard com os novos dados ---

st.header("Visão Geral da Conversão")

# Exemplo: KPI da taxa de conversão a nível de cliente
total_clientes = df['id_cliente'].nunique()
clientes_convertidos = df[df['status_conversao_cliente'] == 'Converteu uma das necessidades']['id_cliente'].nunique()
taxa_conversao_clientes = (clientes_convertidos / total_clientes) * 100 if total_clientes > 0 else 0

st.metric(label="Taxa de Conversão de Clientes", value=f"{taxa_conversao_clientes:.2f}%")
st.write(f"Total de clientes com serviços no Carnaval: {total_clientes}")
st.write(f"Clientes que converteram pelo menos uma necessidade: {clientes_convertidos}")

# Exemplo: Gráfico de barras da conversão por tipo de serviço
st.subheader("Conversão por Tipo de Serviço (Serviço Individual)")
df_conversao_tipo = df.groupby('tipo_servico')['status_conversao_servico'].value_counts(normalize=True).unstack().fillna(0)
st.dataframe(df_conversao_tipo)

fig_conv_tipo = px.bar(df_conversao_tipo,
                       x=df_conversao_tipo.index,
                       y=['Convertido', 'Não Convertido'],
                       title='Proporção de Conversão por Tipo de Serviço',
                       labels={'value':'Proporção', 'variable':'Status'},
                       barmode='group')
st.plotly_chart(fig_conv_tipo)


# Exemplo: Distribuição do tempo de resposta para serviços convertidos vs. não convertidos
st.subheader("Distribuição do Tempo de Resposta (Horas)")
fig_tempo_resposta = px.histogram(df, x="tempo_de_resposta_horas", color="status_conversao_servico",
                                  marginal="box", # shows boxplot on top
                                  nbins=50, # adjust number of bins as needed
                                  title="Tempo de Resposta em Horas por Status de Conversão",
                                  labels={"tempo_de_resposta_horas": "Tempo de Resposta (horas)"})
st.plotly_chart(fig_tempo_resposta)


# Exemplo: Distribuição da quantidade de heróis contatados
st.subheader("Número de Heróis Contatados por Cliente vs. Conversão")
# Criar um dataframe de clientes únicos para este gráfico
df_clientes_unicos = df[['id_cliente', 'quantidade_herois_contatados', 'status_conversao_cliente']].drop_duplicates()
fig_herois_contatados = px.histogram(df_clientes_unicos, x="quantidade_herois_contatados", color="status_conversao_cliente",
                                      nbins=max(df_clientes_unicos['quantidade_herois_contatados'].max(), 5), # dynamic bins
                                      title="Número de Heróis Contatados por Clientes",
                                      labels={"quantidade_herois_contatados": "Nº de Heróis Contatados"})
st.plotly_chart(fig_herois_contatados)


st.subheader("Dados Brutos (Amostra)")
st.dataframe(df.head()) # Mostra as primeiras linhas do DataFrame
