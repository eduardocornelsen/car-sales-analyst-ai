<div align='center'>
    
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white) ![Plotly](https://img.shields.io/badge/Plotly-272D32?style=for-the-badge&logo=plotly&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-111111?style=for-the-badge&logo=langchain&logoColor=white) ![Gemini](https://img.shields.io/badge/Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white) ![Render](https://img.shields.io/badge/Render-009966?style=for-the-badge&logo=render&logoColor=white)

# 🚗 Analista Automotivo IA
## Dashboard Interativo e Agente de Execução de Código (Tool Calling Agent)

Este projeto de bootcamp fornece uma análise avançada de dados de vendas de carros, combinando visualizações de ponta com uma ferramenta de **Inteligência Artificial** capaz de **executar código Python** (Pandas) sob demanda para análises estatísticas em tempo real.

![car-sales-cover](https://github.com/user-attachments/assets/1197e0f4-3d48-4cac-bb2f-101d5bfcc0fe)


<a href="https://car-sales-analyst-ai.onrender.com" style="text-decoration: none;">
  <img src="https://img.shields.io/badge/Teste%20o%20App%20ao%20Vivo%20-E37400?style=for-the-badge&logo=rocket&logoColor=FFFFFF" 
    alt="View Live App" 
    style="border: none; height: 35px; margin-top:20px; margin-bottom: 35px;">
</a>

*(Nota: Se o aplicativo demorar um pouco para carregar, é porque ele está hospedado em um serviço de nível gratuito e está despertando da inatividade.)*

</div>

---

## 📋 Resumo do Projeto

Este projeto cumpre os requisitos do Sprint 5 de Engenharia de Software, focando na criação de um aplicativo web interativo (`app.py`) e seu deploy na nuvem (`Render`). O objetivo principal é demonstrar competência em:
1. **Engenharia de Dados:** Limpeza de dados (`pandas`), criação de features (`manufacturer`).
2. **Desenvolvimento Web:** Uso do framework `Streamlit` para criar um dashboard multi-página.
3. **Análise Avançada:** Criação de visualizações complexas (`plotly-express`) como Box Plots, Mapas de Calor e Regressão de Depreciação.
4. **Integração de IA:** Implementação de um **Tool Calling Agent** (o padrão moderno do LangChain) para execução de código Python em resposta a comandos de texto do usuário.

---

## 🚀 Funcionalidades de Destaque

| Seção | Funcionalidade | Tecnologias | Impacto |
| :--- | :--- | :--- | :--- |
| **Consultor de Dados (IA)** | **Tool Calling Agent (Gemini)** | `LangChain`, `Gemini API`, `st.chat_input` | Permite que o usuário faça perguntas complexas (ex: "Qual a média de cilindros para carros a diesel?") e a IA **escreve e executa o código Pandas** para obter a resposta exata. |
| **EDA Avançada** | **9 Visualizações Interativas** | `Plotly Express`, `Streamlit` | Inclui gráficos de **Depreciação com Regressão (OLS)**, **Box Plots de Outliers** e **Mapas de Calor de Densidade**, demonstrando análise de 3+ variáveis. |
| **Navegação** | **Sidebar Interativa** | `st.sidebar.radio` | Navegação limpa e responsiva entre as seções do dashboard. |

---

## 🛠️ Abordagem Técnica

O projeto foi refatorado para utilizar o padrão mais moderno e estável de Agentes, após resolver complexos problemas de conflito de dependências.

### Arquitetura do Agente
* **Modelo:** Google Gemini (via `ChatGoogleGenerativeAI`).
* **Tool:** Função Python customizada (`PythonCodeExecutor`) exposta ao Gemini via `@tool`.
* **Motor:** `AgentExecutor` e `create_agent` (o novo padrão do LangChain v1.x) gerenciam o raciocínio e o loop de execução do código.

### Estrutura de Arquivos
### 📂 Estrutura Final do Projeto

```bash
.
├── app.py                     # Código principal do Streamlit (versão final)
├── vehicles_us.csv            # Dataset de vendas
├── requirements.txt           # Dependências Python (LangChain, Streamlit, Pandas, Plotly)
├── runtime.txt                # Define a versão do Python no Render (padrão antigo)
├── .python-version            # 🎯 Define a versão do Python (Padrão moderno/alternativo)
├── .gitignore                 # Arquivo que lista segredos e arquivos a serem ignorados (CRUCIAL!)
├── README.md                  # Documentação do projeto
├── LICENSE                    # Licença de código aberto (importante para portfólio)
├── .streamlit/                # Pasta de configuração do Streamlit
│   └── config.toml            # Configuração do servidor Render
├── prompts/                   # Pasta de instruções para a IA
│   └── system.txt             # Instruções de alto nível (System Prompt)
└── notebooks/                 # Pasta para o Notebook de Análise
    └── EDA.ipynb              # Notebook Jupyter com a Análise Exploratória de Dados
```
---

## 💻 Instalação Local e Setup

### 1. Clonar o Repositório
```bash
git clone https://github.com/eduardocornelsen/car-sales-analyst-ai.git
cd car-sales-analyst-ai
```

### 2. Criar e Ativar um Ambiente Virtual (Recomendado)
```bash
# Cria um ambiente com a versão Python correta
conda create --name car-sales-agent python=3.11 
conda activate car-sales-agent
```

### 3. Instalar Dependências
```bash
# Instala todos os pacotes (incluindo o stack LangChain)
pip install -r requirements.txt
```

### 4. Configurar a Chave API
```bash
# .streamlit/secrets.toml
GOOGLE_API_KEY = "SUA_CHAVE_API_AQUI"
```

### 5. Executar o App Streamlit
```bash
streamlit run app.py
```

---
<p align="center"> Copyright © 2025, Eduardo Cornelsen </p>
