from confluent_kafka import Producer
from dotenv import load_dotenv
import socket, time, json, requests, os

def deliveryReport(err, msg):
    if err is not None:
        print(f"Delivery Failed for log {msg.key()} : {err}")
    else:
        print(f"Log Delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset}")
        
def fetchLocalData():
    try:
        with open("./data/logData.json") as f:
            logData = json.load(f)
            
        return logData
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Failed to load logs from file: {e}")
        return []
    
def fetchApiData():
    try:
        load_dotenv()
        
        url = os.getenv("LOGDATAENDPOINT")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        }
        data = {
            "accountSid": os.getenv("ACCOUNTSID"),
            "authToken": os.getenv("AUTHTOKEN"),
            "dateRange": ["", ""]
        }
        
        logData = requests.post(url, json=data, headers=headers)
        return logData
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch logs from API: {e}")
        return []

if __name__ == "__main__":
    # producer config
    producer_config  ={
        'bootstrap.servers': "localhost:9092",
        'client.id' : "log-producer",
    }

    # producer init
    producer = Producer(producer_config)
    
    # fetch log data
    # logData = fetchLocalData()
    logData = []
    
    # produce logs to kafka
    try: 
        for log in logData:
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
                        {"type": "string", "optional": True, "field": "uri"},
                        {"type": "string", "optional": True, "field": "accountSid"},
                        {"type": "string", "optional": True, "field": "numMedia"},
                        {"type": "string", "optional": True, "field": "status"},
                        {"type": "string", "optional": True, "field": "messagingServiceSid"},
                        {"type": "string", "optional": True, "field": "sid"},
                        {"type": "string", "optional": True, "field": "dateSent"},
                        {"type": "string", "optional": True, "field": "dateCreated"},
                        {"type": "string", "optional": True, "field": "errorCode"},
                        {"type": "string", "optional": True, "field": "priceUnit"},
                        {"type": "string", "optional": True, "field": "apiVersion"},
                        {
                            "type": "struct",
                            "optional": True,
                            "field": "subresourceUris",
                            "fields": [
                                {"type": "string", "optional": True, "field": "feedback"},
                                {"type": "string", "optional": True, "field": "media"}
                            ]
                        }
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