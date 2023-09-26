
import asyncio
from binance import AsyncClient, BinanceSocketManager
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

async def binance_client():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client, user_timeout=60)
    ts_btc = bm.trade_socket('BTCUSDT') 

    async with ts_btc as tscm_btc:
        while True:
            data = await tscm_btc.recv()
            price = round(float(data['p']))
            # print('BTC:', price, 'USDT')
            socketio.emit('btc_price_update', {'price': price})

@app.route('/')
def index():
    return render_template('index.html')

def start_binance_client():
    asyncio.run(binance_client())

if __name__ == "__main__":
    socketio.start_background_task(target=start_binance_client)
    socketio.run(app, debug=True)
