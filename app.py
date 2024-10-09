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


# Run the app with uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
