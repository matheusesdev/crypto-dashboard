import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- Configurações da API e Funções de Busca/Processamento ---

COINGECKO_API_URL_MARKETS = "https://api.coingecko.com/api/v3/coins/markets"
COINGECKO_API_URL_CHART = "https://api.coingecko.com/api/v3/coins/{id}/market_chart"

# Cache para os dados da API
@st.cache_data(ttl=600) # Cache de 10 minutos
def fetch_crypto_markets_data(vs_currency="usd", order="market_cap_desc", per_page=50, page=1):
    params = {
        'vs_currency': vs_currency,
        'order': order,
        'per_page': per_page,
        'page': page,
        'sparkline': 'false',
        'price_change_percentage': '1h,24h,7d'
    }
    try:
        response = requests.get(COINGECKO_API_URL_MARKETS, params=params)
        response.raise_for_status()
        return response.json(), datetime.now() # Retorna dados e timestamp da busca
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar dados de mercado da API CoinGecko: {e}")
        return [], datetime.now()
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado (mercados): {e}")
        return [], datetime.now()

@st.cache_data(ttl=600) # Cache de 10 minutos
def fetch_crypto_chart_data(coin_id, vs_currency="usd", days="30"):
    url = COINGECKO_API_URL_CHART.format(id=coin_id)
    params = {
        'vs_currency': vs_currency,
        'days': days
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        prices_df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        prices_df['timestamp'] = pd.to_datetime(prices_df['timestamp'], unit='ms')
        return prices_df, datetime.now() # Retorna DataFrame e timestamp da busca
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar dados do gráfico para {coin_id}: {e}")
        return pd.DataFrame(), datetime.now()
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado (gráfico {coin_id}): {e}")
        return pd.DataFrame(), datetime.now()

def format_value_brl_style(value_str_dot_decimal):
    if not isinstance(value_str_dot_decimal, str):
        value_str_dot_decimal = str(value_str_dot_decimal)
    return value_str_dot_decimal.replace(',', '#TEMP#').replace('.', ',').replace('#TEMP#', '.')

def style_negative_red(val): # for_delta não é mais necessário como argumento aqui
    if pd.isna(val): return ''
    try:
        numeric_val = float(val)
        color = 'red' if numeric_val < 0 else '#00C08B' if numeric_val > 0 else 'inherit'
        return f'color: {color}; font-weight: bold;'
    except ValueError: return ''

# ESTA É A FUNÇÃO ATUALIZADA PARA CORRIGIR O KEYERROR
def process_markets_data_for_display(crypto_data_list_for_table, vs_currency="usd"):
    if not crypto_data_list_for_table:
        return pd.DataFrame().style 

    # Prepara os dados apenas para as colunas que serão exibidas na tabela principal
    # 'Coin ID' é usado para a lógica do selectbox, mas não entra diretamente aqui.
    processed_data_for_table = []
    for crypto in crypto_data_list_for_table:
        processed_data_for_table.append({
            "Rank": crypto.get('market_cap_rank'), 
            "Nome": f"{crypto.get('name', 'N/A')} ({crypto.get('symbol', 'N/A').upper()})",
            f"Preço ({vs_currency.upper()})": float(crypto.get('current_price', 0)),
            "Variação (1h) %": float(crypto.get('price_change_percentage_1h_in_currency', 0)),
            "Variação (24h) %": float(crypto.get('price_change_percentage_24h_in_currency', 0)),
            "Variação (7d) %": float(crypto.get('price_change_percentage_7d_in_currency', 0)),
            f"Capitalização ({vs_currency.upper()})": float(crypto.get('market_cap', 0))
        })
    
    df_display = pd.DataFrame(processed_data_for_table)

    # --- Preparação para Estilização ---
    format_dict = {} 
    price_col_name = f"Preço ({vs_currency.upper()})"
    market_cap_col_name = f"Capitalização ({vs_currency.upper()})"
    change_1h_col_name = "Variação (1h) %"
    change_24h_col_name = "Variação (24h) %"
    change_7d_col_name = "Variação (7d) %"
    currency_symbol_display = "$" if vs_currency == "usd" else "R$" if vs_currency == "brl" else vs_currency.upper() + " "

    # Tratar coluna 'Rank' - converter para inteiro nullable e preparar formatação
    if "Rank" in df_display.columns:
        df_display["Rank"] = pd.to_numeric(df_display["Rank"], errors='coerce').astype('Int64') # Permite <NA>
        format_dict["Rank"] = lambda x: f"{x}" if pd.notna(x) else "N/A" # Formata como string, ou N/A
    
    # --- Formatadores para Styler ---
    def currency_formatter(val, symbol, is_brl):
        if pd.isna(val): return "N/A"
        formatted_val_str = f"{float(val):,.2f}"
        if is_brl: formatted_val_str = format_value_brl_style(formatted_val_str)
        return f"{symbol}{formatted_val_str}"

    if price_col_name in df_display.columns:
        format_dict[price_col_name] = lambda x: currency_formatter(x, currency_symbol_display, vs_currency == "brl")
    if market_cap_col_name in df_display.columns:
        format_dict[market_cap_col_name] = lambda x: currency_formatter(x, currency_symbol_display, vs_currency == "brl")

    def percentage_formatter(val, is_brl):
        if pd.isna(val): return "N/A"
        formatted_val_str = f"{float(val):.2f}%"
        if is_brl: formatted_val_str = formatted_val_str.replace('.', ',')
        return formatted_val_str

    for col in [change_1h_col_name, change_24h_col_name, change_7d_col_name]:
        if col in df_display.columns:
            format_dict[col] = lambda x, is_brl_val= (vs_currency=="brl"): percentage_formatter(x, is_brl_val)
    
    # --- Inicializar e Aplicar Estilos ---
    styler = df_display.style # 'Rank' é uma coluna aqui, não o índice

    # Aplicar cor às colunas de variação
    for col in [change_1h_col_name, change_24h_col_name, change_7d_col_name]:
        if col in df_display.columns:
             styler = styler.map(style_negative_red, subset=[col])
    
    # Definir propriedades de alinhamento e peso da fonte
    styler = styler.set_properties(subset=['Nome'], **{'text-align': 'left', 'font-weight': 'bold'})
    styler = styler.set_properties(
        subset=[price_col_name, market_cap_col_name, change_1h_col_name, change_24h_col_name, change_7d_col_name], 
        **{'text-align': 'right'}
    )
    if "Rank" in df_display.columns: # Estilizar coluna Rank se ela existir
        styler = styler.set_properties(subset=["Rank"], **{'text-align': 'center', 'font-weight': 'bold'})

    # Aplicar todos os formatos de string e estilos de tabela
    styler = styler.format(format_dict, na_rep="N/A").set_table_styles([
        {'selector': 'th', 'props': [('background-color', st.get_option("theme.primaryColor")), ('color', st.get_option("theme.backgroundColor")), ('text-align', 'center'), ('font-size', '14px')]},
        {'selector': 'td', 'props': [('padding', '6px 8px'), ('font-size', '13px')]},
        {'selector': 'tr:hover td', 'props': [('background-color', st.get_option("theme.secondaryBackgroundColor"))]}
    ])
    
    return styler

# --- Configuração da Página Streamlit ---
st.set_page_config(page_title="Cripto Tracker Pro 🚀", layout="wide", initial_sidebar_state="expanded")

# --- Título e Timestamp dos Dados ---
st.title("🚀 Cripto Tracker Pro")
market_data_timestamp_placeholder = st.empty() 

# --- Sidebar ---
# Linha na seção da Sidebar
try:
    st.sidebar.image("assets/imagens/astronauta.png", width=100) # Ajuste o caminho e nome do arquivo
except FileNotFoundError:
    st.sidebar.warning("Arquivo do logo não encontrado. Verifique o caminho.") # Exemplo de logo
st.sidebar.header("⚙️ Controles")
vs_currency_option = st.sidebar.selectbox(
    "Moeda de Cotação:", ("usd", "brl"), index=0, 
    format_func=lambda x: x.upper() + (" (Dólar)" if x == "usd" else " (Real)")
)
# O slider agora controla quantas moedas da lista de 50 buscadas são mostradas na tabela
num_coins_to_display_in_table = st.sidebar.slider("🪙 Quantidade de Criptos na Tabela:", 1, 50, 10) 
days_for_chart = st.sidebar.select_slider(
    "📈 Período do Gráfico:", options=[7, 30, 90, 365], value=30,
    format_func=lambda x: f"{x} dias"
)

if st.sidebar.button("🔄 Recarregar Dados da API", use_container_width=True, type="primary"):
    st.cache_data.clear()
    st.rerun()
st.sidebar.caption("Nota: Recarregar frequentemente pode atingir os limites da API.")

page_load_time = datetime.now()
st.sidebar.markdown(f"<p style='font-size:0.8em; color:gray;'>Página carregada em: {page_load_time.strftime('%d/%m/%Y %H:%M:%S')}</p>", unsafe_allow_html=True)


# --- Corpo Principal ---
# Busca os dados de mercado (e o timestamp da busca)
# Sempre busca 50 para ter uma boa lista para o selectbox de detalhes, independentemente do slider da tabela
all_crypto_data_raw, market_data_fetch_time = fetch_crypto_markets_data(
    vs_currency=vs_currency_option, 
    per_page=50 
)

if all_crypto_data_raw:
    market_data_timestamp_placeholder.caption(f"Dados de mercado da CoinGecko atualizados pela API em: {market_data_fetch_time.strftime('%d/%m/%Y %H:%M:%S')}")
else:
    market_data_timestamp_placeholder.caption(f"Falha ao buscar dados de mercado. Tentativa em: {market_data_fetch_time.strftime('%d/%m/%Y %H:%M:%S')}")

if not all_crypto_data_raw:
    st.error("Não foi possível carregar os dados das criptomoedas. Verifique sua conexão ou aguarde e tente recarregar usando o botão na sidebar.")
else:
    # --- Tabela Principal ---
    st.subheader("💹 Visão Geral do Mercado")
    
    # Filtra a lista de dados brutos para a quantidade a ser exibida na tabela
    # Garante que market_cap_rank não é None e está dentro do limite do slider
    crypto_data_list_for_table = [
        c for c in all_crypto_data_raw 
        if c.get('market_cap_rank') is not None and c['market_cap_rank'] <= num_coins_to_display_in_table
    ]
    # Ordena por rank, caso a API não garanta ou se a filtragem bagunçar
    crypto_data_list_for_table.sort(key=lambda x: x.get('market_cap_rank') or float('inf'))


    df_styler = process_markets_data_for_display(crypto_data_list_for_table, vs_currency=vs_currency_option)
    # Ajusta a altura da tabela dinamicamente
    table_height = (min(num_coins_to_display_in_table, len(crypto_data_list_for_table)) + 1) * 38 + 3 
    st.dataframe(df_styler, use_container_width=True, height=table_height)


    st.markdown("---")
    # --- Seção de Detalhes e Gráfico da Moeda Selecionada ---
    st.subheader("🔍 Análise Detalhada da Criptomoeda")
    
    coin_names_ids = {
        f"{c['name']} ({c['symbol'].upper()})": c['id'] 
        for c in all_crypto_data_raw # Usa a lista completa para o selectbox
        if c.get('name') and c.get('id')
    }
    
    if not coin_names_ids:
        st.warning("Nenhuma criptomoeda disponível para seleção.")
    else:
        if 'selected_coin_key' not in st.session_state or st.session_state.selected_coin_key not in coin_names_ids.keys():
            st.session_state.selected_coin_key = list(coin_names_ids.keys())[0] if coin_names_ids else None

        selected_coin_name = st.selectbox(
            "Selecione uma Criptomoeda para Análise:", 
            options=list(coin_names_ids.keys()),
            key='selected_coin_key'
        )

        if selected_coin_name:
            selected_coin_id = coin_names_ids[selected_coin_name]
            selected_coin_details = next((c for c in all_crypto_data_raw if c['id'] == selected_coin_id), None)

            if selected_coin_details:
                col1, col2 = st.columns([1, 2.5]) # Ajuste de proporção

                with col1:
                    st.image(selected_coin_details.get('image'), width=70, caption=selected_coin_details.get('name'))
                    
                    price_selected = float(selected_coin_details.get('current_price', 0))
                    change_24h_selected = float(selected_coin_details.get('price_change_percentage_24h_in_currency', 0)) # Usar o campo correto
                    market_cap_selected = float(selected_coin_details.get('market_cap', 0))
                    volume_24h_selected = float(selected_coin_details.get('total_volume', 0))

                    currency_symbol_display = "$" if vs_currency_option == "usd" else "R$"
                    
                    price_str = f"{price_selected:,.2f}"
                    market_cap_str = f"{market_cap_selected:,.0f}"
                    volume_str = f"{volume_24h_selected:,.0f}"
                    
                    if vs_currency_option == "brl":
                        price_str = format_value_brl_style(price_str)
                        market_cap_str = format_value_brl_style(market_cap_str)
                        volume_str = format_value_brl_style(volume_str)

                    st.metric(label="Preço Atual", value=f"{currency_symbol_display}{price_str}", delta=f"{change_24h_selected:.2f}%".replace('.',',' if vs_currency_option == 'brl' else '.'))
                    st.markdown(f"**Capitalização:** {currency_symbol_display}{market_cap_str}")
                    st.markdown(f"**Volume (24h):** {currency_symbol_display}{volume_str}")
                    
                    high_24 = selected_coin_details.get('high_24h')
                    low_24 = selected_coin_details.get('low_24h')
                    if high_24 and low_24:
                        high_24_str = f"{float(high_24):,.2f}"
                        low_24_str = f"{float(low_24):,.2f}"
                        if vs_currency_option == "brl":
                            high_24_str = format_value_brl_style(high_24_str)
                            low_24_str = format_value_brl_style(low_24_str)
                        st.markdown(f"**Alta (24h):** {currency_symbol_display}{high_24_str}")
                        st.markdown(f"**Baixa (24h):** {currency_symbol_display}{low_24_str}")

                with col2:
                    chart_data_placeholder = st.empty()
                    with st.spinner(f"Carregando gráfico para {selected_coin_name}..."):
                        chart_df, chart_data_fetch_time = fetch_crypto_chart_data(selected_coin_id, vs_currency_option, str(days_for_chart))
                        if not chart_df.empty:
                            fig = px.line(chart_df, x='timestamp', y='price', title=f"Histórico de Preços ({selected_coin_name})")
                            fig.update_layout(
                                xaxis_title="Data", 
                                yaxis_title=f"Preço ({vs_currency_option.upper()})",
                                paper_bgcolor='rgba(0,0,0,0)', 
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color=st.get_option("theme.textColor")), # Usa a cor do tema
                                height=400 
                            )
                            fig.update_traces(line=dict(color=st.get_option("theme.primaryColor"), width=2.5)) # Usa a cor do tema
                            chart_data_placeholder.plotly_chart(fig, use_container_width=True)
                            st.caption(f"Dados do gráfico atualizados pela API em: {chart_data_fetch_time.strftime('%d/%m/%Y %H:%M:%S')}")
                        else:
                            chart_data_placeholder.warning(f"Não foi possível carregar os dados do gráfico para {selected_coin_name}.")
            else:
                st.warning("Detalhes da moeda selecionada não encontrados.")

st.markdown("---")
st.markdown(f"<p style='text-align: center; font-size:0.9em; color:gray;'>Dashboard CriptoTracker Pro | {datetime.now().year} | Jequié-BA, Brasil</p>", unsafe_allow_html=True)