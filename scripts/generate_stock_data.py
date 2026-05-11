#!/usr/bin/env python3
import json
import math
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "stock-data.json"

FX_RATE = 1370

MARKET_GROUPS = [
    {
        "title": "한국 시장",
        "charts": [
            {"name": "KOSPI", "ticker": "^KS11", "color": "#4fc3f7"},
            {"name": "KOSDAQ", "ticker": "^KQ11", "color": "#81d4fa"},
        ],
    },
    {
        "title": "미국 시장",
        "charts": [
            {"name": "S&P500", "ticker": "^GSPC", "color": "#a5d6a7"},
            {"name": "NASDAQ", "ticker": "^IXIC", "color": "#c5e1a5"},
            {"name": "다우존스", "ticker": "^DJI", "color": "#fff59d"},
        ],
    },
    {
        "title": "공포지수",
        "charts": [
            {"name": "VIX", "ticker": "^VIX", "color": "#ef9a9a"},
        ],
    },
    {
        "title": "환율 / 금리",
        "charts": [
            {"name": "원달러환율", "ticker": "KRW=X", "color": "#ffcc80"},
            {"name": "엔화환율", "ticker": "JPYKRW=X", "color": "#80cbc4"},
            {"name": "미국10년금리", "ticker": "^TNX", "color": "#ce93d8"},
        ],
    },
]

