# trade_socket으로 가격을 symbol_ticker_socket으로는 등락율과 볼륨을 가져오기. (symbol_ticker_socket으로도 가격을 가져올 수 있으나 trade_socket이 조금 더 빠름.)

import asyncio
from binance import AsyncClient, BinanceSocketManager

async def handle_trade_socket(ts):
    async with ts:
        while True:
            trade_data = await ts.recv()
            print(f"Trade Price: {float(trade_data['p'])}")

async def handle_ticker_socket(ts):
    async with ts:
        while True:
            ticker_data = await ts.recv()
            print(f"24h Change Rate: {float(ticker_data['P'])}%")
            print(f"24h Volume: {round(float(ticker_data['q'])): ,}usdt")

async def binance_client():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client, user_timeout=60)

    trade_socket = bm.trade_socket('BTCUSDT')
    ticker_socket = bm.symbol_ticker_socket('BTCUSDT')

    # 두 개의 태스크를 동시에 실행
    await asyncio.gather(handle_trade_socket(trade_socket), handle_ticker_socket(ticker_socket))

def start_binance_client():
    asyncio.run(binance_client())

if __name__ == "__main__":
    start_binance_client()