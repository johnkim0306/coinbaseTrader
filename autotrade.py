import os
from openai import OpenAI
from coinbase.wallet.client import Client
from coinbase.rest import RESTClient
from dotenv import load_dotenv
import requests
import json
import pandas as pd
import pandas_ta as ta
import schedule
import time
import boto3
from io import BytesIO

load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#coinBaseclient = Client( os.getenv('API_KEY'), os.getenv('API_SECRET'))
coinBaseclient = RESTClient( os.getenv('API_KEY2'), os.getenv('API_SECRET2'))
# coinBaseclient = RESTClient(api_key=api_key, api_secret=api_secret)

s3 = boto3.client('s3')

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

        json_data = df.to_json(orient="records", date_format="iso")
        return json_data
    else:
        print(f"Error fetching data. Status code: {response.status_code}")
        return None

def get_accounts_info():
    print("inside get_accounts_info")
    accounts = coinBaseclient.get_accounts()
    print(accounts)

    try:
        json_data = json.dumps(accounts)
        return json_data
    except json.JSONDecodeError:
        print("Data is not in JSON format.")
        return None

def get_buy_price():
    hist_price = coinBaseclient.get_buy_price()
    try:
        json_data = json.dumps(hist_price)
        return json_data
    except json.JSONDecodeError:
        print("Data is not in JSON format.")
        return None

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
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": accounts},
                {"role": "user", "content": averagePrice},
                {"role": "user", "content": MarketIndicator},
            ],
        )
        print(response)
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in analyzing data with GPT-4: {e}")
        return None

def execute_buy():
    try:
        currency_code = 'BTC'
        print(currency_code)
        accounts = coinBaseclient.get_accounts()
        print(accounts)
        account = next(acc for acc in accounts if acc.currency.code == currency_code)
        balance = account.balance

        print(f"Balance for {currency_code}: {balance}")

        buy_response = coinBaseclient.buy(product_id=product_id, amount=amount, currency='USD')
        print("Buy order successful:", buy_response)
        return buy_response
    except Exception as e:
        print(f"Failed to execute buy order: {e}")
        return False

def execute_sell():
    try:
        currency_code = 'BTC'
        accounts = coinBaseclient.get_accounts()
        account = next(acc for acc in accounts if acc.currency.code == currency_code)
        balance = account.balance

        print(f"Balance for {currency_code}: {balance}")

        sell_response = coinBaseclient.sell(product_id=product_id, amount=amount, currency='USD')
        print("Sell order successful:", sell_response)
        return sell_response
    except Exception as e:
        print(f"Failed to execute sell order: {e}")
        return False

decision = 'buy'
def openaiTesting():
    # Message = fetch_and_prepare_data()
    # MarketIndicator = get_coinbase_market_data()
    # advice = analyze_data_with_gpt4(Message, MarketIndicator)
    global decision
    try:
        # decision = json.loads(advice)
        # print(decision)
        # print(decision.get('decision'))
        # if decision.get('decision') == "buy":
        #     execute_buy()
        # elif decision.get('decision') == "sell":
        #     execute_sell()
        accounts = get_accounts_info()
        # Upload a text string to S3
        text_content = accounts
        elapsed_time = time.time()
        file_obj = BytesIO(text_content.encode())
        s3.upload_fileobj(file_obj, 'cryptocurrencys3', f'information/{elapsed_time}Execution.txt')

        # print(accounts)
        if decision == 'buy':
            decision = 'sell'
        elif decision == 'sell':
            decision = 'buy'
        print(decision)

        # execute_buy()
    except Exception as e:
        print(f"Failed to parse the advice as JSON: {e}")


if __name__ == "__main__":
    openaiTesting()
    # schedule.every().hour.at(":01").do(openaiTesting)
    schedule.every(5).seconds.do(openaiTesting)

    while True:
        schedule.run_pending()
        time.sleep(1)
