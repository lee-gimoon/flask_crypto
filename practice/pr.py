import asyncio
from binance import AsyncClient, BinanceSocketManager
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 관심있는 암호화폐 목록
cryptos = ['BTC', 'ETH', 'XRP', 'NEO', 'QTUM', 'GAS', 'FLM', 'ONT', 'EOS']

# 가격 정보를 처리하는 코루틴
async def handle_price_socket(symbol, ts):
    async with ts as tscm:
        while True:
            data = await tscm.recv()
            price = (float(data['p']))
            socketio.emit(f'{symbol.lower()}_price_update', {f'{symbol.lower()}_price': price})

# 등락율과 거래량 정보를 처리하는 코루틴
async def handle_ticker_socket(symbol, ts):
    async with ts as tscm:
        while True:
            data = await tscm.recv()
            change_rate = float(data['P'])
            volume = round(float(data['q']))
            socketio.emit(f'{symbol.lower()}_ticker_update', {f'{symbol.lower()}_change_rate': change_rate, f'{symbol.lower()}_volume': volume})

async def binance_client():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client, user_timeout=60)

    # 각 코인에 대한 소켓 생성
    price_tasks = [bm.trade_socket(f'{crypto}USDT') for crypto in cryptos]
    ticker_tasks = [bm.symbol_ticker_socket(f'{crypto}USDT') for crypto in cryptos]

    # 모든 코인의 소켓을 동시에 처리하기 위해 asyncio.gather 사용
    all_tasks = [handle_price_socket(crypto, task) for crypto, task in zip(cryptos, price_tasks)] + [handle_ticker_socket(crypto, task) for crypto, task in zip(cryptos, ticker_tasks)]
    await asyncio.gather(*all_tasks)

@app.route('/')
def pr():
    return render_template('pr.html')

def start_binance_client():
    asyncio.run(binance_client())

if __name__ == "__main__":
    socketio.start_background_task(target=start_binance_client)
    socketio.run(app, debug=True)
