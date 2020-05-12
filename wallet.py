from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from bit import wif_to_key, PrivateKeyTestnet, PrivateKey, Key
from bit.network import NetworkAPI
import os
import json
import subprocess
from constants import *




# Instantiate Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8100"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
# Import mnemonic
mnemonic = os.getenv('MNEMONIC')

# Use the subprocess library to call the php file script from Python
def derive_wallets(mnemonic, coin, numderive):
    
    command = f'./derive -g --mnemonic="{mnemonic}" --cols=address,index,path,privkey,pubkey,pubkeyhash,xprv,xpub --coin=" {coin}" --numderive="{numderive}" --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    # Read data from standard output and err
    (output, err) = p.communicate()
    # This allows to wait for an output
    p_status = p.wait()
    keys = json.loads(output)
    
    return keys

# Convert the privkey string in a child key to an account object that bit or web3.py can use to transact
def privKeyToAccount(coin, privkey):
    
    if coin == BTCTEST:
        return PrivateKeyTestnet(privkey) 
    
    if coin == ETH:
        return Account.privateKeyToAccount(privkey)
    
# Create the raw, unsigned transaction that contains all metadata needed to transact
def createTx(coin, account, recipient, amount):
    
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])
    
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": recipient, "value": amount})
        return {
            "to": recipient,
            "from": account.address,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address)
        }
    
# This will call create_tx, sign the transaction, then send it to the designated network
def sendTx(coin, account, recipient, amount):

    Tx = createTx(coin, account, recipient, amount)
    
    if coin == BTCTEST:
        
        TxSigned = account.sign_transaction(Tx)
        NetworkAPI.broadcast_tx_testnet(TxSigned)       
        
        return TxSigned
    
    elif coin == ETH:
        
        TxSigned = account.signTransaction(Tx)
        result = w3.eth.sendRawTransaction(TxSigned.rawTransaction)
        
        return result.hex()