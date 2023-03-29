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

    hex_data = "0x88316456000000000000000000000000a0d71b9877f44c744546d649147e3f1e70a93760000000000000000000000000a1ea0b2354f5a344110af2b6ad68e75545009a030000000000000000000000000000000000000000000000000000000000002710fffffffffffffffffffffffffffffffffffffffffffffffffffffffffff2766000000000000000000000000000000000000000000000000000000000000d89a000000000000000000000000000000000000000000000043c33c19375647f24bf0000000000000000000000000000000000000000000000000068fb9b5a2e0d880000000000000000000000000000000000000000000004398075432dafd869f30000000000000000000000000000000000000000000000000068b85568d3a298000000000000000000000000594c5ff3d638d3e4c2fac65113885cc324171647000000000000000000000000000000000000000000000000000000006424040c"
    function_input_0: BaseContractFunction = contract.decode_function_input(hex_data)
    abi_codec = ABICodec(default_registry)
    types = ("address", "address", "uint24", "int24", "int24", "uint256", "uint256", "uint256", "uint256", "address", "uint256")
    tuples = (Si(BaseWeb3).uniswapv3.token0, Si(BaseWeb3).uniswapv3.token1, 10000, -887200, 887200, 19999999999999999943871, 12560042229378440, 19950186722152658004467, 2560042229378440, sender_address, 1790081932)
    byte_data_0 = abi_codec.encode(types, tuples)
    byte_data_0 = HexBytes(hex_data)
    byte_data_1 = HexBytes("0x12210e8a")

    gas = contract.functions.multicall([byte_data_0, byte_data_1]).estimate_gas({'from': sender_address})
    tx_hash = contract.functions.multicall([byte_data_0, byte_data_1]).build_transaction(
        {
            'from': sender_address, "gas": gas, "gasPrice": gas_price, "nonce": nonce
        }
    )

    signed_tx = Si(BaseWeb3).w3.eth.account.sign_transaction(tx_hash, account.key)
    tx = Si(BaseWeb3).w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    print(f"Block Explorer: {Si(BaseWeb3).block_explorer}/tx/{tx.hex()}")
    block_confirmations(tx)
    print(f"Transaction confirmed between {sender_address}  amount")
