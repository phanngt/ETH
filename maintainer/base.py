# Connect to rpc and chain id
from web3 import Web3
from web3.middleware import geth_poa_middleware

from maintainer.scroll_test_net import SCROLL_RPC, SCROLL_BLOCK_EXPLORER


class BaseWeb3:
    def __init__(self, rpc: str = SCROLL_RPC, block_explorer: str = SCROLL_BLOCK_EXPLORER):
        self.w3 = Web3(Web3.HTTPProvider(rpc))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.block_explorer = block_explorer
