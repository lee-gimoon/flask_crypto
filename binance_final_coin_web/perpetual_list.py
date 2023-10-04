# 바이낸스 거래소의 futures에서 perpetual(무기한) 계약의 usdt거래쌍 코인들 분석.

from binance.client import Client

client = Client()  # 공개 API 사용

def get_top_n_symbols_by_quote_volume(): # 상위 거래량 순으로 심볼 출력.
    # 모든 퍼페츄얼 계약의 티커 정보를 가져옴
    tickers = client.futures_ticker()
    print(tickers) # 티커에 대한 params을 알고 싶으면 한번 확인해봐라.

    # 24시간 quoteVolume을 기준으로 내림차순 정렬
    sorted_tickers = sorted(tickers, key = lambda x: float(x['quoteVolume']), reverse=True) # 람다함수에서 x를 매개변수라 생각하고 float(x~)를 return 값이라 생각하고 key 에 return값을 대입한다고 생각하면 됨.
    
    # 상위 5개의 symbol만 추출
    top_5_symbols = [ticker['symbol'] for ticker in sorted_tickers[:5]]
    
    return top_5_symbols

if __name__ == '__main__':
    top_5 = get_top_n_symbols_by_quote_volume()
    print("Top 5 symbols by 24h quote volume:")
    for symbol in top_5:
        print(symbol)