HOLDINGS = [
    {
        "name": "삼성전자",
        "ticker": "005930.KS",
        "currency": "KRW",
        "qty": 18,
        "avgPrice": 72000,
        "news": [
            {"tone": "pos", "title": "AI 칩 수요 급증에 삼성 이익 급증", "source": "GuruFocus.com", "date": "04/30 19:04", "link": "https://finance.yahoo.com/sectors/technology/articles/samsung-profit-jumps-ai-chip-190453520.html"},
            {"tone": "", "title": "삼성전자 네이버 금융 종목뉴스", "source": "네이버 금융", "date": "최신", "link": "https://finance.naver.com/item/news.naver?code=005930"},
        ],
    },
    {
        "name": "SK하이닉스",
        "ticker": "000660.KS",
        "currency": "KRW",
        "qty": 7,
        "avgPrice": 184000,
        "news": [
            {"tone": "pos", "title": "한국 수출, AI 관련 수요 급증 지속", "source": "The Wall Street Journal", "date": "05/01 01:08", "link": "https://www.wsj.com/economy/trade/south-korea-exports-continue-to-surge-on-ai-related-demand-77c4d1fc?siteid=yhoof2&yptr=yahoo"},
            {"tone": "", "title": "SK하이닉스 네이버 금융 종목뉴스", "source": "네이버 금융", "date": "최신", "link": "https://finance.naver.com/item/news.naver?code=000660"},
        ],
    },
    {
        "name": "테슬라",
        "ticker": "TSLA",
        "currency": "USD",
        "qty": 4,
        "avgPrice": 214.5,
        "news": [
            {"tone": "pos", "title": "나스닥은 4월 랠리 이후 미국 증시 월간 상승세를 주도했습니다.", "source": "Yahoo Finance Video", "date": "04/30 20:15", "link": "https://finance.yahoo.com/video/nasdaq-leads-us-stocks-in-monthly-gains-following-april-rally-201531873.html"},
            {"tone": "", "title": "Bitcoin, ETH, XRP, DOGE, MSTR Cashtags가 X 웹에 게시", "source": "CoinGape", "date": "05/01 03:38", "link": "https://coingape.com/bitcoin-eth-xrp-doge-mstr-cashtags-go-live-on-x-web-musk-says-most-crypto-are-scams/"},
        ],
    },
    {
        "name": "알파벳A",
        "ticker": "GOOGL",
        "currency": "USD",
        "qty": 6,
        "avgPrice": 168.0,
        "news": [
            {"tone": "neg", "title": "투자자들이 Google과 Amazon의 경쟁 심화에 무게를 두면서 Nvidia 주가 하락", "source": "Yahoo Finance", "date": "04/30 15:18", "link": "https://finance.yahoo.com/markets/article/nvidia-stock-slips-as-investors-weigh-rising-competition-from-google-and-amazon-151839041.html"},
            {"tone": "", "title": "AI 수익 노다지는 투자자들을 분열시키고 있다", "source": "Yahoo Finance", "date": "04/30 15:22", "link": "https://finance.yahoo.com/sectors/technology/article/the-ai-earnings-bonanza-is-splitting-investors-152258508.html"},
            {"tone": "pos", "title": "1분기 실적, Google Cloud 성장으로 Alphabet 주가 상승", "source": "Yahoo Finance Video", "date": "04/30 13:34", "link": "https://finance.yahoo.com/video/alphabet-stock-gaining-on-q1-earnings-google-cloud-growth-133416304.html"},
        ],
    },
    {
        "name": "애플",
        "ticker": "AAPL",
        "currency": "USD",
        "qty": 5,
        "avgPrice": 185.0,
        "news": [
            {"tone": "pos", "title": "Apple rallies as oil prices cool", "source": "The Times of India", "date": "05/01", "link": "https://timesofindia.indiatimes.com/business/international-business/us-stock-markets-today-may-1-2026-wall-street-heads-for-fresh-records-apple-rallies-as-oil-prices-cool/articleshow/130680184.cms"},
            {"tone": "pos", "title": "Apple shares jump as Nasdaq scores record high", "source": "MarketWatch", "date": "05/01", "link": "https://www.marketwatch.com/livecoverage/s-p-500-nasdaq-record-closes-dow-jones-earnings-results-oil-climbs-little-sign-iran-war-ending"},
            {"tone": "pos", "title": "Apple shares rose over 3% in premarket trading", "source": "Investopedia", "date": "05/01", "link": "https://www.investopedia.com/5-things-to-know-before-the-stock-market-opens-may-1-2026-11963435"},
        ],
    },
    {
        "name": "네이버",
        "ticker": "035420.KS",
        "currency": "KRW",
        "qty": 6,
        "avgPrice": 205000,
        "news": [
            {"tone": "neg", "title": "Naver Posts Weaker First-Quarter Earnings", "source": "The Wall Street Journal", "date": "최근", "link": "https://www.wsj.com/business/earnings/naver-posts-weaker-first-quarter-earnings-1a3511ec"},
            {"tone": "pos", "title": "NAVER, LG CNS와 대규모 데이터센터 계약 체결로 4%대 강세 마감", "source": "재경일보", "date": "04/01", "link": "https://news.jkn.co.kr/post/862468"},
            {"tone": "", "title": "NAVER 네이버 금융 종목뉴스", "source": "네이버 금융", "date": "최신", "link": "https://finance.naver.com/item/news.naver?code=035420"},
        ],
    },
    {
        "name": "카카오",
        "ticker": "035720.KS",
        "currency": "KRW",
        "qty": 12,
        "avgPrice": 52000,
        "news": [
            {"tone": "", "title": "Kakao Corp. 주가 및 기업 개요", "source": "StockAnalysis", "date": "최근", "link": "https://stockanalysis.com/quote/krx/035720/"},
            {"tone": "pos", "title": "Kakao Corp. closed higher at ₩49,600", "source": "Marketlog", "date": "04/15", "link": "https://www.marketlog.com/ca/symbol/035720-xkrx"},
            {"tone": "", "title": "카카오 네이버 금융 종목뉴스", "source": "네이버 금융", "date": "최신", "link": "https://finance.naver.com/item/news.naver?code=035720"},
        ],
    },
]


