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
        subscribe = [{"ticket": "test"}, {"type": "trade", "codes": ["KRW-BTC", "KRW-ETH", "KRW-XRP"], "isOnlyRealtime": True}, {"format": "SIMPLE"}]
        subscribe = json.dumps(subscribe)
        await websocket.send(subscribe)

        while True:
            data = await websocket.recv()
            data = json.loads(data)
            coin_code = data.get("cd") # 'cd': 'KRW-BTC' or 'cd': 'KRW-ETH' .....
            price = round(float(data['tp']))
            if coin_code:
                socketio.emit(coin_code, {coin_code: price})

@app.route('/')
def index():
    return render_template('index.html')

def start_upbit_client():
    asyncio.run(upbit_client())

if __name__ == "__main__":
    socketio.start_background_task(target=start_upbit_client)
    socketio.run(app, debug=True)
