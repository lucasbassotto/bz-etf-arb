import requests
import json
from functions import init_redis
import time
import pygsheets
import pandas as pd
from metatraderlib import quotes
import MetaTrader5 as mt5
import ccxt

coinbase = ccxt.coinbase({"enableRateLimit": True})

gc = pygsheets.authorize(service_file="arbimulti.json")
sh = gc.open('ETF')
wks_tickers = sh.worksheet_by_title("tickers")
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
    etfs_list = ['QSOL11', 'QETH11', 'QBTC11']
    hash_list = ['ETHE11', 'HASH11', 'BITH11', 'SOLH11']

    # Lista para guardar os dados formatados
    qr_quotes = []

# Loop para os ETFs QR
    for etf_symbol in etfs_list:
        crypto = etf_symbol[1:-2]  # Remove o primeiro e os dois últimos caracteres

        usd = redis_client.get('etf:usdbrl')
        usd_brl = float(json.loads(usd))

        data = requests.get(f"https://asset-feed.qrpubsrv.com/api/etfs/{etf_symbol}").json()['data']
        basket_value = data['intraday_price_per_share']

        shares_outstanding = data["total_shares_outstanding"]
        basket_info = data["basket_info"]
        coinbasebid = coinbase.fetch_ticker(f"{crypto}/USD")["bid"]

        coin_value = 0
        usd_value = 0
        others_value = 0

        for x in basket_info:
            if x["ticker"] == crypto:
                coin_value = float(x["amount"])*coinbasebid*usd_brl

            elif x["ticker"] == "USD":
                usd_value = float(x["amount"])*usd_brl
            else:
                others_value += float(x["last_value"])
                    
        fair_price = (coin_value + usd_value + others_value) / float(shares_outstanding)
        ask = quotes(etf_symbol)[0]['best_ask']
        bid = quotes(etf_symbol)[0]['best_bid']
        qr_quotes.append({"ETF": etf_symbol, "Fair Price": fair_price, "BID": bid, "ASK": ask})

    # Loop para os ETFs Hashdex
    for hash_symbol in hash_list:
        hash_data = requests.get(f"https://api2.hashdex.io/marketdata/v2/etf/inavs").json()
        fair_price = float(get_hash11_data(hash_data, hash_symbol)['inavPerShare'])
        ask = quotes(hash_symbol)[0]['best_ask']
        bid = quotes(hash_symbol)[0]['best_bid']
        qr_quotes.append({"ETF": hash_symbol, "Fair Price": fair_price, "BID": bid, "ASK": ask})


    # Criar DataFrame formatado
    df_combined = pd.DataFrame(qr_quotes)
    print(df_combined)

    # Escrever na planilha começando na célula A1
    wks_tickers.set_dataframe(df_combined, (1, 1))

    # Aguarda antes de repetir
    time.sleep(1)