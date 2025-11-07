import streamlit as st
import pandas as pd
import plotly.express as px
import io
import sys
from pathlib import Path
from langchain.tools import tool

# --- Importações do LangChain (Tool Calling Agent) ---
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.agents import create_agent
    from langchain.tools import tool
    from langchain_core.prompts import ChatPromptTemplate
    
    IA_DISPONIVEL = True
except ImportError:
    IA_DISPONIVEL = False
except Exception:
    IA_DISPONIVEL = False

# Read System Prompt from file
system_prompt = Path("./prompts/system.txt").read_text()

# --- Configuração da Página ---
st.set_page_config(
    page_title="Analista Automotivo IA",
    page_icon="🚗",
    layout="wide"
)

# --- Carregar e Limpar os Dados (com cache) ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('vehicles_us.csv', usecols=list(range(13)))
        df.dropna(subset=['price', 'odometer', 'condition', 'model_year', 'model'], inplace=True)
        df['manufacturer'] = df['model'].apply(lambda x: x.split()[0] if isinstance(x, str) else 'Outros')
        return df
    except FileNotFoundError:
        st.error("Erro: O arquivo 'vehicles_us.csv' não foi encontrado no diretório raiz.")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None

car_data = load_data()

st.sidebar.title("Sobre o Projeto 💡")
st.sidebar.markdown(
    """
    Este projeto demonstra análise de dados avançada utilizando **Pandas** e **Inteligência Artificial** (Google Gemini) para executar código Python sob demanda.
    

    **Autor:**
    Eduardo Cornelsen
    
    **Plataforma:**
    Streamlit + Render
    
    ---
    """
)
st.sidebar.info("Acesse a ***Aba 2 (Consultor de Dados)*** para interagir com o **Agente de IA**.")

# --- Título Principal ---
st.title("🚗 Analista Automotivo IA")
st.write("Projeto do Sprint 5 - Dashboard com Tool Calling Agent do LangChain e Gemini Flash 2.5")

# --------------------------------------------------------
# CRIAR A FERRAMENTA CUSTOMIZADA COM IA
# --------------------------------------------------------

@tool
def PythonCodeExecutor(code: str) -> str:
    """
    Execute Python code for data analysis on DataFrame 'df'.
    CRITICAL: You MUST use the actual DataFrame 'df' - do NOT create fake data.
    Always verify results with actual data from df.
    Exemple: print(df['price'].mean())
    """
    try:
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        
        global car_data
        df = car_data.copy()  # Use copy to prevent modifications
        
        # Validate code doesn't create fake data
        if 'pd.DataFrame' in code and '{' in code:
            return "ERROR: Do NOT create fake DataFrames. Use the existing 'df' variable only."

        exec(code, {'df': df, 'pd': pd}, {})
        
        sys.stdout = old_stdout
        output = redirected_output.getvalue()
        
        # Check if output is empty
        if not output.strip():
            return "ERROR: No output generated. Make sure to use print() to display results."
                
        return output
    
    except Exception as e:
        sys.stdout = old_stdout
        return f"Erro: {e}"

tools = [PythonCodeExecutor]


# --- Renderização do App ---

