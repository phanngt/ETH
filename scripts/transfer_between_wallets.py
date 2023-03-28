from eth_account.signers.local import LocalAccount

from maintainer.base import BaseWeb3
from maintainer.singleton import Si
from scripts.block import block_confirmations

from storage.key_map import PRIVATE_KEY_MAP

LAYER_1_BASE_FEE = 0.002  # Estimate the base fee for layer 1 transactions


def transfer_all(sender: LocalAccount, receiver: LocalAccount):
    """
    Transfer all the balance from sender to receiver
    """
    # Build the transaction
    transaction = {
        'from': sender.address,
        'to': receiver.address,
        'value': 0,
        'gasPrice': Si(BaseWeb3).w3.eth.gas_price,
        'nonce': Si(BaseWeb3).w3.eth.get_transaction_count(sender.address),
        'chainId': 534353
    }
    estimated_gas = Si(BaseWeb3).w3.eth.estimate_gas(transaction)
    transaction['gas'] = estimated_gas

    # Calculate the maximum value that can be sent
    max_value = Si(BaseWeb3).w3.eth.get_balance(sender.address) - (estimated_gas * Si(BaseWeb3).w3.eth.gas_price)\
                - Si(BaseWeb3).w3.to_wei(LAYER_1_BASE_FEE, 'ether')
    transaction['value'] = max_value
    eth_amount = Si(BaseWeb3).w3.from_wei(max_value, 'ether')
    print(f"Transfer all balance from {sender.address} to {receiver.address} amount {eth_amount} ETH")
    # Sign the transaction
    signed_transaction = Si(BaseWeb3).w3.eth.account.sign_transaction(transaction, sender.key)
    # Send the transaction
    transaction_hash = Si(BaseWeb3).w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    # Wait for the transaction to be mined
    transaction_receipt = Si(BaseWeb3).w3.eth.wait_for_transaction_receipt(transaction_hash)
    print(f"Block Explorer: {Si(BaseWeb3).block_explorer}/tx/{transaction_hash.hex()}")
    block_confirmations(transaction_receipt)
    print(f"Transaction confirmed between {sender.address} and {receiver.address} amount"
          f" {eth_amount} ETH")


def transfer_between_accounts():
    """
    Manipulate the balance between multiple accounts
    """
    accounts = [Si(BaseWeb3).w3.eth.account.from_key(PRIVATE_KEY_MAP[key]) for key in PRIVATE_KEY_MAP.keys()]
    # Transfer order by order from the first account to the last account
    for i in range(len(accounts) - 1):
        transfer_all(accounts[i], accounts[i + 1])
    # Transfer back from the last account to the first account
    transfer_all(accounts[-1], accounts[0])


transfer_between_accounts()
