from fastapi import FastAPI
from pydantic import BaseModel

from settlement import settle_expenses

app = FastAPI(title="P2P Expense Engine")


class Expense(BaseModel):
    paid_by: str
    amount: float
    participants: list[str]


class SettleRequest(BaseModel):
    expenses: list[Expense]


@app.get("/")
def home():
    return {"message": "P2P Expense Engine is running"}


@app.post("/settle")
def settle(request: SettleRequest):
    expenses = [e.model_dump() for e in request.expenses]
    balances, settlements = settle_expenses(expenses)
    return {
        "balances": {name: str(b) for name, b in balances.items()},
        "settlements": [
            {"from": s["from"], "to": s["to"], "amount": str(s["amount"])}
            for s in settlements
        ],
    }
