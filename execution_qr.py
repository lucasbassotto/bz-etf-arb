from metatraderlib import orders, cancel_all_orders, order_buy, order_sell, quotes
from functions import init_redis
import MetaTrader5 as mt5
import requests
import json
import ccxt
from datetime import datetime
import time

coinbase = ccxt.coinbase({"enableRateLimit": True})

redis_client = init_redis()

etf_symbol = 'QSOL11'
symbol = 'SOL/USD'
crypto = 'SOL'
spread_buy = 0.995
spread_sell = 1.01
lot_size = 500.0
increment = 0.0

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

# Variável de estado para dry run
dryrun = False

while True:
    if len(orders()) != 0:
        print("Cancelando todas as ordens ativas...")
        cancel_all_orders(etf_symbol)
        
    usd = redis_client.get('etf:usdbrl')
    print(usd)
    usd_brl = float(json.loads(usd))

    ticker = quotes(etf_symbol)
    ask = quotes(etf_symbol)[0]['best_ask']
    bid = quotes(etf_symbol)[0]['best_bid']
    print(bid, ask, usd_brl)

    data = requests.get(f"https://asset-feed.qrpubsrv.com/api/etfs/{etf_symbol}").json()['data']
    basket_value = data['intraday_price_per_share']

    shares_outstanding = data["total_shares_outstanding"]
    basket_info = data["basket_info"]
    coinbasebid = coinbase.fetch_ticker(f"{crypto}/USD")["bid"]
    
    print(f"Preço atual de SOL/USD (coinbasebid): {coinbasebid}")

    coin_value = 0
    usd_value = 0
    others_value = 0

    for x in basket_info:
        if x["ticker"] == crypto:
            coin_value = float(x["amount"])*coinbasebid*usd_brl
            print(f"Valor do ativo {crypto} na cesta: {coin_value}")

        elif x["ticker"] == "USD":
            usd_value = float(x["amount"])*usd_brl
            print(f"Valor em USD na cesta: {usd_value}")
        else:
            others_value += float(x["last_value"])
            print(f"Valor de outros ativos acumulados: {others_value}")
                
    etfvalue = (coin_value + usd_value + others_value) / float(shares_outstanding)

    print(f"Valor estimado do ETF (etfvalue): {etfvalue}")
    
    price_buy = float(etfvalue) * spread_buy
    price_sell = float(etfvalue) * spread_sell

    etfdelta = float(basket_value) / etfvalue - 1
    print(f"Delta do ETF (etfdelta): {etfdelta}")

    # Entrar em modo dry run se o delta for maior que 0.003
    if etfdelta > 0.5:
        print("ETF delta acima de 0.003. Entrando em modo dry run...")
        dryrun = True

    # Sair do modo dry run quando o delta estiver abaixo de 0.003
    if dryrun and etfdelta <= 0.5:
        print("ETF delta abaixo de 0.003. Saindo do modo dry run...")
        dryrun = False

    # Executar lógica somente se não estiver em modo dry run
    if not dryrun:

        if len(orders()) != 0:
            print("Cancelando ordens existentes antes de reposicionar...")
            cancel_all_orders(etf_symbol)
        
        if bid < price_buy:
            print("tlr")
            price_buy = bid + increment

        if ask > price_sell:
            print(f"tlrsell, {bid}")
            price_sell = ask - increment
            
        print(f"Valores calculados para novas ordens: price_buy = {price_buy}, price_sell = {price_sell}, {basket_value}")

        order_buy(etf_symbol, lot_size, price_buy)
        print(f"Ordem de compra enviada: {lot_size} unidades a {price_buy}")
            
        order_sell(etf_symbol, lot_size, price_sell)
        print(f"Ordem de venda enviada: {lot_size} unidades a {price_sell}")

    time.sleep(5)