if car_data is not None:

    # --- Criar as Abas ---
    tab1, tab2, tab3 = st.tabs([
        "Projeto do Bootcamp (Obrigatório)", 
        "Bônus: Chat com IA (Agent Executor)",
        "Ver Dados Brutos"
    ])

    # --------------------------------------------------------
    # --- Aba 1: Projeto do Bootcamp (Análise Exploratória Avançada) ---
    # --------------------------------------------------------
    with tab1:
        st.header("Análise Exploratória Avançada com Plotly Express")
        st.markdown("Esta aba contém 9 visualizações interativas para explorar tendências de mercado e depreciação.")
        
        # Cria uma cópia para a manipulação de dados
        df = car_data.copy()
        
        # ---------------------------------------------------
        # REQUISITO 1 (Original): VISUALIZADOR DE DADOS
        # ---------------------------------------------------
        st.divider()
        st.subheader("1. Visualizador de Dados Brutos (com Filtro)")
        
        # Tradução do Checkbox
        include_small_manufacturers = st.checkbox("Incluir fabricantes com menos de 1000 anúncios", value=True)
        
        df_display = df.copy()

        if not include_small_manufacturers:
            manufacturer_counts = df_display['manufacturer'].value_counts()
            large_manufacturers = manufacturer_counts[manufacturer_counts >= 1000].index
            df_display = df_display[df_display['manufacturer'].isin(large_manufacturers)]
            st.info(f"Mostrando apenas {len(large_manufacturers)} fabricantes (com 1000+ anúncios).")
            
        st.dataframe(df_display.head(50))
        st.markdown(f"Total de Registros Exibidos: **{len(df_display)}**")

        # ---------------------------------------------------
        # REQUISITO 2 (Original): TIPOS DE VEÍCULO POR FABRICANTE
        # ---------------------------------------------------
        st.divider()
        st.subheader("2. Tipos de Veículo por Fabricante")
        
        df_type_manufacturer = df.groupby(['manufacturer', 'type']).size().reset_index(name='count')
        
        fig_type_manufacturer = px.bar(
            df_type_manufacturer,
            x="manufacturer",
            y="count",
            color="type",
            title="Distribuição de Tipos de Veículos (Type) por Fabricante"
        )
        st.plotly_chart(fig_type_manufacturer, use_container_width=True)

        # ---------------------------------------------------
        # REQUISITO 3 (Original): HISTOGRAMA DA CONDITION vs MODEL_YEAR
        # ---------------------------------------------------
        st.divider()
        st.subheader("3. Condição (Condition) por Ano do Modelo")
        
        fig_condition_year = px.histogram(
            df,
            x="model_year",
            color="condition",
            title="Histograma de Condição vs. Ano do Modelo",
            barmode="group",
            histfunc='count'
        )
        st.plotly_chart(fig_condition_year, use_container_width=True)
        
        # ---------------------------------------------------
        # REQUISITO 4 (Original): COMPARAÇÃO DA DISTRIBUIÇÃO DE PREÇOS
        # ---------------------------------------------------
        st.divider()
        st.subheader("4. Comparação de Distribuição de Preços")
        
        available_manufacturers = sorted(df['manufacturer'].unique())
        
        # Dropdowns
        manufacturer1 = st.selectbox(
            "Selecione o Fabricante 1:",
            available_manufacturers,
            index=available_manufacturers.index('ford') if 'ford' in available_manufacturers else 0,
            key="manu1"
        )
        
        manufacturer2 = st.selectbox(
            "Selecione o Fabricante 2:",
            available_manufacturers,
            index=available_manufacturers.index('toyota') if 'toyota' in available_manufacturers else (1 if len(available_manufacturers) > 1 else 0),
            key="manu2"
        )
        
        # Checkbox
        normalize_hist = st.checkbox("Normalizar Histograma (Mostrar Proporção)", value=True)
        
        df_comparison = df[
            (df['manufacturer'] == manufacturer1) | (df['manufacturer'] == manufacturer2)
        ]
        
        histnorm_mode = 'probability density' if normalize_hist else None
        
        fig_comparison = px.histogram(
            df_comparison,
            x="price",
            color="manufacturer",
            title=f"Distribuição de Preços: {manufacturer1} vs. {manufacturer2}",
            barmode="overlay",
            opacity=0.75,
            histnorm=histnorm_mode
        )
        
        fig_comparison.update_layout(
            xaxis_title="Preço",
            yaxis_title="Contagem" if not normalize_hist else "Densidade de Probabilidade"
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # ===================================================
        # --- NOVAS VISUALIZAÇÕES (Tier 1 & 2) ---
        # ===================================================

        # ---------------------------------------------------
        # REQUISITO 5 (Tier 1): BOX PLOT de Preço por Condição
        # ---------------------------------------------------
        st.divider()
        st.subheader("5. Distribuição de Preços (Box Plot) por Condição")
        st.write("Visualização para identificar a mediana, quartis e outliers de preços para cada estado de conservação.")

        fig_boxplot = px.box(
            df, 
            x='condition', 
            y='price', 
            color='condition',
            title='Distribuição de Preços por Condição do Veículo (Identificação de Outliers)',
            # Garante que a ordem da condição seja lógica (opcional, mas recomendado)
            category_orders={"condition": ['new', 'excellent', 'good', 'fair', 'salvage', 'other']}
        )
        fig_boxplot.update_layout(xaxis_title="Condição", yaxis_title="Preço")
        st.plotly_chart(fig_boxplot, use_container_width=True)

        # ---------------------------------------------------
        # REQUISITO 6 (Tier 1): SCATTER PLOT (Depreciação)
        # ---------------------------------------------------
        st.divider()
        st.subheader("6. Análise de Depreciação: Preço vs. Quilometragem")
        st.write("Gráfico de dispersão com linha de regressão (OLS) para modelar a depreciação por tipo de veículo.")
        
        # Limita a quilometragem para melhor visualização da tendência (opcional)
        df_scatter = df[df['odometer'] < df['odometer'].quantile(0.99)].copy()
        
        fig_scatter_reg = px.scatter(
            df_scatter,
            x='odometer',
            y='price',
            color='type',
            title='Depreciação vs. Quilometragem por Tipo de Veículo',
            opacity=0.6,
            trendline='ols', # Linha de Regressão de Mínimos Quadrados Ordinários (Ols)
            height=600
        )
        fig_scatter_reg.update_layout(xaxis_title="Quilometragem (Odometer)", yaxis_title="Preço")
        st.plotly_chart(fig_scatter_reg, use_container_width=True)

        # ---------------------------------------------------
        # REQUISITO 7 (Tier 1): MAPA DE CALOR (Densidade)
        # ---------------------------------------------------
        st.divider()
        st.subheader("7. Mapa de Calor: Densidade de Anúncios")
        st.write("Visualiza a combinação de Ano do Modelo e Condição onde a maioria dos anúncios se concentra.")
        
        fig_heatmap_density = px.density_heatmap(
            df,
            x="model_year",
            y="condition",
            title="Densidade de Anúncios por Ano do Modelo e Condição",
            text_auto=True # Exibe o valor da contagem em cada célula
        )
        fig_heatmap_density.update_layout(xaxis_title="Ano do Modelo", yaxis_title="Condição")
        st.plotly_chart(fig_heatmap_density, use_container_width=True)

        # ---------------------------------------------------
        # REQUISITO 8 (Tier 2): DISTRIBUIÇÃO DE TIPOS
        # ---------------------------------------------------
        st.divider()
        st.subheader("8. Distribuição de Frequência de Tipos de Veículo")
        st.write("Contagem simples para ver a composição da frota anunciada.")
        
        df_type_count = df['type'].value_counts().reset_index()
        df_type_count.columns = ['Tipo de Veículo', 'Contagem']
        
        fig_type_dist = px.bar(
            df_type_count,
            x='Tipo de Veículo',
            y='Contagem',
            color='Tipo de Veículo',
            title='Contagem de Anúncios por Tipo de Veículo'
        )
        st.plotly_chart(fig_type_dist, use_container_width=True)

        # ---------------------------------------------------
        # REQUISITO 9 (Tier 2): ANÁLISE DE BARRAS DUPLA (Fuel vs Transmission)
        # ---------------------------------------------------
        st.divider()
        st.subheader("9. Combinação de Transmissão por Tipo de Combustível")
        st.write("Compara a preferência por tipo de transmissão para diferentes combustíveis.")
        
        fig_fuel_trans = px.histogram(
            df,
            x='fuel',
            color='transmission',
            barmode='group',
            title='Distribuição de Transmissão por Tipo de Combustível',
            height=400
        )
        fig_fuel_trans.update_layout(xaxis_title="Tipo de Combustível", yaxis_title="Contagem")
        st.plotly_chart(fig_fuel_trans, use_container_width=True)
        
        st.divider()

    # --------------------------------------------------------
    # --- Aba 2: Bônus - Chat com IA (Agent Executor) ---
    # --------------------------------------------------------
    with tab2:
        st.header("Consultor de Dados Veiculares 🧠")
        st.markdown("Analise qualquer métrica: a IA executa código Python (usando 'df').")

        if not IA_DISPONIVEL:
            st.warning("As bibliotecas do LangChain não foram instaladas corretamente. A Aba de IA está desativada.")
            st.info("Execute a reinstalação estruturada no terminal.")

        # Novo Bloco de Verificação: Apenas verificamos se a chave falha ao ser usada (try/except)
        else:
            try:
                # Check if API key exists (works both locally and on Render)
                import os
                api_key = os.environ.get("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", None)
                
                if api_key is None:
                    st.warning("Chave da API do Google não encontrada.")
                    st.write("Por favor, adicione a variável de ambiente `GOOGLE_API_KEY` no Render.")
                    st.stop()
                
                # Create model (only runs if key exists)
                model = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash", 
                    google_api_key=api_key,
                    temperature=0
                )
                
                # Create Agent
                agent = create_agent(
                    model=model,
                    tools=tools,
                    system_prompt=system_prompt
                )
                
                # Initialize chat history
                if "chat_messages_executor" not in st.session_state:
                    st.session_state.chat_messages_executor = []

                # Initialize button prompt
                if 'button_prompt' not in st.session_state:
                    st.session_state.button_prompt = None

                # NEW: Force stay on this tab when there's activity
                if 'force_tab2' not in st.session_state:
                    st.session_state.force_tab2 = False

                # Function to handle button prompts
                def set_button_prompt(prompt):
                    st.session_state.button_prompt = prompt
                    st.session_state.force_tab2 = True  # Keep user on tab 2

                # Display messages from history
                for message in st.session_state.chat_messages_executor:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                # Get user input from chat box FIRST (at top)
                chat_input = st.chat_input("Ex: Qual o preço médio por fabricante?")

                st.divider()

                # Pre-defined question buttons
                st.subheader("**💡 Perguntas Sugeridas:**")

                # LINHA 1: FABRICANTES
                st.markdown("**1. FABRICANTES**")
                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    if st.button("📊 Preço Médio por Fabricante", key='btn_1a', use_container_width=True):
                        set_button_prompt("Qual o preço médio por fabricante ('manufacturer')?")

                with col2:
                    if st.button("📈 Rank de Preço por Fabricante", key='btn_1b', use_container_width=True):
                        set_button_prompt("Liste os 5 fabricantes com o maior preço médio, mostrando o preço.")

                with col3:
                    if st.button("📦 Rank de Fabricantes por Vendas", key='btn_1c', use_container_width=True):
                        set_button_prompt("Conte o número total de veículos por fabricante e liste os 5 mais vendidos.")

                with col4:
                    if st.button("🔥 Eficiência por Fabricante", key='btn_1d', use_container_width=True):
                        set_button_prompt("Para os 5 fabricantes mais caros, qual é a média de cilindros ('cylinders') e o tipo de transmissão ('transmission') mais comum?")

                with col5:
                    if st.button("⛽️ Popularidade por Tipo de Combustível", key='btn_1e', use_container_width=True):
                        set_button_prompt("Para a Toyota, conte quantos veículos utilizam gasolina e quantos utilizam diesel.")

                # LINHA 2: MODELOS
                st.markdown("**2. MODELOS**")
                col6, col7, col8, col9, col10 = st.columns(5)

                with col6:
                    if st.button("💰 Top 5 Carros Mais Caros", key='btn_2a', use_container_width=True):
                        set_button_prompt("Quais são os 5 carros mais caros? Liste o modelo, ano e preço.")

                with col7:
                    if st.button("📈 Rank de Carros Mais Vendidos", key='btn_2b', use_container_width=True):
                        set_button_prompt("Conte quantos anúncios existem por modelo de carro e liste os 5 modelos mais populares (maior contagem).")

                with col8:
                    if st.button("🚜 4x4 Mais Caros (Top 10)", key='btn_2c', use_container_width=True):
                        set_button_prompt("Quais são os 10 carros mais caros com tração 4x4 ('is_4wd' = True)? Liste o preço e o modelo.")

                with col9:
                    if st.button("🎨 Popularidade da Cor/Tipo", key='btn_2d', use_container_width=True):
                        set_button_prompt("Qual a cor ('paint_color') mais comum entre os veículos do tipo 'SUV'?")

                with col10:
                    if st.button("📉 Rank de Carros Mais Antigos", key='btn_2e', use_container_width=True):
                        set_button_prompt("Quais são os 10 modelos de carros mais antigos ('model_year') no dataset?")

                # LINHA 3: ANÁLISES
                st.markdown("**3. ANÁLISES**")
                col11, col12, col13, col14, col15 = st.columns(5)

                with col11:
                    if st.button("📉 Análise de Depreciação", key='btn_3a', use_container_width=True):
                        set_button_prompt("Qual a taxa média de preço dividido por idade (ano atual - 'model_year') para veículos em 'excelente' condição?")

                with col12:
                    if st.button("🚗 Média de KM por Condição", key='btn_3b', use_container_width=True):
                        set_button_prompt("Qual a quilometragem média ('odometer') por condição ('condition') dos veículos?")

                with col13:
                    if st.button("💎 Melhores Negócios (Baixo Custo/Alto Valor)", key='btn_3c', use_container_width=True):
                        set_button_prompt("Liste os 5 modelos com preço abaixo da média GERAL, mas que estejam em 'excelente' condição.")

                with col14:
                    if st.button("⛽ Eficiência de Combustível/Cilindro", key='btn_3d', use_container_width=True):
                        set_button_prompt("Qual é a média de cilindros ('cylinders') para carros a 'gasolina' e para carros a 'diesel'?")

                with col15:
                    if st.button("💎 Relação Preço/Quilometragem", key='btn_3e', use_container_width=True):
                        set_button_prompt("Calcule a média da relação entre preço e quilometragem ('price' / 'odometer') por tipo de combustível ('fuel').")

                st.divider()

                # Combine button prompt or chat input
                user_input = st.session_state.button_prompt or chat_input

                # Clear button prompt after use
                if st.session_state.button_prompt:
                    st.session_state.button_prompt = None

                # Process input
                if user_input:
                    st.chat_message("user").markdown(user_input)
                    st.session_state.chat_messages_executor.append({"role": "user", "content": user_input})

                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()

                        try:
                            with st.spinner("Processando sua solicitação..."):
                                response = agent.invoke({"messages": st.session_state.chat_messages_executor})

                            # Check for malformed call
                            if response["messages"][-1].response_metadata.get('finish_reason') == 'MALFORMED_FUNCTION_CALL':
                                message_placeholder.empty()
                                st.error("O modelo teve dificuldade em processar sua solicitação. Tente reformular.")
                                st.stop()    

                            # Extract AI response
                            ai_content = response["messages"][-1].content

                            if isinstance(ai_content, list) and len(ai_content) > 0:
                                text_content = ai_content[0].get('text', '')
                            else:
                                text_content = ai_content

                            # DEBUG
                            with st.expander("🔍 Debug: Ver código executado"):
                                st.code(str(response), language="python")

                            # Display text only
                            message_placeholder.markdown(text_content)
                            st.session_state.chat_messages_executor.append({
                                "role": "assistant",
                                "content": text_content
                            })                            

                        except Exception as e:
                            message_placeholder.empty()
                            st.error(f"Erro durante o processamento: {str(e)}")
                            st.write("Detalhes do erro:", e)

            except Exception as e:
                st.error(f"Erro ao inicializar o Agente: {e}")

    # --------------------------------------------------------
    # --- Aba 3: Ver Dados Brutos ---
    # --------------------------------------------------------
    with tab3:
        st.header("Dados Brutos e Colunas")
        st.dataframe(car_data)
        st.subheader("Colunas Disponíveis para Análise:")
        st.write(list(car_data.columns))

else:
    st.info("Aguardando o arquivo 'vehicles_us.csv' para iniciar o aplicativo.")