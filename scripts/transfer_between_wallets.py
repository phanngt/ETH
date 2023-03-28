import time

from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.middleware import geth_poa_middleware
from storage.key_map import PRIVATE_KEY_MAP

SCROLL_RPC = "https://alpha-rpc.scroll.io/l2"
SCROLL_BLOCK_EXPLORER = "https://blockscout.scroll.io"
# Connect to rpc and chain id
w3 = Web3(Web3.HTTPProvider(SCROLL_RPC))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

LAYER_1_BASE_FEE = 0.001  # Estimate the base fee for layer 1 transactions


def transfer_all(sender: LocalAccount, receiver: LocalAccount):
    """
    Transfer all the balance from sender to receiver
    """
    # Build the transaction
    transaction = {
        'from': sender.address,
        'to': receiver.address,
        'value': 0,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(sender.address),
        'chainId': 534353
    }
    estimated_gas = w3.eth.estimate_gas(transaction)
    transaction['gas'] = estimated_gas

    # Calculate the maximum value that can be sent
    max_value = w3.eth.get_balance(sender.address) - (estimated_gas * w3.eth.gas_price) - w3.to_wei(LAYER_1_BASE_FEE,
                                                                                                    'ether')
    transaction['value'] = max_value
    eth_amount = w3.from_wei(max_value, 'ether')
    print(f"Transfer all balance from {sender.address} to {receiver.address} amount {eth_amount} ETH")
    # Sign the transaction
    signed_transaction = w3.eth.account.sign_transaction(transaction, sender.key)
    # Send the transaction
    transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    # Wait for the transaction to be mined
    transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    # Block Explorer
    print(f"Block Explorer: {SCROLL_BLOCK_EXPLORER}/tx/{transaction_hash.hex()}")
    while True:
        print(f"Waiting for the block confirmation...")
        time.sleep(1)
        latest_block = w3.eth.block_number
        tx_block = transaction_receipt.get("blockNumber")
        if latest_block - tx_block >= 1:
            break
    print(f"Transaction confirmed on block {latest_block} between {sender.address} and {receiver.address} amount"
          f" {eth_amount} ETH")


def transfer_between_accounts():
    """
    Manipulate the balance between multiple accounts
    """
    accounts = [w3.eth.account.from_key(PRIVATE_KEY_MAP[key]) for key in PRIVATE_KEY_MAP.keys()]
    # Transfer order by order from the first account to the last account
    for i in range(len(accounts) - 1):
        transfer_all(accounts[i], accounts[i + 1])
    # Transfer back from the last account to the first account
    transfer_all(accounts[-1], accounts[0])


transfer_between_accounts()
