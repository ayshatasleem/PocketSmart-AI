from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI(
    title="PocketSmart AI",
    description="Your Smart Budget & Recommendation Assistant",
    version="1.0.0"
)
@app.get("/dashboard")
def dashboard():
    return FileResponse("dashboard.html")

# Database setup
DATABASE_URL = "sqlite:///./pocketsmart.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Expense database table
class ExpenseDB(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    amount = Column(Float)


Base.metadata.create_all(bind=engine)
@app.post("/expenses")
def add_expense(expense: dict):
    db = SessionLocal()

    new_expense = ExpenseDB(
        category=expense.get("category", "General"),
        amount=expense.get("amount", 0)
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    db.close()

    return {
        "message": "Expense added successfully",
        "id": new_expense.id,
        "category": new_expense.category,
        "amount": new_expense.amount
    }


# Request model
class Expense(BaseModel):
    category: str
    amount: float


@app.get("/")
def home():
    return {
        "message": "Welcome to PocketSmart AI",
        "status": "Project is working"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/about")
def about():
    return {
        "project": "PocketSmart AI",
        "description": "Smart personal finance assistant"
    }


@app.post("/expense")
def expense(expense: Expense):

    db = SessionLocal()

    new_expense = ExpenseDB(
        category=expense.category,
        amount=expense.amount
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    db.close()

    return {
        "id": new_expense.id,
        "category": new_expense.category,
        "amount": new_expense.amount,
        "message": "Expense saved successfully"
    }
@app.get("/expenses")
def get_expenses():
    db = SessionLocal()

    expenses = db.query(ExpenseDB).all()

    result = []

    for expense in expenses:
        result.append({
            "id": expense.id,
            "category": expense.category,
            "amount": expense.amount
        })

    db.close()

    return result
@app.get("/expenses/total")
def total_expenses():
    db = SessionLocal()
    expenses = db.query(ExpenseDB).all()

    total = sum(expense.amount for expense in expenses)

    db.close()

    return {
        "total_expenses": total
    }
@app.get("/expenses/summary")
def expense_summary():
    db = SessionLocal()
    expenses = db.query(ExpenseDB).all()

    summary = {}

    for expense in expenses:
        if expense.category in summary:
            summary[expense.category] += expense.amount
        else:
            summary[expense.category] = expense.amount

    db.close()

    return summary
@app.get("/budget")
def budget():
    total_budget = 10000

    db = SessionLocal()
    expenses = db.query(ExpenseDB).all()

    total_spent = sum(expense.amount for expense in expenses)
    remaining = total_budget - total_spent

    db.close()

    return {
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining_budget": remaining
    }
@app.get("/budget/status")
def budget_status():
    total_budget = 10000

    db = SessionLocal()
    expenses = db.query(ExpenseDB).all()

    total_spent = sum(expense.amount for expense in expenses)
    remaining = total_budget - total_spent

    if total_spent >= total_budget:
        status = "Budget exceeded"
    elif total_spent >= total_budget * 0.8:
        status = "Warning: You are close to your budget"
    else:
        status = "Budget is under control"

    db.close()

    return {
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining_budget": remaining,
        "status": status
    }
@app.get("/recommendation")
def recommendation():

    total_budget = 10000

    db = SessionLocal()

    expenses = db.query(ExpenseDB).all()

    total_spent = sum(expense.amount for expense in expenses)

    db.close()

    remaining = total_budget - total_spent

    if remaining < 2000:
        recommendation = "Reduce unnecessary spending and focus on essential expenses."
    elif remaining < 5000:
        recommendation = "Your spending is moderate. Try to save more this month."
    else:
        recommendation = "Your budget is healthy. You can continue spending carefully and save the remaining amount."

    return {
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining_budget": remaining,
        "recommendation": recommendation
    }
@app.get("/savings")
def savings():

    total_budget = 10000

    db = SessionLocal()

    expenses = db.query(ExpenseDB).all()

    total_spent = sum(expense.amount for expense in expenses)

    db.close()

    remaining = total_budget - total_spent

    savings_target = total_budget * 0.20

    if remaining >= savings_target:
        message = "You are on track to save 20% of your budget."
    else:
        message = "Try to reduce unnecessary expenses to reach your 20% savings target."

    return {
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining_budget": remaining,
        "savings_target": savings_target,
        "message": message
    }
@app.get("/advice")
def advice():

    total_budget = 10000

    db = SessionLocal()

    expenses = db.query(ExpenseDB).all()

    total_spent = sum(expense.amount for expense in expenses)

    db.close()

    remaining = total_budget - total_spent

    if remaining < 2000:
        message = "You should reduce your spending and focus on saving."
    elif remaining < 5000:
        message = "Your spending is moderate. Try to save more."
    else:
        message = "Your budget is healthy. Keep managing your expenses carefully."

    return {
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining_budget": remaining,
        "advice": message
    }
@app.get("/")
def dashboard():
    return FileResponse("dashboard.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)