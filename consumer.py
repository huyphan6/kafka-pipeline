from confluent_kafka import Consumer, KafkaException
from pprint import pformat
from colorama import Fore, Style
import pandas as pd
import json, re

def format_kafka_message(msg):
    if msg is None:
        return None
    else:
        header = f"{Fore.CYAN}=== Kafka Message [Partition {msg.partition()}]{Style.RESET_ALL}"
        
        return (
            f"{header}\n"
            f"{Fore.YELLOW}Topic:{Style.RESET_ALL}     {msg.topic()}\n"
            f"{Fore.YELLOW}Offset:{Style.RESET_ALL}    {msg.offset()}\n"
            f"{Fore.YELLOW}Key:{Style.RESET_ALL}       {msg.key().decode('utf-8') if msg.key() else ''}\n"
            f"{Fore.YELLOW}Value:{Style.RESET_ALL}\n{pformat(msg.value().decode('utf-8'), indent=2)}"
    )

def process_logs(logs, name):
    # convert to dataframe
    df = pd.DataFrame(logs)
    
    # additional cleaning + processing
    df.to_csv(f"data/{name}.csv", index=False)
    print(f"Created Dataframe!")
    return df

def aggregate_to_db(df):
    pass

if __name__ == "__main__":
    # consumer config
    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'log-consumer-group',
        'auto.offset.reset': 'earliest'
    }

    # consumer init
    consumer = Consumer(consumer_config)
    consumer.subscribe(["logs"])
    
    # iterate over the logs and clean accordingly
    outboundLogs = []
    inboundLogs = []
    
    try:
        while True:
            # consumer will poll the producer/broker for data
            msg = consumer.poll(timeout=1.0)
            print(format_kafka_message(msg))
            # print(f'log received with message: {msg}')
            
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break
            
            # logKey = json.loads(msg.key().decode('utf-8')) if msg.key() else None
            try:
                log = json.loads(msg.value().decode('utf-8'))
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {msg.value()} | Error: {e}")
                continue  # Skip malformed messages
            except KeyError as e:
                print(f"Missing 'direction' key in log: {log}")
                continue
            
            if log["direction"] == "inbound":
                inboundLogs.append(log)
            else:
                outboundLogs.append(log)
                
            print(f"{len(inboundLogs) + len(outboundLogs)} logs received!")
            
            inboundDF = process_logs(logs=inboundLogs, name="inboundLogs")
            outboundDF = process_logs(logs=outboundLogs, name="outboundLogs")

    except KeyboardInterrupt:
        pass
    finally:   
        consumer.close()