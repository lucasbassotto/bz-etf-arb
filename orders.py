from metatraderlib import orders, cancel_order
import MetaTrader5 as mt5
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

etf = [x for x in orders() if x["symbol"] == "SOLH11"]

for x in etf:
    cancel_order(x["symbol"],x["ticket"])