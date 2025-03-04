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

def buscaMercadoBRA(ticker):
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
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar mercado para {ticker}: {e}")
        return None

def buscaCriptomoeda(ticker):
    TOKEN = config('TOKEN_BRAPI')
    url = f"https://brapi.dev/api/v2/crypto?coin={ticker}&currency=BRL&range=5d&interval=1d&token={TOKEN}"
    
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
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
        
        response = None
        if (tipo_aplicacao == 9 or tipo_aplicacao == 10):
            response = buscaMercadoBRA(ticker)
        elif (tipo_aplicacao == 14):
            response = buscaCriptomoeda(ticker)
             
        if response is None or "results" not in response:
            logger.warning(f"Sem dados de cotação para {ticker} (ID {id_aplicacao})")
            continue

        try:
            fii = response["results"][0]
            preco_atual = fii.get('regularMarketPrice', None)
            if preco_atual is None:
                logger.warning(f"Preço atual não encontrado para {ticker}")
                continue
            
            dados.append({
                "sigla": ticker,
                "idaplicacao": id_aplicacao,
                "preco_cotado": float(preco_atual),
                "data_hora_cadastro": data_hora_atual.strftime("%Y-%m-%d %H:%M:%S")
            })
        except KeyError as e:
            logger.error(f"Erro ao processar os dados de {ticker}: {e}")
            continue

    print(dados)

except Exception as e:
    logger.error(f"Erro ao buscar informações: {e}")