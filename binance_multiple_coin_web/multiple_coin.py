
# 바이낸스 다수의 코인들에 대한 실시간 가격을 띄우는 웹.

import asyncio
from binance import AsyncClient, BinanceSocketManager
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

cryptos = ['BTC', 'ETH', 'XRP', 'NEO', 'QTUM', 'GAS', 'FLM', 'ONT', 'EOS']

async def handle_socket(symbol, ts):
    async with ts as tscm:
        while True:
            data = await tscm.recv()
            price = (float(data['p']))
            socketio.emit(f'{symbol.lower()}_price_update', {f'{symbol.lower()}_price': price}) # lower()는 파이썬의 문자열 메서드 중 하나로, 문자열 내의 모든 대문자를 소문자로 변환하는 역할을 합니다.

async def binance_client():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client, user_timeout=60)

    coin_tasks = [bm.trade_socket(f'{crypto}USDT') for crypto in cryptos] # 이 안에서의 연산 결과가 리스트의 각 원소로 추가됩니다. => [bm.trade_socket('BTCUSDT'), bm.trade_socket('ETHUSDT'), .....]

    await asyncio.gather(*[handle_socket(crypto, task) for crypto, task in zip(cryptos, coin_tasks)]) # pr_zip 파일 참조.
    # * 연산자: 이 연산자는 "splat" 또는 "unpacking" 연산자라고도 불립니다. 이 연산자를 사용하면 컬렉션의 원소들을 개별적으로 전개(unpack)할 수 있습니다. 
    # 여기서는 리스트 컴프리헨션의 결과로 생성된 리스트의 원소들을 개별적으로 전개하여, asyncio.gather 함수에 각각의 원소를 별도의 인수로 전달하게 됩니다.
    # 이 때, 함수에 인자로 전달되는 개별 값들 사이에는 컴마(,)가 암시적으로 들어갑니다.

@app.route('/')
def multiple_coin():
    return render_template('multiple_coin.html') 

def start_binance_client():
    asyncio.run(binance_client())

if __name__ == "__main__":
    socketio.start_background_task(target=start_binance_client)
    socketio.run(app, debug=True)



# binance_two_coin_web 폴더의 two_coin.py 파일에 있는 코드와 차이점.
# 1.코드 재사용성 (Code Reusability): 위 코드의 방식은 각 암호화폐에 대한 웹소켓 처리 로직을 재사용하는 방식으로 작성되었습니다. 이러한 방식은 새로운 암호화폐를 추가하거나 수정할 때 매우 효율적입니다.

# 2.코드 길이와 가독성 (Code Length and Readability): 위 코드의 방식은 코드가 짧고 깔끔합니다. 새로운 암호화폐를 추가하려면 `cryptos` 리스트에만 심볼을 추가하면 됩니다.

# 3.유지보수 (Maintenance): 위 코드의 방식은 유지보수가 훨씬 쉽습니다. 웹소켓 처리 로직에 변경이 필요한 경우, 하나의 함수만 수정하면 됩니다.

