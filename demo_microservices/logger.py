import logging
import json
import traceback
import sys
import threading
import time
import os
import boto3
from datetime import datetime, timezone

LOG_S3_BUCKET_URL = os.getenv("LOG_S3_BUCKET_URL", "mock-bucket")

class S3BatchJsonHandler(logging.Handler):
    def __init__(self, service_name, batch_interval=5):
        super().__init__()
        self.service_name = service_name
        self.batch_interval = batch_interval
        self.log_batch = []
        self.lock = threading.Lock()
        
        # Start background worker
        self.worker_thread = threading.Thread(target=self._upload_worker, daemon=True)
        self.worker_thread.start()

    def emit(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "service_name": self.service_name,
            "log_level": record.levelname,
            "message": record.getMessage()
        }
        
        if record.exc_info:
            log_entry["stack_trace"] = "".join(traceback.format_exception(*record.exc_info))
        elif sys.exc_info()[0] is not None:
            # Fallback if exc_info isn't explicitly passed but an exception is active
            log_entry["stack_trace"] = "".join(traceback.format_exception(*sys.exc_info()))
            
        with self.lock:
            self.log_batch.append(log_entry)

    def _upload_worker(self):
        while True:
            time.sleep(self.batch_interval)
            with self.lock:
                if not self.log_batch:
                    continue
                batch_to_upload = list(self.log_batch)
                self.log_batch.clear()
            
            self._upload_to_s3(batch_to_upload)

    def _upload_to_s3(self, batch):
        if not LOG_S3_BUCKET_URL:
            return
        
        try:
            # Simulating boto3 s3 upload
            # client = boto3.client('s3')
            # client.put_object(Bucket=LOG_S3_BUCKET_URL, Key=f"{self.service_name}_{int(time.time())}.json", Body=json.dumps(batch))
            print(f"[{self.service_name}] Simulating S3 upload of {len(batch)} logs to {LOG_S3_BUCKET_URL}")
        except Exception as e:
            print(f"Failed to upload logs to S3: {e}")

def setup_logger(service_name):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = S3BatchJsonHandler(service_name)
        logger.addHandler(handler)
        
    return logger
