from fastapi import FastAPI, Request, HTTPException
import time
import requests
from logger import setup_logger

app = FastAPI()
logger = setup_logger("PaymentAPI")

def stripe_charge(card_number, amount=100):
    if card_number == "4242424242424242":
        logger.warning(f"Processing test card {card_number} via external Stripe API...")
        res = requests.post("https://httpstat.us/504?sleep=30000", json={"test": True})
        res.raise_for_status()
    else:
        time.sleep(0.5)

@app.post("/payment/process")
async def process_payment(request: Request):
    user_data = await request.json()
    logger.info(f"Processing payment for user: {user_data.get('user_id')}")
    
    try:
        address = user_data["billing_address"]
        card_number = user_data.get("card_number")
        
        logger.info(f"Initiating transfer with card {card_number} for address {address}")
        stripe_charge(card_number)
        
        logger.info("Payment processed successfully")
        return {"status": "success", "transaction_id": "txn_succ_123"}
        
    except requests.RequestException as e:
        logger.error(f"External payment gateway error: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail="Bad Gateway")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in payment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Error")
