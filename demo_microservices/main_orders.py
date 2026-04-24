from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from database import get_db, init_db
from logger import setup_logger

app = FastAPI()
logger = setup_logger("OrdersAPI")

init_db()

class OrderRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    user_data: dict

INVENTORY_URL = "http://localhost:8003/inventory/deduct"
PAYMENT_URL = "http://localhost:8002/payment/process"

@app.post("/orders/create")
def create_order(req: OrderRequest):
    logger.info(f"Starting order creation for user {req.user_id}, product {req.product_id}")
    
    try:
        logger.info("Calling Inventory API")
        inv_res = requests.post(INVENTORY_URL, json={"product_id": req.product_id, "quantity": req.quantity})
        if inv_res.status_code != 200:
            logger.error(f"Inventory deduction failed: {inv_res.text}")
            raise HTTPException(status_code=400, detail="Inventory unavailable")
            
        logger.info("Calling Payment API")
        pay_res = requests.post(PAYMENT_URL, json=req.user_data)
        if pay_res.status_code != 200:
            logger.error(f"Payment failed: {pay_res.text}")
            raise HTTPException(status_code=400, detail="Payment rejected")
            
        logger.info("Saving order to database")
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO orders (user_id, product_id, status) VALUES (?, ?, ?)",
                (req.user_id, req.product_id, "COMPLETED")
            )
            conn.commit()
            order_id = cursor.lastrowid
        except Exception as db_err:
            logger.error("Failed to commit order into DB schema", exc_info=True)
            raise HTTPException(status_code=500, detail="Database write error")
            
        logger.info(f"Order {order_id} fully completed")
        return {"status": "success", "order_id": order_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Critical checkout error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Checkout failed")
