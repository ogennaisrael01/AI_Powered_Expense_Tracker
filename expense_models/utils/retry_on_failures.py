import logging
import time
from expense_tracker import settings

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)


def retry_on_failures(request):
    attempts = int(settings.ATTEMPTS)
    retries = int(settings.RETRIES)

    for _ in range(1, retries+1):
        try:
            if request:
                return {
                    "success": True,
                    "request": request
                }
        except Exception as e:
            logging.error("Error: ", e)
           
            if attempts < retries:
                time.sleep(int(settings.SLEEP))
                logging.warn(f"RETRYING: {attempts}......")
            else:
                return {
                    "success": False,
                    "message": "Maximum attempts Excedeed"
                }
        attempts += 1