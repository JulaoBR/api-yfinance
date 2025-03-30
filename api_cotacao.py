import requests
import logging

from datetime import datetime, timedelta, timezone
from decouple import config
from src.models.aplicacao_model import AplicacaoModel

TICKERS = []

# Definir o fuso horário UTC-3
fuso_horario = timezone(timedelta(hours=-3))
data_hora_atual = datetime.now(fuso_horario)

PATH_LOGGING = config('PATH_LOGGING')

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,  # Define o nível mínimo de log
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato do log
    handlers=[
        logging.FileHandler(PATH_LOGGING),  # Arquivo onde os logs serão salvos
        logging.StreamHandler()  # Também mostra no console
    ]
)
logger = logging.getLogger(__name__)

def buscaPrecoAtualMercadoBRA(ticker):
    TOKEN = config('TOKEN_BRAPI')
    url = f"https://brapi.dev/api/quote/{ticker}"
    params = {
        'range': '1d',
        'interval': '1d',
        'fundamental': 'false',
        'dividends': 'false',
        'token': TOKEN,
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Levanta um erro se o status code não for 2xx
        response = response.json()
        fii = response["results"][0]

        preco_atual = fii.get('regularMarketPrice', None)
        return preco_atual
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar mercado para {ticker}: {e}")
        return None

def buscaPrecoAtualCriptomoeda(ticker):
    TOKEN = config('TOKEN_BRAPI')
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={ticker}BRL"

    try:
        response = requests.get(url)
        response.raise_for_status()
        fii = response.json()

        preco_atual = fii.get('price', None)
        return preco_atual
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar criptomoeda para {ticker}: {e}")
        return None

try:
    with AplicacaoModel() as model_aplicacao:
        TICKERS = model_aplicacao.consultrar()

    dados = []
    for aplicacao in TICKERS:
        tipo_aplicacao = aplicacao['idcategoria_aplicacao']
        id_aplicacao = aplicacao['idaplicacao']
        ticker = aplicacao['descricao']
        
        preco_atual = None
        if (tipo_aplicacao == 9 or tipo_aplicacao == 10):
            preco_atual = buscaPrecoAtualMercadoBRA(ticker)
        elif (tipo_aplicacao == 14):
            preco_atual = buscaPrecoAtualCriptomoeda(ticker)

        try:
            if preco_atual is None:
                logger.warning(f"Preço atual não encontrado para {ticker} (ID {id_aplicacao})")
                continue
            
            dados.append({
                "sigla": ticker,
                "idaplicacao": id_aplicacao,
                "preco_cotado": preco_atual,
                "data_hora_cadastro": data_hora_atual.strftime("%Y-%m-%d %H:%M:%S")
            })
        except KeyError as e:
            logger.error(f"Erro ao processar os dados de {ticker}: {e}")
            continue

    print(dados)

except Exception as e:
    logger.error(f"Erro ao buscar informações: {e}")