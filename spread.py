import requests
import json
from functions import init_redis
import time
import ccxt
import pandas as pd
from metatraderlib import quotes
import MetaTrader5 as mt5
from functions import init_redis

coinbase = ccxt.coinbase({"enableRateLimit": True})

redis_client = init_redis()


def get_hash11_data(data, etf):
    # Filtra os dados do HASH11
    hash11_data = next((item for item in data if item['info']['fundName'] == etf), None)
    
    if hash11_data:
        # Se os dados do HASH11 forem encontrados, retorna o que você precisa
        return hash11_data
    else:
        return None
    
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

while True:
    last = coinbase.fetch_ticker(f"{'BTC'}/USD")["bid"]
    usd = redis_client.get('etf:usdbrl')
    print(usd)
    usd_brl = float(json.loads(usd))
    ask = quotes('BITG25')[0]['best_ask']
    bid = quotes('BITG25')[0]['best_bid']

    print('spreadbuy', bid/(usd_brl*last), 'spreadsell', ask/(usd_brl*last))

    # Aguarda antes de repetir
    time.sleep(0.1)