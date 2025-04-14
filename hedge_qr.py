import ccxt
import redis
import logging
import MetaTrader5 as mt5
import ast
from time import sleep
from metatraderlib import positions
from functions import init_binance, init_redis, send_order_binance, get_binance_ticker

etf_symbol = 'QSOL11'
# Configuração do logging
logging.basicConfig(
    level=logging.DEBUG,  # Define o nível de log como DEBUG para capturar todos os tipos de log
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Exibe no console
        logging.FileHandler("bot_errors.log", mode='a')  # Registra em um arquivo de log
    ]
)

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

# Inicializar conexões
binance = init_binance()
r = init_redis()

symbol_binance = f'{etf_symbol[1:-2]}/USDT'
currency_per_quota = float(r.get(f"etf:{etf_symbol}"))

def get_qsol11_position():
    try:
        etf_positions = positions() 
        
        logging.debug(f"Posições obtidas: {etf_positions}")

        qsol11 = next((position for position in etf_positions if position['symbol'] == etf_symbol), None)
        if qsol11:
            logging.debug(f"Posição de {etf_symbol} encontrada: {qsol11}")
            return [qsol11['volume'], qsol11['type']]
        else:
            logging.warning(f"Posição de {etf_symbol} não encontrada.")
            return None
    except Exception as e:
        logging.error(f"Erro ao obter posição de {etf_symbol}: {str(e)}")
        return None

# Pega a posição inicial de QSOL11
positiondata = get_qsol11_position()
side = positiondata[1]

if side == 0:
    initial_position = positiondata[0]

if side == 1:
    initial_position = -positiondata[0]

if initial_position is None:
    logging.error(f"Posição inicial de {etf_symbol} não encontrada.")
    quit()

initial_size = initial_position
logging.info(f"Posição inicial de {etf_symbol}: {initial_size}")

# Loop para monitorar o delta
while True:
    try:
        logging.debug("Iniciando o loop para monitorar o delta.")
        
        # Pega a posição inicial de QSOL11
        positiondata = get_qsol11_position()
        side = positiondata[1]

        if side == 0:
            current_position = positiondata[0]

        if side == 1:
            current_position = -positiondata[0]
        
        if current_position is None:
            logging.error(f"Posição de {etf_symbol} não encontrada.")
            break

        current_size = current_position
        delta = current_size - initial_size
        logging.info(f"Delta atual: {delta}")
        print("delta", delta, "position", current_size, "symbol", etf_symbol)
        
        book = get_binance_ticker(binance, symbol_binance)
        bid = book[0]
        ask = book[1]
        # Se o delta for maior que 100 negativo
        if delta <= -100:
            print(f"Delta negativo maior que 100. Comprando {currency_per_quota*delta} {symbol_binance}.")
            logging.info(f"Delta negativo maior que 100. Comprando {currency_per_quota*delta} {symbol_binance}.")
            # Simulando a execução da ordem
            order = binance.create_market_order(symbol=symbol_binance, side="buy", amount=currency_per_quota*abs(delta))
            print(order)
            if order:
                initial_size = current_size  # Atualiza o tamanho inicial após a compra
                logging.info(f"Tamanho inicial atualizado para {initial_size}")

        # Se o delta for maior que 100 positivo
        elif delta >= 100:
            logging.info(f"Delta positivo maior que 100. Vendendo {currency_per_quota*delta} {symbol_binance}.")
            print(f"Delta positivo maior que 100. Vendendo {currency_per_quota*delta} {symbol_binance}.")
            # Simulando a execução da ordem
            order = binance.create_market_order(symbol=symbol_binance, side="sell", amount=currency_per_quota*delta)
            print(order)
            if order:
                initial_size = current_size  # Atualiza o tamanho inicial após a venda
                logging.info(f"Tamanho inicial atualizado para {initial_size}")

        sleep(0.2)  # Aguarda 0.2 segundos antes de verificar novamente

    except Exception as e:
        logging.error(f"Erro no loop principal: {str(e)}")
        break
