from fastapi import FastAPI, Request, Depends, BackgroundTasks, background
from fastapi.templating import Jinja2Templates
from sqlalchemy import engine
import dbmodels
import yfinance as yf
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from pydantic import BaseModel
from dbmodels import StockData
app = FastAPI()

dbmodels.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

class StockReq(BaseModel):
    stockname: str

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def yahoo_data_fetch(id: int):
    db = SessionLocal()
    stock_data = db.query(StockData).filter(StockData.id == id).first()
    yahoo_stock_data = yf.Ticker(stock_data.stockname)
    stock_data.ma200 = yahoo_stock_data.info["twoHundredDayAverage"]
    stock_data.ma50 = yahoo_stock_data.info["fiftyDayAverage"]
    stock_data.price = yahoo_stock_data.info["previousClose"]
    stock_data.forward_pe = yahoo_stock_data.info["forwardPE"]
    stock_data.forward_eps = yahoo_stock_data.info["forwardEps"]
    if stock_data.dividend_yield is not None:
        stock_data.dividend_yield = yahoo_stock_data.info["dividendYield"] * 100
    db.add(stock_data)
    db.commit()

@app.get("/")
def dashboard(request: Request, forward_pe = None, dividend_yield = None, ma50 = None, ma200 = None, db: Session = Depends(get_db)):
    ''''''''''
    displays the dashboard
    '''''''''''
    Stocks = db.query(StockData)
    if forward_pe:
        Stocks = Stocks.filter(StockData.forward_pe < forward_pe)
    if dividend_yield:
        Stocks = Stocks.filter(StockData.dividend_yield > dividend_yield)
    if ma50:
        Stocks = Stocks.filter(StockData.price > ma50)
    if dividend_yield:
        Stocks = Stocks.filter(StockData.price > ma200)

    return templates.TemplateResponse("dashboard.html",{
        "request": request,
        "Stocks": Stocks,
        "dividend_yield": dividend_yield,
        "forward_pe": forward_pe,
        "ma200": ma200,
        "ma50": ma50
    })

@app.post("/stockname")
async def stockCreate(stock_req: StockReq, task_background : BackgroundTasks,db: Session = Depends(get_db)):
    ''''''''''
    stock creation
    '''''''''''
    stock = StockData()
    stock.stockname = stock_req.stockname
    db.add(stock)
    db.commit()
    task_background.add_task(yahoo_data_fetch, stock.id)
    return{
        "code": "success",
        "message": "stock has been created"
    }