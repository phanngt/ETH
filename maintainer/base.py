# Connect to rpc and chain id
import json

from web3 import Web3
from web3.middleware import geth_poa_middleware

from maintainer.scroll_test_net import *


class BaseWeb3:
    """
    Testing for Scroll Testnet, will be changed to other testnet such as: Taiko, Linea, v.v...
    """
    def __init__(self, rpc: str = SCROLL_RPC, block_explorer: str = SCROLL_BLOCK_EXPLORER,
                 chain_id: str = SCROLL_CHAIN_ID):
        self.chain_id = chain_id
        self.w3 = Web3(Web3.HTTPProvider(rpc))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.block_explorer = block_explorer
        self.uniswapv3 = UniswapBase()


class UniswapBase:
    def __init__(self):
        with open(SCROLL_ABI_FILE, "r") as f:
            self.contract_abi = json.load(f).get("abi")
            self.contract_address = SCROLL_UNISWAP_V3_CONTRACT
            self.token0 = SCROLL_UNISWAP_V3_TOKEN_0
            self.token1 = SCROLL_UNISWAP_V3_TOKEN_1
