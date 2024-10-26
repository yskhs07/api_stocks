import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()

# Function to scrape stock names and codes from Screener
def scrape_stock_data():
    stock_data = []
    base_url = "https://www.screener.in/screens/71064/all-stocks/?page={}"
    
    for page in range(1, 11):  # Adjust the number of pages if needed
        response = requests.get(base_url.format(page))
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all the <a> tags that contain stock names and codes
        stock_links = soup.find_all('a', href=True, target='_blank')
        
        for link in stock_links:
            company_name = link.text.strip()  # The company name is the text of the link
            href = link['href']  # Get the href attribute
            
            # Extract the stock code from the href (either number or symbol)
            stock_code = href.split('/')[-2]  # This splits the URL and grabs the code
            
            # Append the stock data in the desired format
            stock_data.append({"name": company_name, "code": stock_code})
    
    return stock_data

# Endpoint to get stock symbols and codes for both NSE and BSE
@app.get("/all_stocks")
def get_all_stocks():
    try:
        stock_data = scrape_stock_data()
        if not stock_data:
            raise HTTPException(status_code=404, detail="No stock data found.")
        return {"stocks": stock_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
#for the second endpoint, we will use the yfinance library to fetch historical P&L statements for a company based on its stock symbol.    
@app.get("/pl_statement/{symbol}")
def get_pl_statement(symbol: str, years: int = 5):
    """
    Retrieve historical P&L statements for a company using Yahoo Finance.
    :param symbol: Stock symbol (e.g., RELIANCE.NS for NSE)
    :param years: Number of years for historical P&L data
    """
    try:
        # Fetch company data from Yahoo Finance
        stock = yf.Ticker(symbol)

        # Get financials (including P&L)
        financials = stock.financials

        # Limit to the number of years requested
        financials = financials.iloc[:, :years]

        # Replace NaN values with None to avoid JSON serialization errors
        financials = financials.replace({np.nan: None})

        # Convert to dictionary for JSON response
        return financials.to_dict()

    except Exception as e:
        return {"error": str(e)}


@app.get("/stock_data/{symbol}")
def get_financials(symbol: str):  
    """
    Retrieve various financial metrics for a company using Yahoo Finance.
    :param symbol: Stock symbol (e.g., RELIANCE.NS for NSE)
    """
    try:
        # Fetch company data from Yahoo Finance
        stock = yf.Ticker(symbol)

        # Fetch company market capitalization and current price
        market_cap = stock.info.get("marketCap", "N/A")
        current_price = stock.info.get("currentPrice", "N/A")
        industry = stock.info.get("industry", "N/A")

        # Fetch PE ratio and PEG ratio
        pe_ratio = stock.info.get("trailingPE")
        peg_ratio = stock.info.get("trailingPegRatio") if stock.info.get("trailingPegRatio") is not None else "N/A"

        #Fetch Company name
        company_name = stock.info.get("longName")

        # Get the highest price per share
        history = stock.history(period="2y")
        highest_price = history['High'].max() if not history.empty else "N/A"

        # Get quarterly financials
        quarterly_financials = stock.quarterly_financials
        quarterly_data = quarterly_financials.loc[['Gross Profit', 'Net Income']] if quarterly_financials is not None else pd.DataFrame()

        # Extract quarterly EPS, check if it's not None
        quarterly_eps = stock.quarterly_earnings[['Earnings Per Share']] if stock.quarterly_earnings is not None else pd.DataFrame()
        if not quarterly_eps.empty:
            quarterly_eps = quarterly_eps.rename(columns={'Earnings Per Share': 'EPS'})
        else:
            quarterly_eps = pd.DataFrame({'EPS': []})  # Create an empty DataFrame with the column name

        # Replace NaN values with None for JSON serialization
        quarterly_data = quarterly_data.replace({np.nan: None})
        quarterly_eps = quarterly_eps.replace({np.nan: None})

        # Get annual financials (last 5 years)
        annual_financials = stock.financials
        annual_data = annual_financials.loc[['Gross Profit', 'Net Income']].head(5)  # Get last 5 years

        # Replace NaN values with None for JSON serialization
        annual_data = annual_data.replace({np.nan: None})

        # Get all-time highest sales and profit
        all_time_high_sales = quarterly_financials.loc['Total Revenue'].max() if 'Total Revenue' in quarterly_financials.index else "N/A"
        all_time_high_profit = quarterly_financials.loc['Net Income'].max() if 'Net Income' in quarterly_financials.index else "N/A"

        # Prepare the response
        response = {
            "Company Name": company_name,
            "Industry": industry,
            "PE Ratio": pe_ratio,
            "PEG Ratio": peg_ratio,
            "Market Capitalization": market_cap,
            "Current Price": current_price,
            "Highest Price Per Share": highest_price,
            "Quarterly Financials": quarterly_data.to_dict(),
            "Quarterly EPS": quarterly_eps.to_dict(),
            "Annual Financials": annual_data.to_dict(),
            "All Time Highest Sales (Quarterly)": all_time_high_sales,
            "All Time Highest Profit (Quarterly)": all_time_high_profit
        }

        return response

    except Exception as e:
        return {"error": str(e)}
    

@app.get("/stock_history/{symbol}")
def get_stock_history(symbol: str, years: int = 5):
    """
    Retrieve historical P&L statements for a company using Yahoo Finance.
    :param symbol: Stock symbol (e.g., RELIANCE.NS for NSE)
    :param years: Number of years for historical P&L data
    """
    try:
        # Fetch company data from Yahoo Finance
        stock = yf.Ticker(symbol)

        # Return the structured response
        return stock.history(period="max").to_dict(),
    
    except Exception as e:
        # Return a detailed error message
        return {"error": str(e), "details": "An error occurred while fetching data."}
    

@app.get("/stock_fundamentals/{symbol}")
def get_stock_fundamentals(symbol: str, years: int = 5):
    """
    Retrieve historical P&L statements for a company using Yahoo Finance.
    :param symbol: Stock symbol (e.g., RELIANCE.NS for NSE)
    :param years: Number of years for historical P&L data
    """
    try:
        # Fetch company data from Yahoo Finance
        stock = yf.Ticker(symbol)

        # Return the structured response
        return stock.info,
    
    except Exception as e:
        # Return a detailed error message
        return {"error": str(e), "details": "An error occurred while fetching data."}
    

@app.get("/stock_financials/{symbol}")
def get_stock_financials(symbol: str, years: int = 5):
    """
    Retrieve historical P&L statements for a company using Yahoo Finance.
    :param symbol: Stock symbol (e.g., RELIANCE.NS for NSE)
    :param years: Number of years for historical P&L data
    """
    try:
        # Fetch company data from Yahoo Finance
        stock = yf.Ticker(symbol)

        financials = stock.financials.fillna(0).to_dict()  # Replace NaN with 0
        quarterly_financials = stock.quarterly_financials.fillna(0).to_dict()  # Replace NaN with 0

        data = {
            "financials": financials,
            "quarterly_financials": quarterly_financials,
        }
        
        # Return the structured response
        return data
    
    except Exception as e:
        # Return a detailed error message
        return {"error": str(e), "details": "An error occurred while fetching data."}
    

@app.get("/stock_all_data/{symbol}")
def get_stock_all_data(symbol: str, years: int = 5):
    """
    Retrieve historical P&L statements for a company using Yahoo Finance.
    :param symbol: Stock symbol (e.g., RELIANCE.NS for NSE)
    :param years: Number of years for historical P&L data
    """
    try:
        # Fetch company data from Yahoo Finance
        stock = yf.Ticker(symbol)

        financials = stock.financials.fillna(0).to_dict()  # Replace NaN with 0
        quarterly_financials = stock.quarterly_financials.fillna(0).to_dict()  # Replace NaN with 0

        data = {
            "info": stock.info,
            "history": stock.history(period="max").to_dict(),
            "financials": financials,
            "quarterly_financials": quarterly_financials,
        }
        
        # Return the structured response
        return data
    
    except Exception as e:
        # Return a detailed error message
        return {"error": str(e), "details": "An error occurred while fetching data."}
    

# Run the app with uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
