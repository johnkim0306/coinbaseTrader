import os
from openai import OpenAI
from coinbase.wallet.client import Client
from dotenv import load_dotenv
import requests
import json
load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
coinBaseclient = Client( os.getenv('API_KEY'), os.getenv('API_SECRET'))


def get_coinbase_market_data():
    # Define the API endpoint
    url = "https://api.pro.coinbase.com/products/BTC-USD/candles"

    # Set the parameters for the request
    params = {
        "granularity": 3600,  # 1-hour granularity
        "limit": 10  # Number of data points
    }

    # Make the API request
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract relevant columns (Open, High, Low, Close, Volume)
        columns = ["time", "open", "high", "low", "close", "volume"]
        market_data = [{col: row[i] for i, col in enumerate(columns)} for row in data]
        return market_data
    else:
        print(f"Error fetching data. Status code: {response.status_code}")
        return None

def get_accounts_info():
    accounts = coinBaseclient.get_accounts()
    print(accounts)
    return accounts

def get_buy_price():
    hist_price = coinBaseclient.get_buy_price()
    print(hist_price)
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

def analyze_data_with_gpt4(data_json):
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


        # current_status = get_current_status()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": accounts},
                {"role": "user", "content": averagePrice},
            ],
            # response_format={"type":"json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in analyzing data with GPT-4: {e}")
        return None

def openaiTesting():
    data_json = fetch_and_prepare_data()
    print(data_json)
    advice = analyze_data_with_gpt4(data_json)
    print(advice)
    print("swag")
    # print(advice)


if __name__ == "__main__":
    market_data = get_coinbase_market_data()
    if market_data:
        for entry in market_data:
            print(entry)
    else:
        print("Failed to fetch market data from Coinbase API.")
    # openaiTesting()
    # make_decision_and_execute()
    # schedule.every().hour.at(":01").do(make_decision_and_execute)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
