import datetime
import logging
import eth_abi
from eth_abi.codec import ABICodec
from eth_abi.registry import (
    registry as default_registry,
)

from eth_account.signers.local import LocalAccount
from hexbytes import HexBytes
from web3._utils.abi import get_abi_input_types
from web3.contract.base_contract import BaseContractFunction

from maintainer.base import BaseWeb3
from maintainer.singleton import Si
from scripts.block import block_confirmations
from scripts.transfer_between_wallets import LAYER_1_BASE_FEE
from storage.key_map import PRIVATE_KEY_MAP


def swap_multiple_accounts():
    """
    Manipulate swaps between multiple accounts
    """
    accounts = [Si(BaseWeb3).w3.eth.account.from_key(PRIVATE_KEY_MAP[key]) for key in PRIVATE_KEY_MAP.keys()]
    # Loop each account, swap eth to usd token and swap usd token to eth
    for account in accounts:
        swap_uniswap_eth_to_usdc(account)


def swap_uniswap_eth_to_usdc(account: LocalAccount):
    """
    Swap eth to usdc
    """
    sender_address = account.address
    logging.info(f"Swap eth to usdc for account {sender_address}")

    nonce = Si(BaseWeb3).w3.eth.get_transaction_count(sender_address)
    gas_price = Si(BaseWeb3).w3.eth.gas_price

    contract = Si(BaseWeb3).w3.eth.contract(address=Si(BaseWeb3).uniswapv3.contract_address,
                                            abi=Si(BaseWeb3).uniswapv3.contract_abi)
    abi_codec = ABICodec(default_registry)

    dt_object = datetime.datetime.fromtimestamp(1680257528)
    print("Date and time:", dt_object)

    hex_data = "0x04e45aaf000000000000000000000000a1ea0b2354f5a344110af2b6ad68e75545009a03000000000000000000000000a0d71b9877f44c744546d649147e3f1e70a9376000000000000000000000000000000000000000000000000000000000000001f40000000000000000000000006cc03ab1abf2004b3705e76b2e7af75ad834f573000000000000000000000000000000000000000000000000002386f26fc100000000000000000000000000000000000000000000000001380417003c599a86ab0000000000000000000000000000000000000000000000000000000000000000"
    function_input_0: BaseContractFunction = contract.decode_function_input(hex_data)
    data = HexBytes(hex_data)
    types = get_abi_input_types(function_input_0[0].abi)
    types = types[0].strip('()').split(',')

    tuples = (Si(BaseWeb3).uniswapv3.token1.lower(), Si(BaseWeb3).uniswapv3.token0.lower(), 500, sender_address.lower(), 10000000000000000, 521154785582746276349, 0)
    byte_data = data[:4] + abi_codec.encode(types, tuples)

    # get_function_params = contract.encodeABI(fn_name=function_input_0[0].fn_name, args=list(tuples))

    # Convert byte data to hex
    # hex_data = "0x" + byte_data.hex()
    # function_input_1: BaseContractFunction = contract.decode_function_input(hex_data)
    hex_data = HexBytes(hex_data)

    gas = contract.functions.multicall(1780259385, [hex_data]).estimate_gas({'from': sender_address})
    tx_hash = contract.functions.multicall([byte_data, byte_data]).build_transaction(
        {
            'from': sender_address, "gas": gas, "gasPrice": gas_price, "nonce": nonce
        }
    )

    signed_tx = Si(BaseWeb3).w3.eth.account.sign_transaction(tx_hash, account.key)
    tx = Si(BaseWeb3).w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    print(f"Block Explorer: {Si(BaseWeb3).block_explorer}/tx/{tx.hex()}")
    block_confirmations(tx)
    print(f"Transaction confirmed between {sender_address}  amount")
