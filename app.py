import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np # Necessário para pd.isna e np.nan

# --- Carregar dados ---
@st.cache_data
def carregar_dados():
    """
    Carrega os dados para a aplicação a partir de um arquivo CSV.
    Certifique-se de que o arquivo 'dados_carnaval_2025.csv' esteja na mesma pasta do 'app.py'.
    """
    with st.spinner('Carregando dados... Por favor, aguarde.'):
        try:
            df = pd.read_csv("dados_carnaval_2025.csv", low_memory=False)

            # Convertendo colunas de data para o tipo datetime
            df['dt_checkin'] = pd.to_datetime(df['dt_checkin'], errors='coerce')
            df['dt_checkout'] = pd.to_datetime(df['dt_checkout'], errors='coerce')

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

# --- Sidebar para Filtros ---
st.sidebar.header("Filtros de Análise")

# Função auxiliar para garantir valores min/max válidos para sliders
def get_min_max_slider_values(series, default_min=0.0, default_max=1000.0, step=1.0):
    series_cleaned = series.dropna()
    if series_cleaned.empty:
        return default_min, default_max, (default_min, default_max)
    
    min_val = float(series_cleaned.min())
    max_val = float(series_cleaned.max())
    
    # Ajustar para garantir que max_val não seja igual a min_val se houver apenas um valor único
    if min_val == max_val:
        max_val += step # Garante que o slider tenha uma faixa, mesmo com um único valor
    
    return min_val, max_val, (min_val, max_val)

# 1. Filtro por Tipo de Serviço
selected_tipo_servico = st.sidebar.multiselect(
    "Tipo de Serviço:",
    options=df['tipo_servico'].unique().tolist(),
    default=df['tipo_servico'].unique().tolist()
)

# 2. Filtro por Status de Conversão (Serviço)
selected_status_conv_servico = st.sidebar.multiselect(
    "Status de Conversão do Serviço:",
    options=df['status_conversao_servico'].unique().tolist(),
    default=df['status_conversao_servico'].unique().tolist()
)

# 3. Filtro por Resposta do Herói
selected_teve_resposta = st.sidebar.multiselect(
    "Teve Resposta do Herói:",
    options=df['teve_resposta_formatado'].unique().tolist(),
    default=df['teve_resposta_formatado'].unique().tolist()
)

# 4. Filtro por Faixa de Tempo de Resposta (horas)
min_tr, max_tr, default_tr_range = get_min_max_slider_values(df['tempo_de_resposta_horas'], default_max=df['tempo_de_resposta_horas'].max() if pd.notna(df['tempo_de_resposta_horas'].max()) else 1000.0, step=0.1)
tempo_resposta_range = st.sidebar.slider(
    "Tempo de Resposta (horas):",
    min_value=min_tr,
    max_value=max_tr,
    value=default_tr_range,
    step=0.1
)

# 5. Filtro por Valor Inicial do Serviço
min_vi, max_vi, default_vi_range = get_min_max_slider_values(df['valor_inicial'], default_max=df['valor_inicial'].max() if pd.notna(df['valor_inicial'].max()) else 10000.0, step=10.0)
valor_inicial_range = st.sidebar.slider(
    "Valor Inicial do Serviço:",
    min_value=min_vi,
    max_value=max_vi,
    value=default_vi_range,
    step=10.0
)

# 6. Filtro por Status de Conversão (Cliente)
selected_status_conv_cliente = st.sidebar.multiselect(
    "Status de Conversão do Cliente:",
    options=df['status_conversao_cliente'].unique().tolist(),
    default=df['status_conversao_cliente'].unique().tolist()
)

