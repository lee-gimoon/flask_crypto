
# 두개의 코인의 실시간 가격을 웹페이지에 띄어보자.

import asyncio
from binance import AsyncClient, BinanceSocketManager
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

async def handle_btc_socket(ts_btc):
    async with ts_btc as tscm_btc:
        while True:
            data = await tscm_btc.recv()
            price = round(float(data['p']))
            socketio.emit('btc_price_update', {'btc_price': price})

async def handle_eth_socket(ts_eth):
    async with ts_eth as tscm_eth:
        while True:
            data = await tscm_eth.recv()
            price = round(float(data['p']))
            socketio.emit('eth_price_update', {'eth_price': price})

async def binance_client():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client, user_timeout=60)
    
    ts_btc = bm.trade_socket('BTCUSDT')
    ts_eth = bm.trade_socket('ETHUSDT')
    
    await asyncio.gather(handle_btc_socket(ts_btc), handle_eth_socket(ts_eth))

@app.route('/')
def two_coin():
    return render_template('two_coin.html')

def start_binance_client():
    asyncio.run(binance_client())

if __name__ == "__main__":
    socketio.start_background_task(target=start_binance_client)
    socketio.run(app, debug=True)
