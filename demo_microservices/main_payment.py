from fastapi import FastAPI, Request, HTTPException
import time
from logger import setup_logger

app = FastAPI()
logger = setup_logger("PaymentAPI")

@app.post("/payment/process")
async def process_payment(request: Request):
    user_data = await request.json()
    logger.info(f"Processing payment for user: {user_data.get('user_id')}")
    
    try:
        if "billing_address" not in user_data:
            logger.error("Missing billing address, failing payment")
            raise HTTPException(status_code=400, detail="Missing billing address")
            
        address = user_data["billing_address"]
        card_number = user_data.get("card_number")
        
        logger.info(f"Initiating transfer with card {card_number} for address {address}")
        time.sleep(0.5) 
        
        logger.info("Payment processed successfully")
        return {"status": "success", "transaction_id": "txn_succ_123"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in payment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Error")
