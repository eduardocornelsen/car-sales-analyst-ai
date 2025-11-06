import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Vendas de Carros",
    page_icon="🚗",
    layout="wide"
)

# --- Carregar os Dados (com cache) ---
# Isso melhora a performance, o Streamlit não recarrega os dados toda vez
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('vehicles_us.csv')
        return df
    except FileNotFoundError:
        st.error("Erro: O arquivo 'vehicles_us.csv' não foi encontrado.")
        st.info("Por favor, certifique-se de que 'vehicles_us.csv' está na mesma pasta que app.py.")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None

car_data = load_data()

# --- Requisito 1: Pelo menos um cabeçalho ---
st.header("Dashboard de Análise de Vendas de Carros 🚗")
st.write("Este dashboard interativo permite explorar o conjunto de dados de vendas de carros.")

# Só continuar se os dados foram carregados com sucesso
if car_data is not None:

    st.divider() # Adiciona uma linha de separação

    # --- Requisito 2: Botão para Histograma ---
    st.subheader("Histograma de Quilometragem (Odometer)")
    
    # Criar o botão
    hist_button = st.button('Construir histograma')
    
    if hist_button: # se o botão for clicdado
        # escrever uma mensagem
        st.write('Criando um histograma para a coluna "odometer"')
        
        # criar um histograma
        fig_hist = px.histogram(car_data, x="odometer", title="Distribuição de Quilometragem")
    
        # exibir um gráfico Plotly interativo
        st.plotly_chart(fig_hist, use_container_width=True)

    st.divider() # Adiciona uma linha de separação

    # --- Requisito 3: Botão para Gráfico de Dispersão ---
    st.subheader("Gráfico de Dispersão: Preço vs. Quilometragem")
    
    # Criar o segundo botão
    scatter_button = st.button('Construir gráfico de dispersão')
    
    if scatter_button: # se o botão for clicado
        # escrever uma mensagem
        st.write('Criando um gráfico de dispersão para "price" vs "odometer"')
        
        # criar o gráfico de dispersão
        fig_scatter = px.scatter(car_data, x="odometer", y="price", title="Preço vs. Quilometragem")
    
        # exibir um gráfico Plotly interativo
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    st.divider() # Adiciona uma linha de separação

    # --- Desafio Opcional: Usando Checkboxes ---
    st.subheader("Desafio Opcional: Gráficos com Checkbox")
    st.write("Marque as caixas abaixo para gerar os gráficos.")

    # Checkbox para o histograma
    build_histogram_check = st.checkbox('Criar um histograma de condição do veículo')
    
    if build_histogram_check: # se a caixa de seleção for selecionada
        st.write('Criando um histograma de "odometer" por "condition"')
        fig_hist_cond = px.histogram(car_data, x="odometer", color="condition", title="Histograma de Quilometragem por Condição")
        st.plotly_chart(fig_hist_cond, use_container_width=True)

    # Checkbox para o gráfico de dispersão
    build_scatter_check = st.checkbox('Criar um gráfico de dispersão de preço por ano do modelo')
    
    if build_scatter_check: # se a caixa de seleção for selecionada
        st.write('Criando um gráfico de dispersão de "price" por "model_year"')
        fig_scatter_year = px.scatter(car_data, x="model_year", y="price", title="Preço por Ano do Modelo")
        st.plotly_chart(fig_scatter_year, use_container_width=True)
        
else:
    st.warning("Não foi possível carregar os dados para exibir os gráficos.")