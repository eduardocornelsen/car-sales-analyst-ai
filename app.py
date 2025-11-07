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
        df = pd.read_csv('vehicles_us.csv')
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
    # --- Aba 1: Projeto do Bootcamp (Obrigatório) ---
    # --------------------------------------------------------
    with tab1:
        st.header("Análise Exploratória com Plotly Express")
        st.markdown("Esta aba cumpre todos os requisitos do Sprint 5.")
        
        st.divider()
        st.subheader("1. Histograma de Quilometragem")
        if st.button('Construir Histograma', key='hist_btn'):
            fig_hist = px.histogram(car_data, x="odometer", title="Distribuição de Quilometragem")
            st.plotly_chart(fig_hist, use_container_width=True)

        st.divider()
        st.subheader("2. Gráfico de Dispersão: Preço vs. Quilometragem")
        if st.button('Construir Gráfico de Dispersão', key='scatter_btn'):
            fig_scatter = px.scatter(car_data, x="odometer", y="price", title="Preço vs. Quilometragem")
            st.plotly_chart(fig_scatter, use_container_width=True)

    # --------------------------------------------------------
    # --- Aba 2: Bônus - Chat com IA (Agent Executor) ---
    # --------------------------------------------------------
    with tab2:
        st.header("Consultor de Dados Veiculares 🧠")
        st.markdown("Analise qualquer métrica: a IA executa código Python (usando 'df').")

        if not IA_DISPONIVEL:
            st.warning("As bibliotecas do LangChain não foram instaladas corretamente. A Aba de IA está desativada.")
            st.info("Execute a reinstalação estruturada no terminal.")

        elif "GOOGLE_API_KEY" not in st.secrets:
            st.warning("Chave da API do Google não encontrada.")
            st.write("Por favor, adicione sua `GOOGLE_API_KEY` ao arquivo `.streamlit/secrets.toml`.")
        else:
            try:
                # Configure LLM
                model = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash", 
                    google_api_key=st.secrets["GOOGLE_API_KEY"],
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

                # Display messages from history
                for message in st.session_state.chat_messages_executor:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                # Initialize chat history
                if "chat_messages_executor" not in st.session_state:
                    st.session_state.chat_messages_executor = []

                # Initialize button prompt
                if 'button_prompt' not in st.session_state:
                    st.session_state.button_prompt = None

                # Function to handle button prompts
                def set_button_prompt(prompt):
                    st.session_state.button_prompt = prompt

                # Display messages from history
                for message in st.session_state.chat_messages_executor:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                # Pre-defined question buttons
                st.markdown("**💡 Perguntas Sugeridas:**")
                col1, col2, col3 = st.columns(3)

                # LINHA 1: PERGUNTAS SIMPLES
                with col1:
                    if st.button("📊 Preço médio por fabricante", key='btn_simple_1', use_container_width=True):
                        set_button_prompt("Qual o preço médio por fabricante ('manufacturer')?")

                with col2:
                    if st.button("🚗 Top 5 Carros Mais Caros", key='btn_simple_2', use_container_width=True):
                        set_button_prompt("Quais são os 5 carros mais caros? Liste o modelo, ano e preço.")

                with col3:
                    if st.button("📈 Média de Quilometragem por Condição", key='btn_simple_3', use_container_width=True):
                        set_button_prompt("Qual a quilometragem média ('odometer') por condição ('condition') dos veículos?")

                # LINHA 2: PERGUNTAS COMPLEXAS
                col4, col5, col6 = st.columns(3)

                with col4:
                    if st.button("📈 Rank de Fabricantes por Preço", key='btn_complex_1', use_container_width=True):
                        set_button_prompt("Calcule o preço médio por fabricante ('manufacturer') e ordene do mais caro para o mais barato.")

                with col5:
                    if st.button("📉 Análise de Depreciação", key='btn_complex_2', use_container_width=True):
                        set_button_prompt("Qual a média do preço dividido pela idade (ano atual - 'model_year') para veículos em 'excelente' condição?")
                    
                with col6:
                    if st.button("🚗 4x4 Mais Caros (Top 10)", key='btn_complex_3', use_container_width=True):
                        set_button_prompt("Quais são os 10 carros mais caros com tração 4x4 ('is_4wd' = True)? Liste o preço e o modelo.")

                st.divider()

                # Get user input from button or chat
                user_input = st.session_state.button_prompt or st.chat_input("Ex: Qual o preço médio por fabricante?")

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