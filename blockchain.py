import datetime
import hashlib
import json
from flask import Flask, jsonify

class Blockchain:
    
    def __init__(self):
        self.chain = []
        # creating genesis block
        self.create_block(proof = 1, previous_hash = '0')
        
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_opertaion = hashlib.sha256(str(new_proof - previous_proof).encode()).hexdigest()
            if hash_opertaion[:4] == '0000':
                check_proof = True
            else:
                new_proof +=1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            # checking if chain is well connected
            if block['previous_hash'] != self.hash(previous_block):
                return False
            # checking if proofs are valid
            previous_proof = previous_block['proof']
            if hashlib.sha256(str(block['proof'] - previous_proof).encode()).hexdigest()[:4] != '0000':
                return False
            previous_block = block
            block_index+=1
        return True

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

blockchain = Blockchain()

# mining a new block
@app.route('/mine', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_block_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_block_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {
        'message': 'congrats! you just mined a block',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200
    
# getting the blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

# checking validity
@app.route('/check', methods = ['GET'])
def check():
    if blockchain.is_chain_valid(blockchain.chain):
        response_msg = "All good bro!"
    else:
        response_msg = "Blockchain is courrpted"
    response = {'validity': response_msg}
    
    return jsonify(response), 200