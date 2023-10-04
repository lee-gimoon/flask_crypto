import websockets
import asyncio
import json
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__) # 이 부분은 Flask 웹 애플리케이션 인스턴스를 생성합니다. __name__ 변수는 현재 실행 중인 모듈의 이름을 나타냅니다. Flask는 이를 사용하여 어디에서 애플리케이션의 리소스를 찾아야 할지(예: 템플릿 디렉토리) 결정합니다.
socketio = SocketIO(app, cors_allowed_origins="*") 

async def upbit_client():
    uri = "wss://api.upbit.com/websocket/v1"

    async with websockets.connect(uri, ping_interval=60) as websocket: 

        subscribe = [{"ticket":"test"}, {"type":"trade", "codes":["KRW-BTC", "KRW-ETH", "KRW-XRP"], "isOnlyRealtime": True}, {"format":"SIMPLE"}]
        
        subscribe = json.dumps(subscribe) 
        await websocket.send(subscribe) 

        while True:
            data = await websocket.recv()
            data = json.loads(data) 
            coin_code = data.get("cd")  # 코인 코드 (예: KRW-BTC)

            if coin_code == "KRW-BTC":
                btc_pr = round(float(data['tp']))
                socketio.emit('btc_price_update', {'btc_price': btc_pr})
            elif coin_code == "KRW-ETH":
                eth_pr = round(float(data['tp']))
                socketio.emit('eth_price_update', {'eth_price': eth_pr})
            elif coin_code == "KRW-XRP":
                xrp_pr = round(float(data['tp']))
                socketio.emit('xrp_price_update', {'xrp_price': xrp_pr})



@app.route('/') # 데코레이터이기 때문에 index = app.route('/')(index) 와 같음. 즉, app.route('/')(index) 고차 함수가 호출된다는 말. (flask_doc폴더의 decorator파일 참조.)
def index():
    return render_template('index.html')

def start_binance_client():
    asyncio.run(upbit_client())

if __name__ == "__main__": # if __name__ == "__main__": 구문 아래에 있는 코드는 스크립트나 모듈이 직접 실행될 때만 실행되며, 다른 스크립트나 모듈에 의해 import될 때는 실행되지 않습니다.
    socketio.start_background_task(target=start_binance_client) # upbit 클라이언트를 백그라운드 작업으로 시작합니다.
    socketio.run(app, debug=True) # Flask 앱을 실행합니다.