import ccxt
import redis
import logging
import ast
from time import sleep
from functions import init_binance, init_redis, send_order_binance, get_binance_ticker
from metatraderlib import positions
import MetaTrader5 as mt5

etf_symbol = 'HASH11'

if etf_symbol == 'HASH11':
    etf_basket={'BTC': 0.0001050915085, 'ETH': 0.0005869303968,'XRP': 0.326341184}

if etf_symbol == 'SOLH11':
    etf_basket={"SOL": 0.028}

# Configuração do logging
logging.basicConfig(
    level=logging.DEBUG,  # Define o nível de log como DEBUG para capturar todos os tipos de log
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Exibe no console
        logging.FileHandler("bot_errors.log", mode='a')  # Registra em um arquivo de log
    ]
)

# Inicializar conexões
binance = init_binance()

# Inicializa o terminal MetaTrader 5
if not mt5.initialize():
    print(f"Erro ao inicializar MetaTrader5: {mt5.last_error()}")
    quit()

# Mostra informações da conta conectada
account_info = mt5.account_info()
if account_info is not None:
    print(f"Conectado à conta {account_info.login}")
else:
    print(f"Erro ao obter informações da conta: {mt5.last_error()}")


def get_hash11_position():
    try:
        etf_positions = positions()
        logging.debug(f"Posições obtidas: {etf_positions}")

        hash11 = next((position for position in etf_positions if position['symbol'] == etf_symbol), None)
        if hash11:
            logging.debug(f"Posição encontrada: {hash11}")
            return hash11['volume']
        else:
            logging.warning("Posição não encontrada.")
            return 0.0
    except Exception as e:
        logging.error(f"Erro ao obter posição: {str(e)}")
        return None

# Pega a posição inicial de HASH11
initial_position = get_hash11_position()
if initial_position is None:
    logging.error("Posição inicialnão encontrada.")
    quit()

initial_size = initial_position
logging.info(f"Posição inicial: {initial_size}")

# Loop para monitorar o delta
while True:
    try:
        logging.debug("Iniciando o loop para monitorar o delta.")
        
        current_position = get_hash11_position()
        if current_position is None:
            logging.error("Posição não encontrada.")
            break

        current_size = current_position
        delta = current_size - initial_size
        logging.info(f"Delta atual: {delta}")
        print("delta", delta, "position", current_size, "symbol", etf_symbol)
        
        # Se o delta for maior que 100 negativo
        if delta <= -100:
            for symbol, quantity in etf_basket.items():
                quantity_to_buy = quantity * delta # Multiplica a quantidade por 1000
                # Enviar a ordem para o mercado
                print(f"Delta negativo maior que 100. Comprando {quantity_to_buy} {symbol}.")
                logging.info(f"Delta negativo maior que 100. Comprando {quantity_to_buy} {symbol}.")
                order = binance.create_market_order(symbol=f'{symbol}/USDT', side="buy", amount=abs(quantity_to_buy))
                sleep(0.1)
                logging.info(f"Ordem executada para {symbol}: {quantity_to_buy} unidades.")
            
            initial_size = current_size  # Atualiza o tamanho inicial após a compra
            logging.info(f"Tamanho inicial atualizado para {initial_size}")
        # Se o delta for maior que 100 positivo
        elif delta >= 100:
            for symbol, quantity in etf_basket.items():
                quantity_to_sell = quantity * delta # Multiplica a quantidade por 1000
                # Enviar a ordem para o mercado
                logging.info(f"Delta positivo maior que 100. Vendendo {quantity_to_sell} {symbol}.")
                print(f"Delta positivo maior que 100. Vendendo {quantity_to_sell} {symbol}.")
                order = binance.create_market_order(symbol=f'{symbol}/USDT', side="sell", amount=abs(quantity_to_sell))
                sleep(0.1)
                logging.info(f"Ordem executada para {symbol}: {quantity_to_sell} unidades.")

            initial_size = current_size  # Atualiza o tamanho inicial após a compra
            logging.info(f"Tamanho inicial atualizado para {initial_size}")
        
        sleep(0.2)  # Aguarda 0.2 segundos antes de verificar novamente

    except Exception as e:
        logging.error(f"Erro no loop principal: {str(e)}")
        break
