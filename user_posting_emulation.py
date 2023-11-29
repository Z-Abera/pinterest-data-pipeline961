import requests
from time import sleep
import random
from multiprocessing import Process
from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import sqlalchemy
from sqlalchemy import text
import uvicorn

app = FastAPI()

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

# Kafka producer configuration
kafka_bootstrap_servers = 'b-2.pinterestmskcluster.w8g8jt.c12.kafka.us-east-1.amazonaws.com:9098,b-1.pinterestmskcluster.w8g8jt.c12.kafka.us-east-1.amazonaws.com:9098,b-3.pinterestmskcluster.w8g8jt.c12.kafka.us-east-1.amazonaws.com:9098'
pin_topic = '0eb84f80c29b.pin'
geo_topic = '0eb84f80c29b.geo'
user_topic = '0eb84f80c29b.user'

producer = KafkaProducer(
    bootstrap_servers=kafka_bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_to_kafka(topic, data):
    # Send data to Kafka topic
    producer.send(topic, value=data)

def run_infinite_post_data_loop():
    while True:
        sleep(random.randrange(0, 2))
        random_row = random.randint(0, 11000)
        engine = new_connector.create_db_connector()

        with engine.connect() as connection:
            # Fetch data from Pinterest table
            pin_string = text(f"SELECT * FROM pinterest_data LIMIT {random_row}, 1")
            pin_selected_row = connection.execute(pin_string)

            for row in pin_selected_row:
                pin_result = dict(row._mapping)
                # Send Pinterest data to Kafka
                send_to_kafka(pin_topic, pin_result)

            # Fetch data from Geolocation table
            geo_string = text(f"SELECT * FROM geolocation_data LIMIT {random_row}, 1")
            geo_selected_row = connection.execute(geo_string)

            for row in geo_selected_row:
                geo_result = dict(row._mapping)
                # Send Geolocation data to Kafka
                send_to_kafka(geo_topic, geo_result)

            # Fetch data from User table
            user_string = text(f"SELECT * FROM user_data LIMIT {random_row}, 1")
            user_selected_row = connection.execute(user_string)

            for row in user_selected_row:
                user_result = dict(row._mapping)
                # Send User data to Kafka
                send_to_kafka(user_topic, user_result)

            print("Data sent to Kafka")

@app.post("/{proxy}")
def trigger_data_posting():
    # API endpoint to trigger data posting
    p = Process(target=run_infinite_post_data_loop)
    p.start()
    return {"message": "Data posting process started"}

    # Start FastAPI server
    uvicorn.run(app, host="http://ec2-52-90-167-165.compute-1.amazonaws.com:8082", port=8082)
