import time

from maintainer.base import BaseWeb3
from maintainer.singleton import Si


def block_confirmations(transaction_receipt: dict):
    # Block Explorer
    while True:
        print(f"Waiting for the block confirmation...")
        time.sleep(1)
        latest_block = Si(BaseWeb3).w3.eth.block_number
        tx_block = transaction_receipt.get("blockNumber")
        if latest_block - tx_block >= 1:
            break
