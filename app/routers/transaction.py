import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
 
from app.dependencies.auth import verify_api_key
from app.schemas.transaction import Transaction
from app.services import transaction_client
from app.services.mt103_parser import parse_mt103
 
router = APIRouter(prefix="/transactions", tags=["transactions"])
 
 
def _forward(resp: httpx.Response) -> JSONResponse:
    return JSONResponse(status_code=resp.status_code, content=resp.json())
 
 
@router.post("", dependencies=[Depends(verify_api_key)])
async def create_transaction(payload: Transaction) -> JSONResponse:
    resp = await transaction_client.create_transaction(payload.model_dump())
    return _forward(resp)
 
 
@router.post("/mt103", dependencies=[Depends(verify_api_key)])
async def create_transaction_from_mt103(request: Request) -> JSONResponse:
    raw_text = (await request.body()).decode("utf-8")
    payload = parse_mt103(raw_text)
    resp = await transaction_client.create_transaction(payload.model_dump())
    return _forward(resp)
 
 
@router.get("/{transaction_id}", dependencies=[Depends(verify_api_key)])
async def get_transaction(transaction_id: str) -> JSONResponse:
    resp = await transaction_client.get_transaction(transaction_id)
    return _forward(resp)
 