import ccxt
import redis
import logging
import uuid
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do .env
load_dotenv()

# Configurar o logging
logging.basicConfig(
    filename="bot_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def get_binance_ticker(binance, symbol):
    try:
        # Usando o método fetch_ticker para obter informações sobre o ticker
        ticker = binance.fetch_ticker(symbol)
        return [ticker['bid'], ticker['ask']]  # Retorna o último preço

    except Exception as e:
        print(f"Erro ao obter os dados do ticker: {e}")
        return None


# Inicializar o conector Bybit
def init_binance():
    return ccxt.binance({
        'apiKey': os.getenv("BINANCE_APIKEY"),
        'secret': os.getenv("BINANCE_SECRET"),
        'enableRateLimit': True,
        'options': {
        'defaultType': 'future'}
    })

def init_hyperliquid():
    return ccxt.hyperliquid({
        'apiKey': os.getenv("hyperAPI_KEY"),
        'secret': os.getenv("hyperAPI_SECRET"),
        'enableRateLimit': True,
        'options': {
        'defaultType': 'swap'}
    })

# Inicializar conexão Redis
def init_redis():
    try:
        r = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True
        )
        return r
    except redis.ConnectionError as e:
        logging.error(f"Erro ao conectar ao Redis: {e}")
        raise

# Funções utilitárias
def cancel_all_orders(binance, symbol=None):
    try:
        if symbol:
            response = binance.cancel_all_orders(symbol)
        else:
            response = binance.cancel_all_orders()
        print(f"Todas as ordens foram canceladas com sucesso para {symbol or 'todos os símbolos'}")
        return response
    except Exception as e:
        print(f"Erro ao cancelar ordens: {e}")

def send_order_binance(binance, symbol, side, amount, price):
    try:
        client_order_id = f"BOT_{uuid.uuid4()}"
        order = binance.create_order(symbol, 'LIMIT', side, amount, price, {'clientOrderId': client_order_id})
        print(f"Ordem enviada com sucesso: ID={client_order_id}")
        return order
    except Exception as e:
        logging.error(f"Erro ao enviar ordem: {e}")
        print("Erro ao enviar ordem.")

# Função para obter o preço atual do USDT/USD na Kraken
def get_usdt_usd_price(kraken):
    try:
        ticker = kraken.fetch_ticker('USDT/USD')
        return float(ticker['ask'])
    except Exception as e:
        logging.error(f"Erro ao buscar ticker Kraken: {e}")
        return None
    

def hyperliquidinfo():
    # Inicializa a conexão com a HyperLiquid
    exchange = ccxt.hyperliquid({
            'apiKey': os.getenv("hyperAPI_KEY"),
            'secret': os.getenv("hyperAPI_SECRET"),
            'enableRateLimit': True,
            'options': {
            'defaultType': 'swap'}
        })

    try:
        balance = exchange.fetch_balance(params={"user": os.getenv("USER_ID")})
        balance = balance["info"]
        balances = balance["marginSummary"]
        positions = balance["assetPositions"]
        return {"saldo": balances, "positions": positions} 
    except Exception as e:
        print(f"Erro ao buscar saldo: {e}")
        return None