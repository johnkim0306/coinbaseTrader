import os
from openai import OpenAI
from coinbase.wallet.client import Client
from dotenv import load_dotenv
import requests
import json
import pandas as pd
import pandas_ta as ta
load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
coinBaseclient = Client( os.getenv('API_KEY'), os.getenv('API_SECRET'))


def get_coinbase_market_data():
    url = "https://api.pro.coinbase.com/products/BTC-USD/candles"
    params = {
        "granularity": 3600,  
        "limit": 20
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
        df = df[::-1]
        # Convert timestamp to datetime
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Calculate SMA, RSI Bollinger Bands, EMA
        df['sma_10'] = ta.sma(df['close'], length=10)
        df['rsi_14'] = ta.rsi(df['close'], length=14)
        
        # Calculate Stochastic Oscillator (%K and %D)
        stoch_k, stoch_d = ta.stoch(high=df['high'], low=df['low'], close=df['close'])
        df['stoch_k'] = stoch_k
        df['stoch_d'] = stoch_d

        # Calculate Bollinger Bands (BBL, BBM, BBU)
        bbands = ta.bbands(close=df['close'])
        df['bbands_lower'] = bbands['BBL_5_2.0']
        df['bbands_middle'] = bbands['BBM_5_2.0']
        df['bbands_upper'] = bbands['BBU_5_2.0']

        # EMA
        df['ema'] = ta.ema(close=df['close'])

        # print(df.tail(15))
        return df
    else:
        print(f"Error fetching data. Status code: {response.status_code}")
        return None

def get_accounts_info():
    accounts = coinBaseclient.get_accounts()
    # print(accounts)
    return accounts

def get_buy_price():
    hist_price = coinBaseclient.get_buy_price()
    # print(hist_price)
    return hist_price

def fetch_and_prepare_data():
    combined_data = 'Do you recgonize this tell me if you understood what i sent you '
    return json.dumps(combined_data)

def get_instructions(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            instructions = file.read()
        return instructions
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred while reading the file:", e)

def analyze_data_with_gpt4(Message, MarketIndicator):
    print(Message)
    print(MarketIndicator)
    instructions_path = "instructions.md"
    try:
        instructions = get_instructions(instructions_path)
        if not instructions:
            print("No instructions found.")
            return None
        accounts = get_accounts_info()
        if not accounts:
            print("No averagePrice found.")
            return None
        averagePrice = get_buy_price()
        if not averagePrice:
            print("No averagePrice found.")
            return None

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": accounts},
                {"role": "user", "content": averagePrice},
                {"role": "user", "content": MarketIndicator},
            ],
            # response_format={"type":"json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in analyzing data with GPT-4: {e}")
        return None

def openaiTesting():
    Message = fetch_and_prepare_data()
    # print(Message)
    MarketIndicator = get_coinbase_market_data()
    if not MarketIndicator.empty:
        print("Market Indicator Received")
    else:
        print("Failed to fetch market data from Coinbase API.")
    advice = analyze_data_with_gpt4(Message, MarketIndicator)
    print(advice)
    print("swag")
    # print(advice)


if __name__ == "__main__":
    openaiTesting()
    # make_decision_and_execute()
    # schedule.every().hour.at(":01").do(make_decision_and_execute)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
