# JSON data in -> Cleaned JSON out
import json

def clean(data: list) -> list:
    # remove unnecessary and sensitive fields
    for log in data:
        del log["uri"]
        del log["accountSid"]
        del log["sid"]
        del log["subresourceUris"]
    
    return data