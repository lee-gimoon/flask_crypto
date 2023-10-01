import asyncio
from binance import AsyncClient, BinanceSocketManager
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

async def handle_trade_socket(ts):
    async with ts:
        while True:
            trade_data = await ts.recv()
            socketio.emit('btc_price_update', {'btc_price': float(trade_data['p'])})

async def handle_ticker_socket(ts):
    async with ts:
        while True:
            ticker_data = await ts.recv()
            socketio.emit('ticker_update', {
                'change_rate': float(ticker_data['P']),
                'volume': round(float(ticker_data['q']))
            })

async def binance_client():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client, user_timeout=60)

    trade_socket = bm.trade_socket('BTCUSDT')
    ticker_socket = bm.symbol_ticker_socket('BTCUSDT')

    # 두 개의 태스크를 동시에 실행
    await asyncio.gather(handle_trade_socket(trade_socket), handle_ticker_socket(ticker_socket))

@app.route('/')
def final():
    return render_template('final.html')

def start_binance_client():
    asyncio.run(binance_client())

if __name__ == "__main__":
    socketio.start_background_task(target=start_binance_client)
    socketio.run(app, debug=True)
