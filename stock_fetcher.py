# stock_fetcher.py - Enhanced Version for Detailed Data Collection

import yfinance as yf
import finnhub
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --- Initialization ---
# Load environment variables from .env file
load_dotenv() 

# Initialize Finnhub client with your API key
try:
    finnhub_client = finnhub.Client(api_key=os.environ.get("FINNHUB_API_KEY"))
    if not os.environ.get("FINNHUB_API_KEY"):
        print("Warning: FINNHUB_API_KEY not found. News and some profile data will be unavailable.")
except Exception as e:
    print(f"Error initializing Finnhub client: {e}")
    finnhub_client = None

def fetch_detailed_stock_data(symbol):
    """
    Fetches a comprehensive set of data for a given stock symbol
    from both yfinance and Finnhub to provide rich context for an LLM.
    """
    print(f"Fetching detailed data for {symbol}...")
    
    try:
        # --- yfinance Data Fetching ---
        ticker = yf.Ticker(symbol)
        info = ticker.info # This is the primary source of yfinance data

        # Gracefully handle missing data using .get() with a default value
        
        # 1. Core Profile & Quote Data
        profile_data = {
            "companyName": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "country": info.get("country"),
            "website": info.get("website"),
            "longBusinessSummary": info.get("longBusinessSummary"),
            "marketCap": info.get("marketCap"),
            "sharesOutstanding": info.get("sharesOutstanding"),
        }
        
        quote_data = {
            "currentPrice": info.get("currentPrice"),
            "previousClose": info.get("previousClose"),
            "open": info.get("open"),
            "dayHigh": info.get("dayHigh"),
            "dayLow": info.get("dayLow"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "volume": info.get("volume"),
            "averageVolume": info.get("averageVolume"),
        }

        # 2. Key Financial Ratios (The 'Vitals' of the Company)
        financial_ratios = {
            "peRatio": info.get("trailingPE"),
            "forwardPeRatio": info.get("forwardPE"),
            "priceToBook": info.get("priceToBook"),
            "priceToSales": info.get("priceToSalesTrailing12Months"),
            "dividendYield": info.get("dividendYield"),
            "earningsGrowth": info.get("earningsQuarterlyGrowth"),
            "revenueGrowth": info.get("revenueQuarterlyGrowth"),
            "returnOnEquity": info.get("returnOnEquity"),
            "debtToEquity": info.get("debtToEquity"),
            "profitMargins": info.get("profitMargins"),
        }
        
        # 3. Analyst Ratings from yfinance
        analyst_ratings = {
            "recommendation": info.get("recommendationKey", "N/A").upper(),
            "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions"),
        }

        # --- Finnhub Data Fetching (for real-time news and complementary data) ---
        finnhub_news = []
        if finnhub_client:
            try:
                today = datetime.now()
                one_week_ago = today - timedelta(days=7)
                news_list = finnhub_client.company_news(symbol, _from=one_week_ago.strftime('%Y-%m-%d'), to=today.strftime('%Y-%m-%d'))
                finnhub_news = [{"headline": item['headline'], "source": item['source'], "url": item['url']} for item in news_list[:5]]
            except Exception as e:
                print(f"Could not fetch news from Finnhub for {symbol}: {e}")
                finnhub_news = [{"headline": "News data unavailable.", "source": "", "url": ""}]

        # --- Consolidate all data into a single structured dictionary ---
        consolidated_data = {
            "symbol": symbol,
            "fetchTimestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "profile": profile_data,
            "quote": quote_data,
            "financialRatios": financial_ratios,
            "analystRatings": analyst_ratings,
            "news": finnhub_news,
        }
        
        print("Data fetching complete.")
        return consolidated_data

    except Exception as e:
        print(f"An error occurred while fetching data for {symbol}: {e}")
        return {"error": f"Could not retrieve data for symbol {symbol}. It may be an invalid ticker."}

# Example of how to run this for testing
if __name__ == "__main__":
    import json
    detailed_data = fetch_detailed_stock_data("RELIANCE.NS")
    # Use json.dumps for pretty printing the dictionary
    print(json.dumps(detailed_data, indent=2))
