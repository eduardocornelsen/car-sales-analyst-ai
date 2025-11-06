import streamlit as st
import pandas as pd
import plotly.express as px

# Tente importar as bibliotecas de IA. Se não funcionarem, a aba de IA apenas avisará o usuário.
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
    IA_DISPONIVEL = True
except ImportError:
    IA_DISPONIVEL = False

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Vendas de Carros",
    page_icon="🚗",
    layout="wide"
)

# --- Carregar os Dados (com cache) ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('vehicles_us.csv')
        # Pequena limpeza para o agente de IA funcionar melhor
        df['model_year'] = df['model_year'].fillna(0).astype(int)
        df['cylinders'] = df['cylinders'].fillna(0).astype(int)
        df['odometer'] = df['odometer'].fillna(df['odometer'].mean())
        return df
    except FileNotFoundError:
        st.error("Erro: O arquivo 'vehicles_us.csv' não foi encontrado no diretório raiz.")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None

car_data = load_data()

# --- Título Principal ---
st.title("🚗 Dashboard de Análise de Vendas de Carros")
st.write("Projeto do Sprint 5 - Combinando os requisitos do bootcamp com um Chatbot de IA.")

if car_data is not None:
    # --- Criar as Abas ---
    tab1, tab2, tab3 = st.tabs([
        "Projeto do Bootcamp (Obrigatório)", 
        "Bônus: Chat com IA (Avançado)",
        "Ver Dados Brutos"
    ])

    # --- Aba 1: Projeto do Bootcamp (Obrigatório) ---
    with tab1:
        st.header("Análise Exploratória com Plotly Express")
        st.markdown("Esta aba cumpre todos os requisitos do Sprint 5.")
        
        st.divider()

        # 1. Histograma (com botão)
        st.subheader("Histograma de Quilometragem (Odometer)")
        hist_button = st.button('Construir histograma')
        if hist_button:
            st.write('Criando um histograma para a coluna "odometer"')
            fig_hist = px.histogram(car_data, x="odometer", title="Distribuição de Quilometragem")
            st.plotly_chart(fig_hist, use_container_width=True)

        st.divider()

        # 2. Gráfico de Dispersão (com botão)
        st.subheader("Gráfico de Dispersão: Preço vs. Quilometragem")
        scatter_button = st.button('Construir gráfico de dispersão')
        if scatter_button:
            st.write('Criando um gráfico de dispersão para "price" vs "odometer"')
            fig_scatter = px.scatter(car_data, x="odometer", y="price", title="Preço vs. Quilometragem")
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        st.divider()
            
        # 3. Desafio Opcional (Checkbox)
        st.subheader("Desafio Opcional: Análise por Condição")
        st.write("Veja a distribuição de quilometragem por condição do veículo.")
        build_hist_condition = st.checkbox('Construir histograma por condição')
        
        if build_hist_condition:
            st.write('Criando um histograma de "odometer" por "condition"')
            fig_hist_cond = px.histogram(car_data, 
                                         x="odometer", 
                                         color="condition", 
                                         title="Histograma de Quilometragem por Condição")
            st.plotly_chart(fig_hist_cond, use_container_width=True)


    # --- Aba 2: Bônus - Chat com IA ---
    with tab2:
        st.header("Auto-Analista (IA)")
        st.write("Faça uma pergunta em linguagem natural sobre os dados.")

        if not IA_DISPONIVEL:
            st.warning("As bibliotecas de IA (langchain, etc.) não estão instaladas. A Aba de IA está desativada.")
            st.code("pip install langchain langchain-google-genai langchain-experimental")
        elif "GOOGLE_API_KEY" not in st.secrets:
            st.warning("Chave da API do Google não encontrada.")
            st.write("Para usar esta aba, por favor, adicione sua `GOOGLE_API_KEY` ao arquivo `.streamlit/secrets.toml`.")
        else:
            # Configurar o LLM
            llm = ChatGoogleGenerativeAI(model="gemini-pro", 
                                         google_api_key=st.secrets["GOOGLE_API_KEY"],
                                         temperature=0,
                                         convert_system_message_to_human=True)
            
            # Criar o Agente
            agent = create_pandas_dataframe_agent(llm, 
                                                  car_data, 
                                                  verbose=True,
                                                  allow_dangerous_code=True)
            
            # Inicializar o histórico do chat
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = []

            # Exibir mensagens
            for message in st.session_state.chat_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Input do usuário
            if prompt := st.chat_input("Qual o preço médio por marca?"):
                st.chat_message("user").markdown(prompt)
                st.session_state.chat_messages.append({"role": "user", "content": prompt})

                try:
                    # Executar o agente
                    with st.spinner("A IA está pensando..."):
                        response = agent.invoke(prompt)
                        ai_response = response['output']
                    
                    st.chat_message("assistant").markdown(ai_response)
                    st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                except Exception as e:
                    st.error(f"Erro ao processar a pergunta: {e}")
                    st.session_state.chat_messages.append({"role": "assistant", "content": f"Desculpe, tive um erro: {e}"})

    # --- Aba 3: Ver Dados Brutos ---
    with tab3:
        st.header("Dados Brutos")
        st.dataframe(car_data)

else:
    st.info("Aguardando o arquivo 'vehicles_us.csv' para iniciar o aplicativo.")