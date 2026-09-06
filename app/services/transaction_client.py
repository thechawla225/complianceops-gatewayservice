import httpx
from fastapi import HTTPException
from app.config import settings
 
 
async def create_transaction(payload: dict) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        try:
            return await client.post(
                f"{settings.transaction_service_url}/transactions", json=payload
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail="transaction service unreachable") from exc
 
 
async def get_transaction(transaction_id: str) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        try:
            return await client.get(
                f"{settings.transaction_service_url}/transactions/{transaction_id}"
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail="transaction service unreachable") from exc
 