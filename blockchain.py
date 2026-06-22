import hashlib
import json
import time
from database import get_blockchain, add_block

class Block:
    def __init__(self, index, voter_id, candidate, timestamp, previous_hash, hash_val=None):
        self.index = index
        self.voter_id = voter_id
        self.candidate = candidate
        self.timestamp = str(timestamp)
        self.previous_hash = previous_hash
        self.hash = hash_val or self.calculate_hash()

    def calculate_hash(self):
        """Computes the SHA-256 hash of the block's content."""
        block_string = json.dumps({
            "index": self.index,
            "voter_id": self.voter_id,
            "candidate": self.candidate,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "voter_id": self.voter_id,
            "candidate": self.candidate,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


class Blockchain:
    def __init__(self):
        self.chain = []
        self.load_from_db()

    def load_from_db(self):
        """Loads the blockchain from the SQLite database, or creates genesis if empty."""
        db_chain = get_blockchain()
        if not db_chain:
            self.create_genesis_block()
        else:
            self.chain = []
            for b in db_chain:
                block = Block(
                    index=b['block_index'],
                    voter_id=b['voter_id'],
                    candidate=b['candidate'],
                    timestamp=b['timestamp'],
                    previous_hash=b['previous_hash'],
                    hash_val=b['hash']
                )
                self.chain.append(block)

    def create_genesis_block(self):
        """Generates the initial block in the blockchain ledger."""
        genesis = Block(
            index=0,
            voter_id="GENESIS_SYSTEM",
            candidate="GENESIS_SYSTEM",
            timestamp=str(int(time.time())),
            previous_hash="0"
        )
        # Persist Genesis Block to db
        add_block(
            block_index=genesis.index,
            voter_id=genesis.voter_id,
            candidate=genesis.candidate,
            timestamp=genesis.timestamp,
            previous_hash=genesis.previous_hash,
            hash_val=genesis.hash
        )
        self.chain.append(genesis)

    def get_latest_block(self):
        """Returns the most recent block in the chain."""
        self.load_from_db()  # Keep in sync with DB
        return self.chain[-1]

    def mint_block(self, voter_id, candidate):
        """Mints a new block with the transaction details and appends it to the DB and chain."""
        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            voter_id=voter_id,
            candidate=candidate,
            timestamp=str(int(time.time())),
            previous_hash=latest_block.hash
        )
        
        # Persist to SQLite
        success = add_block(
            block_index=new_block.index,
            voter_id=new_block.voter_id,
            candidate=new_block.candidate,
            timestamp=new_block.timestamp,
            previous_hash=new_block.previous_hash,
            hash_val=new_block.hash
        )
        
        if success:
            self.chain.append(new_block)
            return new_block
        else:
            raise Exception("Failed to append block to the database ledger.")

    def is_chain_valid(self):
        """Validates the blockchain integrity by verifying hashes and link integrity."""
        self.load_from_db()  # Refresh chain state
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            # 1. Re-verify the hash of the current block
            if current.hash != current.calculate_hash():
                return False
                
            # 2. Check if previous hash matches
            if current.previous_hash != previous.hash:
                return False
                
        return True
