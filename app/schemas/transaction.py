from typing import Optional
from pydantic import BaseModel, Field
 

class Debtor(BaseModel):
    name: str
    agentBic: Optional[str] = Field(default=None, min_length=8, max_length=11)
 
 
class Creditor(BaseModel):
    name: str
    agentBic: Optional[str] = Field(default=None, min_length=8, max_length=11)
 
#Transaction Amount is always defined as a string in MT103, so ive defined it in the same way in my schema
class InstructedAmount(BaseModel):
    amount: str 
    currency: str = Field(min_length=3, max_length=3)
 
 
class Transaction(BaseModel):
    endToEndId: str
    debtor: Debtor
    creditor: Creditor
    instructedAmount: InstructedAmount
    remittanceInformation: Optional[str] = None