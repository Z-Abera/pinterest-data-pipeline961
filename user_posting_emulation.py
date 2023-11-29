import requests
from time import sleep
import random
from multiprocessing import Process
import boto3
import json
import sqlalchemy
from sqlalchemy import text


random.seed(100)


class AWSDBConnector:

    def __init__(self):

        self.HOST = "pinterestdbreadonly.cq2e8zno855e.eu-west-1.rds.amazonaws.com"
        self.USER = 'project_user'
        self.PASSWORD = ':t%;yCY3Yjg'
        self.DATABASE = 'pinterest_data'
        self.PORT = 3306
        
    def create_db_connector(self):
        engine = sqlalchemy.create_engine(f"mysql+pymysql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}?charset=utf8mb4")
        return engine


new_connector = AWSDBConnector()


def run_infinite_post_data_loop():
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
            invoke_url1 = "https://d2ro2kddr2.execute-api.us-east-1.amazonaws.com/0eb84f80c29b-stage/topics/0eb84f80c29b.pin"
            
            for row in pin_selected_row:
                pin_result = dict(row._mapping)
                #To send JSON messages you need to follow this structure
                payload = json.dumps({
                    "records": [
                        {
                        #Data should be send as pairs of column_name:value, with different columns separated by commas       
                        "value": {"index": pin_result["index"], "unique_id": pin_result["unique_id"], "title": pin_result["title"], "description": pin_result["description"],"poster_name": pin_result["poster_name"],"follower_count": pin_result["follower_count"],"tag_list": pin_result["tag_list"],"is_image_or_video": pin_result["is_image_or_video"],"image_src": pin_result["image_src"],"downloaded": pin_result["downloaded"],"save_location": pin_result["save_location"],"category": pin_result["category"]}
                        }
                    ]
                })

                headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'}
                #headers = {'Content-Type': 'application/json'}
                
                response = requests.request("POST", invoke_url1, headers=headers, data=payload)
                print("printing status code")
                print(response.status_code)
                print(response.reason)

            geo_string = text(f"SELECT * FROM geolocation_data LIMIT {random_row}, 1")
            geo_selected_row = connection.execute(geo_string)
            invoke_url2 = "https://d2ro2kddr2.execute-api.us-east-1.amazonaws.com/0eb84f80c29b-stage/topics/{geo_topic}"
            
            for row in geo_selected_row:
                geo_result = dict(row._mapping)

            user_string = text(f"SELECT * FROM user_data LIMIT {random_row}, 1")
            user_selected_row = connection.execute(user_string)
            invoke_url3 = "https://d2ro2kddr2.execute-api.us-east-1.amazonaws.com/0eb84f80c29b-stage/topics/{user_topic}"
            
            for row in user_selected_row:
                user_result = dict(row._mapping)
            
            #print(pin_result.keys())

            #print(geo_result.keys())
            #print(user_result.keys())


if __name__ == "__main__":
    run_infinite_post_data_loop()
    #print('Working')
    
    

