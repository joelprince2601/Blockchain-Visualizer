from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SmartContract:
    address: str
    code: str
    state: Dict[str, Any]
    owner: str
    created_at: datetime = datetime.utcnow()

class SmartContractExecutor:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.contracts: Dict[str, SmartContract] = {}
        
    def deploy_contract(self, code: str, owner: str) -> str:
        """Deploy a new smart contract"""
        # Generate contract address
        contract_address = self._generate_contract_address(code, owner)
        
        # Create new contract instance
        contract = SmartContract(
            address=contract_address,
            code=code,
            state={},
            owner=owner
        )
        
        # Store contract
        self.contracts[contract_address] = contract
        return contract_address
        
    def execute_contract(self, contract_address: str, method: str, params: Dict[str, Any]) -> Any:
        """Execute a smart contract method"""
        if contract_address not in self.contracts:
            raise ValueError("Contract not found")
            
        contract = self.contracts[contract_address]
        
        # Create execution context
        context = {
            'contract': contract,
            'blockchain': self.blockchain,
            'params': params,
            'state': contract.state
        }
        
        # Execute contract code (simplified)
        try:
            # In a real implementation, you would need a secure execution environment
            result = eval(f"{contract.code}.{method}({params})")
            return result
        except Exception as e:
            raise Exception(f"Contract execution failed: {e}")
            
    def _generate_contract_address(self, code: str, owner: str) -> str:
        """Generate a unique contract address"""
        import hashlib
        content = f"{code}{owner}{datetime.utcnow().timestamp()}"
        return hashlib.sha256(content.encode()).hexdigest()

# Example smart contract code
class TokenContract:
    def __init__(self, context):
        self.context = context
        self.state = context['state']
        if 'balances' not in self.state:
            self.state['balances'] = {}
            
    def transfer(self, from_address: str, to_address: str, amount: float) -> bool:
        """Transfer tokens between addresses"""
        balances = self.state['balances']
        
        # Check if sender has enough balance
        if balances.get(from_address, 0) < amount:
            return False
            
        # Update balances
        balances[from_address] = balances.get(from_address, 0) - amount
        balances[to_address] = balances.get(to_address, 0) + amount
        return True
        
    def get_balance(self, address: str) -> float:
        """Get token balance for an address"""
        return self.state['balances'].get(address, 0) 