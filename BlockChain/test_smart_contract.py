from blockchain import Blockchain
from smart_contract import SmartContractExecutor, TokenContract

def main():
    # Initialize blockchain
    blockchain = Blockchain()
    
    # Create contract executor
    executor = SmartContractExecutor(blockchain)
    
    # Deploy token contract
    token_code = """
class Token:
    def transfer(self, from_addr, to_addr, amount):
        if self.state['balances'].get(from_addr, 0) >= amount:
            self.state['balances'][from_addr] = self.state['balances'].get(from_addr, 0) - amount
            self.state['balances'][to_addr] = self.state['balances'].get(to_addr, 0) + amount
            return True
        return False
    """
    
    contract_address = executor.deploy_contract(token_code, "owner_address")
    print(f"Contract deployed at: {contract_address}")
    
    # Execute contract methods
    result = executor.execute_contract(
        contract_address,
        "transfer",
        {"from_addr": "Alice", "to_addr": "Bob", "amount": 100}
    )
    print(f"Transfer result: {result}")

if __name__ == "__main__":
    main() 