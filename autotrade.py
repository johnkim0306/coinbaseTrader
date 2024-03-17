import os
from openai import OpenAI
from coinbase.wallet.client import Client
from dotenv import load_dotenv
import json
load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
coinBaseclient = Client( os.getenv('API_KEY'), os.getenv('API_SECRET'))

accounts = coinBaseclient.get_accounts()
for account in accounts:
    print('Account balance:', account.balance.amount, account.balance.currency)

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

        # current_status = get_current_status()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello my name is John how are you?"},
                # {"role": "user", "content": current_status}
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
    openaiTesting()
    # make_decision_and_execute()
    # schedule.every().hour.at(":01").do(make_decision_and_execute)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
