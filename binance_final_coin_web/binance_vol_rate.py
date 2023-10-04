
# 한 종류의 코인(ticker)에 대한 거래량과 등락율을 실시간으로 받아오기 위한 코드.

import asyncio
from binance import AsyncClient, BinanceSocketManager

async def binance_client():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client, user_timeout=60)

    # 24시간 티커 데이터를 구독 (trade_socket이 아닌 symbol_ticker_socket을 써야 등락율과 볼륨을 얻을 수 있다.)
    ticker_socket = bm.symbol_ticker_socket('BTCUSDT') # https://python-binance.readthedocs.io/en/latest/binance.html#binance.websockets.BinanceSocketManager.symbol_ticker_socket 참조. (ctrl + F 하여 symbol_ticker_socket 검색후 확인.)

    async with ticker_socket as tsc:
        data = await tsc.recv()
        print(data)
        # 24시간 동안의 가격 변화 및 거래량 정보 추출
        price_change_percent = data['P']
        volume = data['v'] # 코인 개수 볼륨.
        usdt_volume = data['q'] # usdt 볼륨.
        
        print(f'24h Change Rate: {price_change_percent}%')
        print(f'24h Volume: {volume}')
        print(f'24h Usdt-Volume: {usdt_volume}')

    await client.close_connection()

# 웹소켓 클라이언트 시작 함수
def start_binance_client():
    asyncio.run(binance_client())

if __name__ == "__main__":
    start_binance_client()