# 7. Filtro por Quantidade de Heróis Contatados
min_qhc, max_qhc, default_qhc_range = get_min_max_slider_values(df['quantidade_herois_contatados'], default_max=df['quantidade_herois_contatados'].max() if pd.notna(df['quantidade_herois_contatados'].max()) else 10.0, step=1.0)
herois_contatados_range = st.sidebar.slider(
    "Nº de Heróis Contatados:",
    min_value=int(min_qhc), # Sliders de int precisam de int
    max_value=int(max_qhc),
    value=(int(default_qhc_range[0]), int(default_qhc_range[1])),
    step=1
)


# --- Aplicar Filtros ---
df_filtered = df.copy()

# Filtros de seleção múltipla
if selected_tipo_servico:
    df_filtered = df_filtered[df_filtered['tipo_servico'].isin(selected_tipo_servico)]
if selected_status_conv_servico:
    df_filtered = df_filtered[df_filtered['status_conversao_servico'].isin(selected_status_conv_servico)]
if selected_teve_resposta:
    df_filtered = df_filtered[df_filtered['teve_resposta_formatado'].isin(selected_teve_resposta)]
if selected_status_conv_cliente:
    df_filtered = df_filtered[df_filtered['status_conversao_cliente'].isin(selected_status_conv_cliente)]

# Filtros de range (sliders)
df_filtered = df_filtered[
    (df_filtered['tempo_de_resposta_horas'] >= tempo_resposta_range[0]) &
    (df_filtered['tempo_de_resposta_horas'] <= tempo_resposta_range[1])
]
df_filtered = df_filtered[
    (df_filtered['valor_inicial'] >= valor_inicial_range[0]) &
    (df_filtered['valor_inicial'] <= valor_inicial_range[1])
]
df_filtered = df_filtered[
    (df_filtered['quantidade_herois_contatados'] >= herois_contatados_range[0]) &
    (df_filtered['quantidade_herois_contatados'] <= herois_contatados_range[1])
]


