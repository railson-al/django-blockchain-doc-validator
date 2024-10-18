from web3 import Web3
from django.conf import settings
import json
import os
import logging


# Configuração do logger
logger = logging.getLogger(__name__)

# Carregue as configurações do seu arquivo .env
INFURA_URL = settings.INFURA_URL
CONTRACT_ADDRESS = settings.CONTRACT_ADDRESS
WALLET_PRIVATE_KEY = settings.WALLET_PRIVATE_KEY


# Inicialize a conexão Web3
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

abi_path = os.path.join(settings.BASE_DIR, 'contracts', 'build', 'contracts', 'DocumentRegistry.json')
# Carregue o ABI do seu contrato
with open(abi_path, 'r') as abi_file:
    contract_json = json.load(abi_file)

# Inicialize o contrato
contract_abi = contract_json['abi']
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

def register_document(document_hash):
    """
    Registra um documento na blockchain.

    :param document_hash: O hash do documento a ser registrado (em formato hexadecimal)
    :return: O recibo da transação
    """

    try:
        # Converta o hash para bytes32
        document_hash_bytes = bytes.fromhex(document_hash[2:])  # Remove '0x' do início se presente
        # print(document_hash_bytes)

        nonce = w3.eth.get_transaction_count(w3.eth.account.from_key(WALLET_PRIVATE_KEY).address)
        txn = contract.functions.registerDocument(document_hash_bytes).build_transaction({
            'chainId': 4,  # 4 para Rinkeby, 1 para Mainnet
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        })

        signed_txn = w3.eth.account.sign_transaction(txn, private_key=WALLET_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return tx_receipt
    except Exception as e:
        logger.error(f"Erro ao registrar documento na blockchain: {e}")
        raise



def verify_document(document_hash):
    """
    Verifica se um documento está registrado na blockchain.
    
    :param document_hash: O hash do documento a ser verificado
    :return: True se o documento está registrado, False caso contrário
    """
    try:
        return contract.functions.verifyDocument(document_hash).call()
    except Exception as e:
        print(f"Erro ao verificar documento na blockchain: {e}")
        return False