import yfinance as yf


stocks_data = {"SPY","QQQ","VXUS","IEF","BND","SHY","BTC","ETH"}

class yahoo:
    @staticmethod
    def fetch_stock_data(ticker_symbol):
        try:
            stock = yf.Ticker(ticker_symbol)

            # Try to get current price from info first
            current_price = stock.info.get("currentPrice")
            previous_close = stock.info.get("previousClose")
            company_name = stock.info.get("longName")

            # If info doesn't have the data, try historical data as real fallback
            if current_price is None or previous_close is None:
                historical_data = stock.history(period="5d")
                if not historical_data.empty:
                    current_price = float(historical_data['Close'].iloc[-1]) if current_price is None else current_price
                    previous_close = float(historical_data['Close'].iloc[-2]) if len(historical_data) > 1 and previous_close is None else previous_close

            # If we still don't have data, raise an error - no fake data
            if current_price is None or previous_close is None:
                raise ValueError(f"Unable to fetch real market data for {ticker_symbol}")

            # Calculate change and percentage
            change = current_price - previous_close
            changeporcentual = (change / previous_close * 100) if previous_close != 0 else 0

            return {
                "symbol": ticker_symbol,
                "current_price": current_price,
                "price": previous_close,
                "name": company_name,
                "change": change,
                "changePercent": changeporcentual
            }

        except Exception as e:
            # Don't return fake data - let the calling code handle the error
            raise Exception(f"Failed to fetch real market data for {ticker_symbol}: {str(e)}")

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