# --- Verifica se o DataFrame filtrado está vazio ---
if df_filtered.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados. Por favor, ajuste os filtros na barra lateral.")
else:
    st.header("Visão Geral da Conversão")

    # KPI da taxa de conversão a nível de cliente
    total_clientes_filtered = df_filtered['id_cliente'].nunique()
    clientes_convertidos_filtered = df_filtered[df_filtered['status_conversao_cliente'] == 'Converteu uma das necessidades']['id_cliente'].nunique()
    taxa_conversao_clientes_filtered = (clientes_convertidos_filtered / total_clientes_filtered) * 100 if total_clientes_filtered > 0 else 0

    st.metric(label="Taxa de Conversão de Clientes (com filtros)", value=f"{taxa_conversao_clientes_filtered:.2f}%")
    st.write(f"Total de clientes com serviços no Carnaval (com filtros): {total_clientes_filtered}")
    st.write(f"Clientes que converteram pelo menos uma necessidade (com filtros): {clientes_convertidos_filtered}")

    st.markdown("---")

    # Gráfico de barras da conversão por tipo de serviço
    st.subheader("Conversão por Tipo de Serviço (Serviço Individual)")
    if not df_filtered.empty and 'tipo_servico' in df_filtered.columns and 'status_conversao_servico' in df_filtered.columns:
        df_conversao_tipo = df_filtered.groupby('tipo_servico')['status_conversao_servico'].value_counts(normalize=True).unstack().fillna(0)
        
        # Garante que ambas as colunas 'Convertido' e 'Não Convertido' existam
        expected_cols = ['Convertido', 'Não Convertido']
        for col in expected_cols:
            if col not in df_conversao_tipo.columns:
                df_conversao_tipo[col] = 0.0 # Adiciona a coluna com zeros se estiver faltando

        if not df_conversao_tipo.empty:
            fig_conv_tipo = px.bar(df_conversao_tipo,
                                x=df_conversao_tipo.index,
                                y=['Convertido', 'Não Convertido'],
                                title='Proporção de Conversão por Tipo de Serviço',
                                labels={'value':'Proporção', 'variable':'Status'},
                                barmode='group')
            st.plotly_chart(fig_conv_tipo)
            st.markdown("""
            **Insight:** Este gráfico mostra como a taxa de conversão varia entre diferentes tipos de serviço (ex: 'boarding', 'day_care').
            Observe se há tipos de serviço com uma proporção significativamente maior de 'Não Convertido',
            o que pode indicar um problema específico nesse segmento durante o Carnaval.
            """)
        else:
            st.warning("Dados insuficientes para plotar a Conversão por Tipo de Serviço com os filtros aplicados.")
    else:
        st.warning("Dados insuficientes para plotar a Conversão por Tipo de Serviço com os filtros aplicados.")


    # Distribuição do tempo de resposta para serviços convertidos vs. não convertidos
    st.subheader("Distribuição do Tempo de Resposta (Horas)")
    if not df_filtered.empty and 'tempo_de_resposta_horas' in df_filtered.columns and not df_filtered['tempo_de_resposta_horas'].dropna().empty:
        fig_tempo_resposta = px.histogram(df_filtered, x="tempo_de_resposta_horas", color="status_conversao_servico",
                                          marginal="box",
                                          nbins=min(50, int(df_filtered['tempo_de_resposta_horas'].max() / (tempo_resposta_range[1] - tempo_resposta_range[0]) * 50) + 1 if tempo_resposta_range[1] - tempo_resposta_range[0] > 0 else 50), # Ajusta nbins dinamicamente
                                          title="Tempo de Resposta em Horas por Status de Conversão",
                                          labels={"tempo_de_resposta_horas": "Tempo de Resposta (horas)"})
        st.plotly_chart(fig_tempo_resposta)
        st.markdown("""
        **Insight:** Este histograma revela a frequência de diferentes tempos de resposta e a proporção de conversão em cada faixa.
        Observe a concentração de serviços com tempo de resposta muito curto (próximo de zero). Se muitos não convertem nessa faixa,
        o problema pode não ser a velocidade, mas outros fatores na interação. Tempos de resposta muito longos são quase sempre associados à não conversão.
        """)
    else:
        st.warning("Dados insuficientes para plotar a Distribuição do Tempo de Resposta com os filtros aplicados.")


    # Distribuição da quantidade de heróis contatados
    st.subheader("Número de Heróis Contatados por Cliente vs. Conversão")
    df_clientes_unicos_filtered = df_filtered[['id_cliente', 'quantidade_herois_contatados', 'status_conversao_cliente']].drop_duplicates()

    if not df_clientes_unicos_filtered.empty and 'quantidade_herois_contatados' in df_clientes_unicos_filtered.columns:
        max_herois = df_clientes_unicos_filtered['quantidade_herois_contatados'].max()
        if pd.isna(max_herois):
            nbins_val = 5
        else:
            nbins_val = max(int(max_herois), 5)

        fig_herois_contatados = px.histogram(df_clientes_unicos_filtered, x="quantidade_herois_contatados", color="status_conversao_cliente",
                                              nbins=nbins_val,
                                              title="Número de Heróis Contatados por Clientes",
                                              labels={"quantidade_herois_contatados": "Nº de Heróis Contatados"})
        st.plotly_chart(fig_herois_contatados)
        st.markdown("""
        **Insight:** Este gráfico mostra quantos Heróis um cliente contatou e se ele converteu uma necessidade.
        É útil para identificar se clientes que conversam com muitos Heróis (alta 'quantidade_herois_contatados')
        têm mais ou menos chances de converter. Isso pode sinalizar indecisão do cliente ou falta de opções adequadas.
        """)
    else:
        st.warning("Dados de 'quantidade_herois_contatados' não disponíveis ou inválidos para plotar o histograma com os filtros aplicados.")


    st.subheader("Dados Brutos (Amostra com Filtros Aplicados)")
    st.dataframe(df_filtered.head(10)) # Mostra as primeiras 10 linhas do DataFrame filtrado
