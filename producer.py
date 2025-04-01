from confluent_kafka import Producer
import json, requests, logging, os
from collections.abc import Callable
from clean_data import clean
from api.twilio_logs import fetch_twilio_logs_by_date_range

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery Failed for log {msg.key()} : {err}")
    else:
        print(f"Log Delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset}")
        
def fetch_local_data():
    try:
        with open("./data/logData.json") as f:
            logData = json.load(f)
            
        return logData
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Failed to load logs from file: {e}")
        return []
    
def fetch_api_data(api: Callable) -> list:
    try:
        data = api()
        return data
    except requests.ConnectionError:
        logging.error("Network error: Failed to connect to API.")
    except requests.Timeout:
        logging.error("Request timed out.")
    except requests.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
    except requests.RequestException as e:
        logging.error(f"Failed to fetch logs from API: {e}")
    
    return None  # Return None instead of an empty list

if __name__ == "__main__":
    # producer config
    producer_config  ={
        'bootstrap.servers': "localhost:9092",
        'client.id' : "log-producer",
    }

    # producer init
    producer = Producer(producer_config)
    
    # api injection to fetch log data
    start_date, end_date = "02/31/24", "03/01/2024"
    log_data = fetch_api_data(lambda: fetch_twilio_logs_by_date_range(start_date, end_date))
    # clean
    cleaned_logs = clean(log_data)
    
    # produce logs to kafka
    try: 
        for log in cleaned_logs:
            # Prepare the message with schema (for value) and a simple string key
            message = {
                "schema": {
                    "type": "struct",
                    "fields": [
                        {"type": "string", "optional": True, "field": "body"},
                        {"type": "string", "optional": True, "field": "numSegments"},
                        {"type": "string", "optional": True, "field": "direction"},
                        {"type": "string", "optional": True, "field": "from"},
                        {"type": "string", "optional": True, "field": "to"},
                        {"type": "string", "optional": True, "field": "dateUpdated"},
                        {"type": "string", "optional": True, "field": "price"},
                        {"type": "string", "optional": True, "field": "errorMessage"},
                        {"type": "string", "optional": True, "field": "numMedia"},
                        {"type": "string", "optional": True, "field": "status"},
                        {"type": "string", "optional": True, "field": "messagingServiceSid"},
                        {"type": "string", "optional": True, "field": "dateSent"},
                        {"type": "string", "optional": True, "field": "dateCreated"},
                        {"type": "string", "optional": True, "field": "errorCode"},
                        {"type": "string", "optional": True, "field": "priceUnit"},
                        {"type": "string", "optional": True, "field": "apiVersion"},
                    ],
                    "optional": False
                },
                "payload": log  # actual data (without schema)
            }

            # Send message with a string key and structured value
            producer.produce('logs', key=(log['direction']).encode('utf-8'), value=json.dumps(message))
            producer.poll(1)
            print(f"Producer Finished")
    except KeyError as e:
        print(f"Missing 'direction' key in log: {log}")
    except Exception as e:
        print(f"Failed to produce log: {e}")
        
    producer.flush()