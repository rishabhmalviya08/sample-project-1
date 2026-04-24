from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from database import get_db, init_db
from logger import setup_logger

app = FastAPI()
logger = setup_logger("InventoryAPI")

init_db()

class InventoryRequest(BaseModel):
    product_id: int
    quantity: int

@app.post("/inventory/deduct")
def deduct_inventory(req: InventoryRequest):
    logger.info(f"Deducting {req.quantity} of product {req.product_id}")
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("INSERT OR IGNORE INTO inventory (product_id, stock) VALUES (?, 100)", (req.product_id,))
        
        cursor.execute("SELECT stock FROM inventory WHERE product_id = ?", (req.product_id,))
        row = cursor.fetchone()
        
        if not row or row[0] < req.quantity:
            logger.error(f"Insufficient stock for product {req.product_id}")
            raise HTTPException(status_code=400, detail="Insufficient stock")
            
        new_stock = row[0] - req.quantity
        cursor.execute("UPDATE inventory SET stock = ? WHERE product_id = ?", (new_stock, req.product_id))
        conn.commit()
        
        logger.info(f"Successfully deducted stock for product {req.product_id}. New stock: {new_stock}")
        return {"status": "success", "new_stock": new_stock}
    except Exception as e:
        logger.error(f"Database error while deducting inventory: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
