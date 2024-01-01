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

new_connector = AWSDBconnect()

def run_infinite_post_data_loop():
    pin_stream = 'streaming-0eb84f80c29b-pin'
    geo_stream = 'streaming-0eb84f80c29b-geo'
    user_stream = 'streaming-0eb84f80c29b-user'
    while True:
        sleep(random.randrange(0, 2))
        random_row = random.randint(0, 11000)
        engine = new_connector.create_db_connector()

        with engine.connect() as connection:

            pin_string = text(f"SELECT * FROM pinterest_data LIMIT {random_row}, 1")
            pin_selected_row = connection.execute(pin_string)
            invoke_url = "https://d2ro2kddr2.execute-api.us-east-1.amazonaws.com/0eb84f80c29b-prod/0eb84f80c29b-streams/stream-name/record"
            
            for row in pin_selected_row:
                pin_result = dict(row._mapping)
                payload = json.dumps({
                        "StreamName": pin_stream,
                        #Data should be send as pairs of column_name:value, with different columns separated by commas       
                        "Data": {"index": pin_result["index"], "unique_id": pin_result["unique_id"], "title": pin_result["title"], "description": pin_result["description"],"poster_name": pin_result["poster_name"],"follower_count": pin_result["follower_count"],"tag_list": pin_result["tag_list"],"is_image_or_video": pin_result["is_image_or_video"],"image_src": pin_result["image_src"],"downloaded": pin_result["downloaded"],"save_location": pin_result["save_location"],"category": pin_result["category"]},
                        "PartitionKey": pin_stream
                })

                headers = {'Content-Type': 'application/json'}
                
                response = requests.request("PUT", invoke_url, headers=headers, data=payload)
                print(response.status_code)
                print("printing response text")
                print(response.text)

            geo_string = text(f"SELECT * FROM geolocation_data LIMIT {random_row}, 1")
            geo_selected_row = connection.execute(geo_string)
            
            for row in geo_selected_row:
                geo_result = dict(row._mapping)
                print("geo_keys")
                print(geo_result.keys())
                payload = new_connector.getPayload(geo_result,geo_stream)

                headers = {'Content-Type': 'application/json'}
                
                response = requests.request("PUT", invoke_url, headers=headers, data=payload)
                print(response.status_code)

            user_string = text(f"SELECT * FROM user_data LIMIT {random_row}, 1")
            user_selected_row = connection.execute(user_string)
            
            for row in user_selected_row:
                user_result = dict(row._mapping)
                print("user_keys")
                print(user_result.keys())
                #To send JSON messages you need to follow this structure
                payload = new_connector.getPayload(user_result,user_stream)

                headers = {'Content-Type': 'application/json'}
                
                response = requests.request("PUT", invoke_url, headers=headers, data=payload)
                print(response.status_code)


if __name__ == "__main__":
    run_infinite_post_data_loop()