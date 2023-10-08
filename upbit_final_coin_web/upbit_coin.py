import websockets
import asyncio
import json
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

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
                
            elif data['ty'] == 'ticker':
                scr = round(100*data['scr'], 2)
                atp24h = round(float(data['atp24h']))
                socketio.emit(f"{coin_code}_ticker", {"scr": scr, "atp24h": atp24h})

        
@app.route('/')
def index():
    return render_template('index.html')

def start_upbit_client():
    asyncio.run(upbit_client())

if __name__ == "__main__":
    socketio.start_background_task(target=start_upbit_client) # Flask 애플리케이션은 동기적으로 동작하기 때문에, 메인 스레드에서 asyncio.run()을 호출하면, 이벤트 루프가 해당 작업을 완료할 때까지 애플리케이션을 차단하게 됩니다.
    socketio.run(app, debug=True) # 따라서, Flask-SocketIO의 start_background_task()를 사용하여 별도의 스레드에서 백그라운드 작업을 실행하는 것이 권장됩니다.
                                                             
