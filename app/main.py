from fastapi import FastAPI
from app.exceptions import register_exception_handlers
from app import metrics
from app.routers import health, transaction

app = FastAPI(title="ComplianceOps Gateway")

app.middleware("http")(metrics.record_request)

app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(transaction.router)

register_exception_handlers(app)
