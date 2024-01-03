from user_posting_emulation import AWSDBConnector as AWSDBconnect
import requests
import json
from time import sleep
import random
from multiprocessing import Process
import boto3
import sqlalchemy
from sqlalchemy import text
import datetime
"""
Post results to Kafka
"""
new_connector = AWSDBconnect()

def run_infinite_post_data_loop():
    pin_stream = 'streaming-0eb84f80c29b-pin'
    geo_stream = 'streaming-0eb84f80c29b-geo'
    user_stream = 'streaming-0eb84f80c29b-user'
    pin_topic = '0eb84f80c29b.pin'
    geo_topic = '0eb84f80c29b.geo'
    user_topic = '0eb84f80c29b.user'
    while True:
        sleep(random.randrange(0, 2))
        random_row = random.randint(0, 11000)
        engine = new_connector.create_db_connector()

        with engine.connect() as connection:

            pin_string = text(f"SELECT * FROM pinterest_data LIMIT {random_row}, 1")
            pin_selected_row = connection.execute(pin_string)
            #invoke_url = "https://YourAPIInvokeURL/YourDeploymentStage/topics/YourTopicName"
            invoke_url1 = "https://d2ro2kddr2.execute-api.us-east-1.amazonaws.com/0eb84f80c29b-prod/topics/"+pin_topic
            
            for row in pin_selected_row:
                pin_result = dict(row._mapping)
               #To send JSON messages you need to follow this structure
                payload = new_connector.getPayload(pin_result)
                print("print payload:")
                print(payload)

                headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'}
                #headers = {'Content-Type': 'application/json'}
                
                response = requests.request("POST", invoke_url1, headers=headers, data=payload)
                print(response.status_code)
                print(response.raw)
            
            geo_string = text(f"SELECT * FROM geolocation_data LIMIT {random_row}, 1")
            geo_selected_row = connection.execute(geo_string)
            invoke_url2 = "https://d2ro2kddr2.execute-api.us-east-1.amazonaws.com/0eb84f80c29b-prod/topics/"+geo_topic
            
            
            for row in geo_selected_row:
                geo_result = dict(row._mapping)
                print("geo_keys")
                print(geo_result.keys())
                payload = new_connector.getPayload(geo_result)

                headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'}
                
                response = requests.request("POST", invoke_url2, headers=headers, data=payload)
                print(response.status_code)

            user_string = text(f"SELECT * FROM user_data LIMIT {random_row}, 1")
            user_selected_row = connection.execute(user_string)
            invoke_url3 = "https://d2ro2kddr2.execute-api.us-east-1.amazonaws.com/0eb84f80c29b-prod/topics/"+user_topic
            
            for row in user_selected_row:
                user_result = dict(row._mapping)
                print("user_keys")
                print(user_result.keys())
                #To send JSON messages you need to follow this structure
                payload = new_connector.getPayload(user_result)

                headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'}
                
                response = requests.request("POST", invoke_url3, headers=headers, data=payload)
                print(response.status_code)
                


if __name__ == "__main__":
    run_infinite_post_data_loop()