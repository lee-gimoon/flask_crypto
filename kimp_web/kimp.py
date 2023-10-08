import websockets
import asyncio
import json
from flask import Flask, render_template
from flask_socketio import SocketIO
from binance import AsyncClient, BinanceSocketManager

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

prices = {
    'upbit': {
        'KRW-BTC': None,
        'KRW-ETH': None,
        'KRW-XRP': None
    },
    'binance': {
        'BTC': None,
        'ETH': None,
        'XRP': None
    }
}

# 업비트.
async def upbit_client():
    uri = "wss://api.upbit.com/websocket/v1"

    async with websockets.connect(uri, ping_interval=60) as websocket:
        subscribe = [
            {"ticket": "test"},
            {"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH", "KRW-XRP"], "isOnlyRealtime": True},
            {"type": "trade", "codes": ["KRW-BTC", "KRW-ETH", "KRW-XRP"], "isOnlyRealtime": True},
            {"format": "SIMPLE"}
        ]
        subscribe = json.dumps(subscribe)
        await websocket.send(subscribe)

        while True:
            data = await websocket.recv()
            data = json.loads(data)
            coin_code = data.get("cd")

            if data['ty'] == 'trade':
                price = round(float(data['tp']), 2)
                socketio.emit(f"{coin_code}_trade", {"price": price})
                prices['upbit'][coin_code] = price # 김프계산을 위해 값 저장.
                calculate_and_emit_premium()

            elif data['ty'] == 'ticker':
                scr = round(100*data['scr'], 2)
                atp24h = round(float(data['atp24h']))
                socketio.emit(f"{coin_code}_ticker", {"scr": scr, "atp24h": atp24h})


# 바이낸스.
# 관심있는 암호화폐 목록
cryptos = ['BTC', 'ETH', 'XRP']

# 가격 정보를 처리하는 코루틴
async def handle_price_socket(symbol, ts):
    async with ts as tscm:
        while True:
            data = await tscm.recv()
            price = (float(data['p']))
            socketio.emit(f'{symbol.lower()}_price_update', {f'{symbol.lower()}_price': price})
            prices['binance'][symbol] = price # 김프계산을 위해 값 저장.
            calculate_and_emit_premium()

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

# 예시 환율
usd_to_krw = 1349.0  # 실제 서비스에서는 이 값을 실시간으로 업데이트해야 합니다.

def calculate_and_emit_premium():
    for coin in cryptos:
        upbit_key = f"KRW-{coin}"
        upbit_price = prices['upbit'].get(upbit_key, None)  # 기본값을 None으로 설정
        binance_price = prices['binance'].get(coin, None)  # 기본값을 None으로 설정

        # 두 거래소의 가격 정보가 모두 있는 경우에만 계산을 진행. (upbit_price와 binance_price 둘 다 None이 아닐 때만 김프 계산을 진행하도록 수정되었습니다.)
        if upbit_price is not None and binance_price is not None:
            # 바이낸스 가격을 KRW로 환산
            binance_price_in_krw = binance_price * usd_to_krw
            premium = ((upbit_price - binance_price_in_krw) / binance_price_in_krw) * 100
            socketio.emit(f'{upbit_key}_premium', {'premium': premium})


@app.route('/')
def kimp():
    return render_template('kimp.html')

async def combined_client():
    await asyncio.gather(upbit_client(), binance_client())

def run_combined_client():
    asyncio.run(combined_client())

if __name__ == "__main__":
    socketio.start_background_task(target=run_combined_client) # socketio.start_background_task()는 별도의 스레드를 생성하여 그곳에서 실행시킴. (당연하게도 일반 함수만 target함)
    socketio.run(app, debug=True)

# 김프계산 파이썬(서버) or 자바스크립트(클라이언트)
# 서버에서 미리 계산하여 전송하는 것이 클라이언트의 연산 부담을 줄이고, 일관된 데이터를 제공할 수 있기 때문에 파이썬 방법을 추천합니다.