def fetch_chart(ticker, range_value="6mo", interval="1d"):
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        + urllib.parse.quote(ticker)
        + f"?range={urllib.parse.quote(range_value)}&interval={urllib.parse.quote(interval)}"
    )
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json,text/plain,*/*"},
    )
    with urllib.request.urlopen(req, timeout=20) as res:
        payload = json.loads(res.read().decode("utf-8"))
    result = payload["chart"]["result"][0]
    meta = result["meta"]
    timestamps = result.get("timestamp", [])
    closes = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
    points = [(ts, close) for ts, close in zip(timestamps, closes) if isinstance(close, (int, float))]
    return meta, points


def moving_average(values, period):
    out = []
    for i in range(len(values)):
        if i + 1 < period:
            out.append(None)
        else:
            window = values[i + 1 - period : i + 1]
            out.append(sum(window) / period)
    return out


def rsi(values, period=14):
    if len(values) <= period:
        return 50
    gains = 0
    losses = 0
    for i in range(len(values) - period, len(values)):
        diff = values[i] - values[i - 1]
        if diff >= 0:
            gains += diff
        else:
            losses -= diff
    if losses == 0:
        return 100
    rs = gains / losses
    return 100 - (100 / (1 + rs))


def round_or_none(value, digits=4):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return round(float(value), digits)


def build_market():
    market_labels = []
    market_cards = []
    market_groups = []
    for group in MARKET_GROUPS:
        next_group = {"title": group["title"], "charts": []}
        for chart in group["charts"]:
            try:
                meta, points = fetch_chart(chart["ticker"])
                tail = points[-60:]
                labels = [datetime.fromtimestamp(ts).strftime("%m/%d") for ts, _ in tail]
                values = [round_or_none(close, 4) for _, close in tail]
                if len(labels) > len(market_labels):
                    market_labels = labels
                price = meta.get("regularMarketPrice") or values[-1]
                prev = meta.get("previousClose") or meta.get("chartPreviousClose") or (values[-2] if len(values) > 1 else price)
                change = ((price - prev) / prev * 100) if prev else 0
                market_cards.append({"name": chart["name"], "value": round_or_none(price, 2), "change": round_or_none(change, 2)})
                next_group["charts"].append({"name": chart["name"], "color": chart["color"], "values": values})
            except Exception as exc:
                print(f"market fetch failed: {chart['name']} {exc}")
        market_groups.append(next_group)
    return market_labels, market_cards, market_groups


def build_holdings():
    holdings = []
    for item in HOLDINGS:
        try:
            meta, points = fetch_chart(item["ticker"])
            tail = points[-60:]
            labels = [datetime.fromtimestamp(ts).strftime("%m/%d") for ts, _ in tail]
            prices = [float(close) for _, close in tail]
            ma20 = moving_average(prices, 20)
            ma60 = moving_average(prices, 60)
            price = meta.get("regularMarketPrice") or prices[-1]
            prev = meta.get("previousClose") or meta.get("chartPreviousClose") or (prices[-2] if len(prices) > 1 else price)
            day_change = ((price - prev) / prev * 100) if prev else 0
            stock = dict(item)
            stock.update(
                {
                    "currentPrice": round_or_none(price, 4),
                    "dayChange": round_or_none(day_change, 2),
                    "prices": [round_or_none(v, 4) for v in prices],
                    "labels": labels,
                    "ma20Series": [round_or_none(v, 4) for v in ma20],
                    "ma60Series": [round_or_none(v, 4) for v in ma60],
                    "ma20": round_or_none(next((v for v in reversed(ma20) if v is not None), price), 4),
                    "ma60": round_or_none(next((v for v in reversed(ma60) if v is not None), price), 4),
                    "rsi": round_or_none(rsi(prices), 1),
                }
            )
            holdings.append(stock)
        except Exception as exc:
            print(f"holding fetch failed: {item['ticker']} {exc}")
    return holdings


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    market_labels, market_cards, market_groups = build_market()
    payload = {
        "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fxRate": FX_RATE,
        "marketLabels": market_labels,
        "marketCards": market_cards,
        "marketGroups": market_groups,
        "holdings": build_holdings(),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
