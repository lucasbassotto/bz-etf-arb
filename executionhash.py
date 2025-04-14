from metatraderlib import orders, cancel_order, cancel_all_orders, order_buy, order_sell, quotes
from functions import init_redis
import MetaTrader5 as mt5
import requests
import json
import redis
import ccxt
from datetime import datetime
import time

coinbase = ccxt.coinbase({"enableRateLimit": True})

redis_client = init_redis()

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


etf_symbol = 'HASH11'
symbol = 'SOL/USD'
crypto = 'SOL'
spread_buy = 0.995
spread_sell = 1.015
lot_size = 200.0
increment = 0.0

def get_hash11_data(data):
    # Filtra os dados do HASH11
    hash11_data = next((item for item in data if item['info']['fundName'] == etf_symbol), None)
    
    if hash11_data:
        # Se os dados do HASH11 forem encontrados, retorna o que você precisa
        return hash11_data
    else:
        return None

while True:
    if len(orders()) != 0:
        cancel_all_orders(etf_symbol)
        
    usd = redis_client.get('etf:usdbrl')
    usd_brl = float(json.loads(usd))

    ticker = quotes(etf_symbol)
    ask = quotes(etf_symbol)[0]['best_ask']
    bid = quotes(etf_symbol)[0]['best_bid']
    
    data = requests.get(f"https://api2.hashdex.io/marketdata/v2/etf/inavs").json()     
    basket_value = get_hash11_data(data)['inavPerShare']

    price_buy = float(basket_value)*spread_buy
    price_sell = float(basket_value)*spread_sell


    if bid < price_buy:
        price_buy = bid+increment

    if ask > price_sell:
        price_sell = ask-increment
        print(basket_value, price_buy, price_sell)

    order_buy(etf_symbol, lot_size, price_buy)
    order_sell(etf_symbol, lot_size, price_sell)

    time.sleep(5)

