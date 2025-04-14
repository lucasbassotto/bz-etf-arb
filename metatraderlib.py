import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

def quotes(symbol):
    # Verifique se o símbolo está disponível
    if mt5.symbol_select(symbol, True):
        symbol_info = mt5.symbol_info(symbol)
        return [{'best_bid':symbol_info.bid, 'best_ask':symbol_info.ask}]

def positions():
# Obter as posições abertas
    positions = mt5.positions_get()

    if positions is None or len(positions) == 0:
        print("Não há posições abertas.")
    else:
        # Converter as posições em um DataFrame
        positions_data = []
        for position in positions:
            positions_data.append(position._asdict())
    return positions_data

def history(from_date, to_date):
    # Obtém histórico de ordens
    history = mt5.history_orders_get(from_date, to_date)
    history_data = []
    
    for trade in history:
        history_data.append(trade._asdict())
    
    return history_data

def orders():
    orders = mt5.orders_get()
    order_data = []
    if orders is None:
        print("Nenhuma ordem pendente encontrada. Detalhes:", mt5.last_error())
    else:
        for order in orders:
            order_data.append(order._asdict())
    
    return order_data

def order_buy(symbol, lot_size, price):
    # Configurar os detalhes da ordem
    order_request = {
        "action": mt5.TRADE_ACTION_PENDING,  # Ordem pendente
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_BUY_LIMIT,  # Tipo de ordem: compra limitada
        "price": price,
        "sl": 0.0,  # Stop Loss (0.0 para não definir)
        "tp": 0.0,  # Take Profit (0.0 para não definir)
        "deviation": 1,  # Tolerância de preço em pontos
        "magic": int(datetime.now().timestamp()),
        "comment": "Ordem passiva via Python",
        "type_time": mt5.ORDER_TIME_GTC,  # Good Till Cancelled (válida até ser cancelada)
        "type_filling": mt5.ORDER_FILLING_RETURN,  # Experimente ORDER_FILLING_IOC ou ORDER_FILLING_RETURN
    }
    
    # Enviar a ordem
    result = mt5.order_send(order_request)
    
    # Verificar resultado
    if result is None:
        print("Erro ao enviar a ordem. Detalhes do erro:", mt5.last_error())
    else:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Erro ao enviar a ordem. Código de retorno: {result.retcode}")
            print("Detalhes:", result)
        else:
            print("Ordem enviada com sucesso!")
            print(result)

def order_sell(symbol, lot_size, price):
    # Configurar os detalhes da ordem
    order_request = {
        "action": mt5.TRADE_ACTION_PENDING,  # Ordem pendente
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_SELL_LIMIT,  # Tipo de ordem: compra limitada
        "price": price,
        "sl": 0.0,  # Stop Loss (0.0 para não definir)
        "tp": 0.0,  # Take Profit (0.0 para não definir)
        "deviation": 1,  # Tolerância de preço em pontos
        "magic": int(datetime.now().timestamp()),
        "comment": "Ordem passiva via Python",
        "type_time": mt5.ORDER_TIME_GTC,  # Good Till Cancelled (válida até ser cancelada)
        "type_filling": mt5.ORDER_FILLING_RETURN,  # Experimente ORDER_FILLING_IOC ou ORDER_FILLING_RETURN
    }
    
    # Enviar a ordem
    result = mt5.order_send(order_request)
    
    # Verificar resultado
    if result is None:
        print("Erro ao enviar a ordem. Detalhes do erro:", mt5.last_error())
    else:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Erro ao enviar a ordem. Código de retorno: {result.retcode}")
            print("Detalhes:", result)
        else:
            print("Ordem enviada com sucesso!")
            print(result)

def cancel_order(symbol, order_id):
    # Configurar os detalhes para cancelar a ordem
    cancel_request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "symbol": symbol,
        "order": order_id,
        "comment": "Cancelando ordem via Python"
    }
    
    # Enviar a solicitação para cancelar a ordem
    result = mt5.order_send(cancel_request)
    
    # Verificar o resultado
    if result is None:
        print("Erro ao cancelar a ordem. Detalhes:", mt5.last_error())
    else:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Erro ao cancelar a ordem. Código de retorno: {result.retcode}")
            print("Detalhes:", result)
        else:
            print(f"Ordem {order_id} cancelada com sucesso!")
            print(result)


def cancel_all_orders(symbol):
    orderslist = [x for x in orders() if x["symbol"] == symbol]
    # Iterar sobre as ordens e cancelar cada uma
    for order in orderslist:
        ticket = order['ticket']
        symbol = order['symbol']
        success = cancel_order(symbol, ticket)
        if success:
            print(f"Ordem {ticket} para o símbolo {symbol} foi cancelada com sucesso.")
        else:
            print(f"Falha ao cancelar a ordem {ticket} para o símbolo {symbol}.")

