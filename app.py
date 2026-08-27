from flask import Flask, jsonify
import os
import requests
import json

app = Flask(__name__)

# List of public RPC endpoints for Base mainnet (fallbacks)
RPC_ENDPOINTS = [
    os.getenv('BASE_RPC_URL_1', 'https://base.blockpi.network/v1/rpc/public'),
    os.getenv('BASE_RPC_URL_2', 'https://base.meowrpc.com'),
    os.getenv('BASE_RPC_URL_3', 'https://base.llamarpc.com')
]

def fetch_gas_price():
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_gasPrice",
        "params": [],
        "id": 1
    }
    headers = {"Content-Type": "application/json"}
    for url in RPC_ENDPOINTS:
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                if 'result' in result:
                    # Handle hex string with or without 0x prefix
                    gas_price_wei = int(result['result'], 0)
                    gas_price_gwei = gas_price_wei / 1e9
                    return gas_price_gwei
        except Exception as e:
            # try next endpoint
            continue
    raise Exception("All RPC endpoints failed")

@app.route('/gas-price', methods=['GET'])
def gas_price():
    try:
        price = fetch_gas_price()
        return jsonify({"gas_price_gwei": price})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)