# 🚀 Cripto Tracker Pro

Um dashboard interativo construído com Streamlit para visualizar e analisar dados de criptomoedas em tempo real, utilizando a API da CoinGecko.

## 📜 Descrição

O Cripto Tracker Pro oferece uma visão geral do mercado de criptomoedas, permitindo aos usuários:
* Visualizar as principais criptomoedas por capitalização de mercado.
* Analisar detalhes específicos de cada moeda, incluindo seu preço histórico.
* Personalizar a visualização escolhendo a moeda de cotação (USD ou BRL) e o período para análise gráfica.

Este projeto demonstra o uso de Python com bibliotecas populares para criação de dashboards web interativos e consumo de APIs externas.

## ✨ Funcionalidades Principais

* **Visão Geral do Mercado:** Exibe uma tabela com as principais criptomoedas, incluindo Rank, Nome, Preço, Variações de Preço (1h, 24h, 7d) e Capitalização de Mercado.
* **Dados da API CoinGecko:** Busca dados atualizados diretamente da API pública da CoinGecko.
* **Seleção de Moeda de Cotação:** Permite ao usuário alternar a exibição de valores entre Dólar Americano (USD) e Real Brasileiro (BRL), com formatação de moeda apropriada.
* **Controle de Quantidade:** Slider para definir quantas das principais criptomoedas serão exibidas na tabela principal.
* **Análise Detalhada por Moeda:**
    * Seleção de uma criptomoeda específica a partir de uma lista.
    * Exibição do logo da moeda selecionada.
    * Apresentação de métricas chave: Preço Atual, Variação 24h, Capitalização de Mercado, Volume Total (24h), e Máxima/Mínima das últimas 24 horas.
    * Gráfico interativo do histórico de preços para períodos selecionáveis (7, 30, 90 ou 365 dias).
* **Cache de Dados Inteligente:** Utiliza o cache do Streamlit (`@st.cache_data`) para minimizar chamadas à API, respeitando limites de taxa e melhorando a performance. Exibe timestamps de quando os dados foram efetivamente buscados da API.
* **Tema Personalizável:** Suporta customização de tema visual através do arquivo `.streamlit/config.toml`.
* **Tabela Estilizada:** A tabela principal possui formatação condicional de cores para variações de preço e alinhamento de texto otimizado.

## 🛠️ Tecnologias Utilizadas

* **Python 3.x**
* **Streamlit:** Para a construção da interface web interativa.
* **Requests:** Para realizar chamadas à API CoinGecko.
* **Pandas:** Para manipulação e estruturação dos dados.
* **Plotly Express:** Para a criação dos gráficos interativos.
* **API da CoinGecko:** Como fonte principal dos dados de criptomoedas.

## ⚙️ Configuração e Instalação Local

Siga os passos abaixo para executar o Cripto Tracker Pro em sua máquina local:

1.  **Pré-requisitos:**
    * Python 3.7 ou superior instalado.
    * Pip (gerenciador de pacotes do Python).
    * Git instalado (para clonar o repositório).

2.  **Clone o Repositório (se estiver no GitHub):**
    ```bash
    git clone [https://github.com/](https://github.com/)[SEU_USUARIO_NO_GITHUB]/[NOME_DO_SEU_REPOSITORIO].git
    cd [NOME_DO_SEU_REPOSITORIO]
    ```
    Se você tem os arquivos localmente, pule este passo.

3.  **Crie um Ambiente Virtual (Recomendado):**
    ```bash
    python -m venv venv
    # No Windows
    venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

4.  **Instale as Dependências:**
    Certifique-se de que você tem um arquivo `requirements.txt` na raiz do projeto com o seguinte conteúdo (ou similar):
    ```txt
    streamlit
    requests
    pandas
    plotly-express
    ```
    Então, instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure o Logo (Opcional):**
    O dashboard tenta carregar um logo da pasta `assets/imagens/astronauta.png`.
    * Crie uma pasta `assets` na raiz do projeto.
    * Dentro de `assets`, crie uma pasta `imagens`.
    * Coloque seu arquivo de logo (ex: `astronauta.png`) dentro de `assets/imagens/`.
    * Se preferir, altere o caminho no arquivo `crypto_dashboard.py` ou remova a seção do logo.

6.  **Configure o Tema (Opcional):**
    Para usar um tema personalizado:
    * Crie uma pasta chamada `.streamlit` na raiz do projeto.
    * Dentro dela, crie um arquivo `config.toml`.
    * Adicione suas configurações de tema. Exemplo:
        ```toml
        [theme]
        primaryColor="#00C08B"
        backgroundColor="#0F172A"
        secondaryBackgroundColor="#1E293B"
        textColor="#E2E8F0"
        font="sans serif"
        ```

## ▶️ Como Executar

Após a configuração e instalação das dependências:

1.  Abra o terminal ou prompt de comando.
2.  Navegue até a pasta raiz do seu projeto.
3.  Execute o comando:
    ```bash
    streamlit run crypto_dashboard.py
    ```
4.  Seu navegador padrão deve abrir automaticamente com o dashboard. Caso contrário, o terminal mostrará um endereço local (geralmente `http://localhost:8501`) para acesso.

## 🚀 Possíveis Melhorias Futuras

* Gráficos de Candlestick para análise de preço mais detalhada.
* Adição de indicadores técnicos (Médias Móveis, RSI, etc.).
* Funcionalidade para "favoritar" moedas.
* Comparação lado a lado de múltiplas criptomoedas.
* Notificações de alteração de preço (avançado).

## 📝 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes (Opcional: adicione um arquivo LICENSE ao seu projeto se desejar).

---