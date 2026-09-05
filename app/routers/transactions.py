from fastapi import APIRouter, Depends, Request
 
from app.dependencies.auth import verify_api_key
from app.schemas.transaction import TransactionCreate
from app.services import transaction_client

#Adding this dependency here, it will be used when the parser is actually written
from app.services.mt103_parser import parse_mt103
 
router = APIRouter(prefix="/transactions", tags=["transactions"])
 
 
@router.post("", dependencies=[Depends(verify_api_key)])
async def create_transaction(payload: TransactionCreate) -> dict:
    return await transaction_client.create_transaction(payload.model_dump())
 
 
@router.post("/mt103", dependencies=[Depends(verify_api_key)])
async def create_transaction_from_mt103(request: Request) -> dict:
    raw_text = (await request.body()).decode("utf-8")
    payload = parse_mt103(raw_text)
    return await transaction_client.create_transaction(payload.model_dump())
 
 
@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str) -> dict:
    return await transaction_client.get_transaction(transaction_id)