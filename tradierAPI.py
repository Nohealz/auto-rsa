# Nelson Dane
# Tradier API

import os
import sys
import requests
from time import sleep
from dotenv import load_dotenv

def tradier_init():
    # Initialize .env file
    load_dotenv()
    # Import Tradier account
    if not os.getenv("TRADIER_ACCESS_TOKEN"):
        print("Tradier not found, skipping...")
        return None
    # Get access token
    BEARER = os.environ["TRADIER_ACCESS_TOKEN"]
    # Log in to Tradier account
    print("Logging in to Tradier...")
    try:
        response = requests.get('https://api.tradier.com/v1/user/profile',
        params={},
        headers={'Authorization': f'Bearer {BEARER}', 'Accept': 'application/json'}
        )
        json_response = response.json()
        if json_response is None:
            raise Exception("Error: Tradier API returned None")
    except Exception as e:
        print(f'Error logging in to Tradier: {e}')
        return None
    # Print number of accounts found
    print(f"Tradier accounts found: {len(json_response['profile']['account'])}")
    # Print account numbers
    tradier_accounts = []
    for x in range(len(json_response['profile']['account'])):
        print(f"{json_response['profile']['account'][x]['account_number']}")
        tradier_accounts.append(json_response['profile']['account'][x]['account_number'])
    print("Logged in to Tradier!")
    return tradier_accounts

async def tradier_holdings(tradier, ctx=None):
    print()
    print("==============================")
    print("Tradier")
    print("==============================")
    print()
    # Initialize .env file
    load_dotenv()
    BEARER = os.getenv("TRADIER_ACCESS_TOKEN", None)
    # Make sure init didn't return None
    if tradier is None or BEARER is None:
        print("Error: No Tradier account")
        return None
    # Loop through accounts
    for account_number in tradier:
        try:
            # Get holdings from API
            response = requests.get(f'https://api.tradier.com/v1/accounts/{account_number}/positions',
                params={},
                headers={'Authorization': f'Bearer {BEARER}', 'Accept': 'application/json'}
            )
            # Convert to JSON
            json_response = response.json()
            if json_response['positions'] == 'null':
                print(f"No holdings on Tradier account {account_number}")
                if ctx:
                    await ctx.send(f"No holdings on Tradier account {account_number}")
                continue
            # Create list of holdings
            stocks = []
            for stock in json_response['positions']['position']:
                stocks.append(stock['symbol'])
            # Create list of amounts
            amounts = []
            for amount in json_response['positions']['position']:
                amounts.append(amount['quantity'])
            # Get current price of each stock
            current_price = []
            for sym in stocks:
                response = requests.get('https://api.tradier.com/v1/markets/quotes',
                    params={'symbols': sym, 'greeks': 'false'},
                    headers={'Authorization': f'Bearer {BEARER}', 'Accept': 'application/json'}
                )
                json_response = response.json()
                current_price.append(json_response['quotes']['quote']['last'])
            # Current value for position
            current_value = []
            for value in stocks:
                # Set index for easy use
                i = stocks.index(value)
                current_value.append(amounts[i] * current_price[i])
            # Print and send them
            print(f"Holdings on Tradier account {account_number}")
            if ctx:
                await ctx.send(f"Holdings on Tradier account {account_number}")
            for position in stocks:
                # Set index for easy use
                i = stocks.index(position)
                print(f"{position}: {amounts[i]} @ ${current_price[i]} = ${current_value[i]}")
                if ctx:
                    await ctx.send(f"{position}: ${amounts[i]} @ {current_price[i]} = ${current_value[i]}")
        except Exception as e:
            print(f"Error getting Tradier holdings in account {account_number}: {e}")
            if ctx:
                await ctx.send(f"Error getting Trader holdings in account {account_number}: {e}")

async def tradier_transaction(tradier, action, stock, amount, price, time, DRY=True, ctx=None):
    print()
    print("==============================")
    print("Tradier")
    print("==============================")
    print()
    action = action.lower()
    stock = stock.upper()
    amount = int(amount)
    BEARER = os.environ["TRADIER_ACCESS_TOKEN"]
    # Make sure init didn't return None
    if tradier is None:
        print("Error: No Tradier account")
        return None
    # Loop through accounts
    for account_number in tradier:
        if not DRY:
            response = requests.post(f'https://api.tradier.com/v1/accounts/{account_number}/orders',
            data={'class': 'equity', 'symbol': stock, 'side': action, 'quantity': amount, 'type': 'market', 'duration': 'day'},
            headers={'Authorization': f'Bearer {BEARER}', 'Accept': 'application/json'}
            )
            json_response = response.json()
            #print(response.status_code)
            #print(json_response)
            if json_response['order']['status'] == "ok":
                print(f"{action} {amount} of {stock} on Tradier account {account_number}")
                if ctx:
                    await ctx.send(f"{action} {amount} of {stock} on Tradier account {account_number}")
            else:
                print(f"Error: {json_response['order']['status']}")
                if ctx:
                    await ctx.send(f"Error: {json_response['order']['status']}")
                return None
        else:
            print(f"Running in DRY mode. Trasaction would've been: {action} {amount} of {stock} on Tradier account {account_number}")
            if ctx:
                await ctx.send(f"Running in DRY mode. Trasaction would've been: {action} {amount} of {stock} on Tradier account {account_number}")