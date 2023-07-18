from django.shortcuts import render

import hashlib
import os
import time
import glob
from cryptography.fernet import Fernet
import json
import pandas as pd

# Create your views here.
from django.http import HttpResponse


def index(request):
    print(key)
    # create_blockchain(10)
    # if __name__ == '__main__':
    create_blockchain(15)
    # verify_blockchain()
    ChainDataFrame = get_blockchain_data()
    ChainDataFrame.columns = ['PID','AGE','SEX','GRP','OCC','CMB','HB1','COM']
    ChainDataFrame = json.loads(ChainDataFrame.to_json(orient='records'))
    # print(ChainDataFrame)

    if(verify_blockchain()):
        ChainStatusMessage = "Valid"
        return render(request,'index.html',{'CHAIN':ChainStatusMessage,'CDF':ChainDataFrame})
    else:
        ChainStatusMessage = "InValid"
        return render(request,'index.html',{'CHAIN':ChainStatusMessage})

# Generate a key for encryption and decryption
# WARNING: In real-world applications, you need to securely manage and store this key

key = Fernet.generate_key()
print(key)
cipher_suite = Fernet(key)

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash

def calculate_hash(index, previous_hash, timestamp, data):
    value = str(index) + str(previous_hash) + str(timestamp) + data
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def create_genesis_block():
    data = encrypt_data({
        "Participant ID": "0",
        "Age": "0",
        "Sex": "None",
        "Group": "None",
        "Occupation": "None",
        "Co Morbidity": "None",
        "Hemoglobin Level": "None",
        "Compliance": "None"
    })
    return Block(0, "0", int(time.time()), data, calculate_hash(0, "0", int(time.time()), data))

def create_new_block(previous_block, data):
    index = previous_block.index + 1
    timestamp = int(time.time())
    encrypted_data = encrypt_data(data)
    hash = calculate_hash(index, previous_block.hash, timestamp, encrypted_data)
    return Block(index, previous_block.hash, timestamp, encrypted_data, hash)

def encrypt_data(data):
    data_str = json.dumps(data)
    encrypted_data = cipher_suite.encrypt(data_str.encode('utf-8'))
    return encrypted_data.decode('utf-8')

def decrypt_data(encrypted_data):
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
    return json.loads(decrypted_data)

def save_block_to_file(block, folder='blocks'):
    os.makedirs(folder, exist_ok=True)
    data = [str(block.index), block.previous_hash, str(block.timestamp), block.data, block.hash]
    with open(f'{folder}/block_{block.index}.txt', 'w') as f:
        f.write('\n'.join(data))

def load_block_from_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.read().splitlines()
        return Block(int(lines[0]), lines[1], int(lines[2]), lines[3], lines[4])

def create_blockchain(num_blocks_to_add):
    blockchain = [create_genesis_block()]
    previous_block = blockchain[0]

    for i in range(1, num_blocks_to_add+1):
        block_to_add = create_new_block(previous_block, {
            "Participant ID": str(i),
            "Age": str(i*10),
            "Sex": "M" if i%2 == 0 else "F",
            "Group": "A" if i%2 == 0 else "B",
            "Occupation": f"Occupation {i}",
            "Co Morbidity": f"Co Morbidity {i}",
            "Hemoglobin Level": str(i*10),
            "Compliance": "Yes"
        })
        blockchain.append(block_to_add)
        previous_block = block_to_add
        print(f"Block #{block_to_add.index} has been added to the blockchain!")
        print(f"Hash: {block_to_add.hash}\n")
        save_block_to_file(block_to_add)

def verify_blockchain(folder='blocks'):
    block_files = sorted(glob.glob(f'{folder}/*.txt'), key=os.path.getmtime)
    previous_hash = None
    for block_file in block_files:
        block = load_block_from_file(block_file)
        decrypted_data = decrypt_data(block.data)
        block_hash = calculate_hash(block.index, block.previous_hash, block.timestamp, block.data)
        if previous_hash is not None and previous_hash != block.previous_hash:
            print(f"Invalid block #{block.index}.")
            return False
        if block_hash != block.hash:
            print(f"Invalid hash in block #{block.index}.")
            return False
        previous_hash = block.hash
    print("Blockchain is valid.")
    return True

def get_blockchain_data(folder='blocks'):
    block_files = sorted(glob.glob(f'{folder}/*.txt'), key=os.path.getmtime)
    blockchain_data = []
    for block_file in block_files:
        block = load_block_from_file(block_file)
        decrypted_data = decrypt_data(block.data)
        blockchain_data.append(decrypted_data)
    return pd.DataFrame(blockchain_data)

