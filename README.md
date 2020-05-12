# Multiblockchain Wallet 



This script allows to manage multiblockchain transactions within command line. It was built on Python, ***hd-wallet-derive*** command tool, ***bit*** and ***web3*** Python libraries. I used ***Ganache*** to create a local Ethereuem network and pre-fund accounts. 

#### How to use: 

1. Open up a new terminal window inside of ***wallet folder***, then run ***python***. Within the Python shell, run `from wallet import *` -- you can now access the functions interactively.

   1. Derive wallets by calling ***derive_wallets*** with required parameters: ***mnemonic, coin, numderive***.
   2. Create account object by calling ***privKeyToAccount*** providing required ***coin*** and ***privkey***. 

2. To send a transaction run the following command in Python shell `sendTx(coin, account, recipient, amount)`:

   ![](https://github.com/karlmunchaussen/multiblockchainwallet/blob/master/images/1.png?raw=true) 

   1. [Ethereum transaction confirmation image](https://github.com/karlmunchaussen/multiblockchainwallet/blob/master/images/2.png?raw=true)
   2. [Bitcoin transaction confirmation image](https://github.com/karlmunchaussen/multiblockchainwallet/blob/master/images/3.png?raw=true)

#### List of functions:

* derive_wallets (use the subprocess library to call the php file script from Python):

```
def derive_wallets(mnemonic, coin, numderive):
    
    command = f'./derive -g --mnemonic="{mnemonic}" --cols=address,index,path,privkey,pubkey,pubkeyhash,xprv,xpub --coin=" {coin}" --numderive="{numderive}" --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    # Read data from standard output and err
    (output, err) = p.communicate()
    # This allows to wait for an output
    p_status = p.wait()
    keys = json.loads(output)
    
    return keys
```



* privKeyToAccount (convert the privkey string in a child key to an account object that bit or web3.py can use to transact):

  ```
  def privKeyToAccount(coin, privkey):
      
      if coin == BTCTEST:
          return PrivateKeyTestnet(privkey) 
      
      if coin == ETH:
          return Account.privateKeyToAccount(privkey)
  ```



* createTx (create the raw, unsigned transaction that contains all metadata needed to transact):

  ```
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
  ```



* sendTx (calls create_tx, signs the transaction, then sends it to the designated network): 

  ```
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
  ```

  
