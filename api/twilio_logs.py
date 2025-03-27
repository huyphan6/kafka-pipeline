# fetches twilio SMS log data

import requests, logging, os
from dotenv import load_dotenv

#! DATE FORMAT: MM/DD/YYYY
def fetch_twilio_logs_by_date_range(start: str, end: str) -> list:
    try:
        load_dotenv()
        
        url = os.getenv("LOG_DATA_ENDPOINT")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        }
        data = {
            "accountSid": os.getenv("ACCOUNT_SID"),
            "authToken": os.getenv("AUTH_TOKEN"),
            "dateRange": [start, end]
        }
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)

        try:
            logData = response.json()
        except requests.JSONDecodeError:
            logging.error("Failed to decode JSON response.")
            return None

        logging.info("Fetched Logs Successfully")
        return logData
    
    except requests.ConnectionError:
        logging.error("Network error: Failed to connect to API.")
    except requests.Timeout:
        logging.error("Request timed out.")
    except requests.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
    except requests.RequestException as e:
        logging.error(f"Failed to fetch logs from API: {e}")

    return None