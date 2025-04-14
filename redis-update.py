from metatraderlib import orders, positions, history
from functions import init_redis
import MetaTrader5 as mt5
import redis
import pandas as pd
import time
import requests


# Inicializa o terminal MetaTrader 5
if not mt5.initialize():
    print(f"Erro ao inicializar MetaTrader5: {mt5.last_error()}")
    quit()


r = init_redis()
etfs_list = ['QSOL11', 'QETH11', 'QBTC11']
for etf_symbol in etfs_list:
    data = requests.get(f"https://asset-feed.qrpubsrv.com/api/etfs/{etf_symbol}").json()['data']
    symbol = etf_symbol[1:-2]
    basket_value = data['intraday_price_per_share']
    amount = [x for x in data['basket_info'] if x['ticker'] == symbol][0]['amount']
    shares = data['total_shares_outstanding']
    crypto_per_share = float(amount)/float(shares)
    print(etf_symbol, crypto_per_share)
    r.set(f'etf:{etf_symbol}', str(crypto_per_share))

while True:
    r.set("etf:positions", str(positions()))
    r.set("etf:orders", str(orders()))
    print("positions updated", positions())
    time.sleep(5)



