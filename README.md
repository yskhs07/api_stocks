# Stock Data Scraper and P&L API

This FastAPI application provides two main functionalities:

1. Scrapes stock names and codes from Screener.in and returns a list of all available stocks.
2. Retrieves historical Profit & Loss (P&L) statements for a company using the Yahoo Finance API.

## Features

- **Stock Data Scraping**: Scrapes stock names and codes for NSE and BSE from Screener.in.
- **P&L Statements**: Fetches historical P&L data for a given stock symbol from Yahoo Finance.

## Endpoints

### 1. `/all_stocks`
- **Method**: `GET`
- **Description**: Scrapes and returns all stock names and their corresponding stock codes from Screener.in.
- **Response**: A list of stocks with the following format:
  ```json
  {
    "stocks": [
      {"name": "RELIANCE", "code": "RELIANCE"},
      {"name": "TCS", "code": "TCS"}
      ...
    ]
  }

### 1. `/pl_statement/{symbol}`
- **Method**: `GET`
- **Description**: Fetches historical P&L statements for a given stock symbol from Yahoo Finance.
- **Parameters**:
symbol: The stock symbol (e.g., RELIANCE.NS for NSE).
years (optional): Number of years of P&L data to fetch (default is 5 years).
- **Response**: A dictionary containing the P&L statement data, e.g.
```json
{
  "Revenue": {
    "2023": 1000000,
    "2022": 950000,
    ...
  },
  ...
}
```
### Prerequisites
**Python 3.7+**
Install the required Python packages:

```pip install -r requirements.txt```

1. Clone the repository
2. Install the dependencies:
```pip install -r requirements.txt```
3. Run the application:
```uvicorn app:app --reload```
4. Open your browser and navigate to http://127.0.0.1:8000/docs to access the interactive API documentation (powered by Swagger).

### Usage
- To get all available stocks:
```GET http://127.0.0.1:8000/all_stocks```

- To get the historical P&L statement for a stock (e.g., Reliance):

```GET http://127.0.0.1:8000/pl_statement/RELIANCE.NS?years=2```

