import yfinance as yf


stocks_data = {"SPY","QQQ","VXUS","IEF","BND","SHY","BTC","ETH"}

class yahoo:
    @staticmethod
    def fetch_stock_data(ticker_symbol):
        stock = yf.Ticker(ticker_symbol)
        current_price = stock.info.get("currentPrice")
        previous_close = stock.info.get("previousClose")
        company_name = stock.info.get("longName")
        historical_data_month = stock.history(period="1mo")
        return {
            "symbol": ticker_symbol,
            "current_price": current_price,
            "price": previous_close,
            "name": company_name,
        }

    @staticmethod
    def fetch_all_stock_data():
        print('Fetching all stock data...')
        results_data = []  # Create a new list each time to avoid appending to old results
        for ticker_symbol in stocks_data:
            try:
                stock_data = yahoo.fetch_stock_data(ticker_symbol)
                results_data.append(stock_data)
            except Exception as e:
                print(f"Error fetching data for {ticker_symbol}: {e}")
        return results_data
