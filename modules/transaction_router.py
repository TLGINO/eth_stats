import json
import os
from datetime import datetime

import pandas as pd
import requests
import websockets


class APIWrapper:
    def __init__(self, rpc_endpoint):
        self.rpc_endpoint = f"https://{rpc_endpoint}"
        self.ws_endpoint = f"wss://{rpc_endpoint}"

    async def subscribe_to_new_blocks(self):
        async with websockets.connect(self.ws_endpoint) as websocket:
            subscription_payload = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "eth_subscribe",
                    "params": ["newHeads"],
                    "id": 1,
                }
            )
            await websocket.send(subscription_payload)

            print("Subscribed to new blocks.")

            while True:
                response = await websocket.recv()
                block_data = json.loads(response).get("params", {}).get("result", {})
                if block_data == {}:
                    continue

                # Functions to run
                self.get_withdrawal_data(block_data)
                self.get_block_transactions(block_data)

                # open("tmp.json", "w+").write(json.dumps(block_data))

    def execute_call(self, payload) -> json:
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            self.rpc_endpoint, headers=headers, data=json.dumps(payload)
        )

        if response.status_code == 200:
            result = response.json()["result"]
            return result

        raise Exception(f"Error: {response}")

    def custom_writer(self, path, data_df):
        f_path = f"data/{path}"
        data_df.insert(0, "datetime", f"'{datetime.now()}'")

        if os.path.exists(f_path):
            with open(f_path, "a") as f:
                data_df.to_csv(f, header=False, index=False)
        else:
            data_df.to_csv(f_path, index=False)

    def get_block_transactions(self, block_data):
        block_number = block_data["number"]
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBlockByNumber",
            "params": [block_number, True],
            "id": 1,
        }

        result = self.execute_call(payload)
        block_transactions = result["transactions"]

        # [TODO] check for IDM

        df = pd.DataFrame(block_transactions)

        # Write data
        self.custom_writer("block_transactions.csv", df)

    def get_withdrawal_data(self, block_data):
        withdrawals_data = block_data["withdrawals"]
        df = pd.DataFrame(withdrawals_data)

        # Write data
        self.custom_writer("withdrawals.csv", df)
