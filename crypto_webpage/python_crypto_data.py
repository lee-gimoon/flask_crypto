
import asyncio
from binance import AsyncClient, BinanceSocketManager
from flask import Flask, render_template
from flask_socketio import SocketIO # flask_socketio: Flask 애플리케이션에서 Socket.IO를 사용하기 위한 확장입니다.

app = Flask(__name__) # 이 부분은 Flask 웹 애플리케이션 인스턴스를 생성합니다. __name__ 변수는 현재 실행 중인 모듈의 이름을 나타냅니다. Flask는 이를 사용하여 어디에서 애플리케이션의 리소스를 찾아야 할지(예: 템플릿 디렉토리) 결정합니다.
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
            socketio.emit('btc_price_update', {'btc_price': price}) # 객체 {'price': price}가 클라이언트 측의 이벤트 리스너로 전달된다. 즉, 이 객체는 인자로써 클라이언트의 function(data) {...} 함수의 data 매개변수로 들어가게된다.

@app.route('/') # 데코레이터이기 때문에 index = app.route('/')(index) 와 같음. 즉, app.route('/')(index) 고차 함수가 호출된다는 말. (flask_doc폴더의 decorator파일 참조.)
def index():
    return render_template('index.html')

def start_binance_client():
    asyncio.run(binance_client())

if __name__ == "__main__": # if __name__ == "__main__": 구문 아래에 있는 코드는 스크립트나 모듈이 직접 실행될 때만 실행되며, 다른 스크립트나 모듈에 의해 import될 때는 실행되지 않습니다.
    socketio.start_background_task(target=start_binance_client) # Binance 클라이언트를 백그라운드 작업으로 시작합니다.
    socketio.run(app, debug=True) # Flask 앱을 실행합니다.


# __name__ 변수에 대한 이해:
# Python에서 스크립트나 모듈이 실행될 때, 그 스크립트나 모듈의 __name__이라는 내장 변수가 생성됩니다.
# 스크립트나 모듈이 직접 실행될 때 (예: python myscript.py), __name__ 변수는 "__main__"으로 설정됩니다.
# 반면, 어떤 모듈이 다른 스크립트나 모듈에 의해 import될 때, __name__ 변수는 해당 모듈의 이름으로 설정됩니다.