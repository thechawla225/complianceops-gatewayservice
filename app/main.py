from fastapi import FastAPI
from app.exceptions import register_exception_handlers
from app.routers import health, transaction
 
app = FastAPI(title="ComplianceOps Gateway")
 
app.include_router(health.router)
app.include_router(transaction.router)
 
register_exception_handlers(app)