from user_posting_emulation import *

new_connector = AWSDBConnector()
"""
For posting the kinesis data
"""
@run_continously
def run_infinite_post_data_loop():
    #new_connector.connect_and_get_records()
 
    pin_topic = '0eb84f80c29b.pin'
    geo_topic = '0eb84f80c29b.geo'
    user_topic = '0eb84f80c29b.user'
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
            invoke_url1 = "https://d2ro2kddr2.execute-api.us-east-1.amazonaws.com/0eb84f80c29b-prod/streams/"+pin_stream+"/record"
            invoke_url2 = "https://d2ro2kddr2.execute-api.us-east-1.amazonaws.com/0eb84f80c29b-prod/streams/"+geo_stream+"/record"
            invoke_url3 = "https://d2ro2kddr2.execute-api.us-east-1.amazonaws.com/0eb84f80c29b-prod/streams/"+user_stream+"/record"
            
            for row in pin_selected_row:
                pin_result = dict(row._mapping)
            
            geo_string = text(f"SELECT * FROM geolocation_data LIMIT {random_row}, 1")
            geo_selected_row = connection.execute(geo_string)
                       
            for row in geo_selected_row:
                geo_result = dict(row._mapping)

            user_string = text(f"SELECT * FROM user_data LIMIT {random_row}, 1")
            user_selected_row = connection.execute(user_string)
            
            for row in user_selected_row:
                user_result = dict(row._mapping)
        # post result to Kinesis stream via API
        update_record("PUT", invoke_url1, pin_result, pin_stream)
        print("just before the geo data")
        update_record("PUT", invoke_url2, geo_result, geo_stream)
        print("just before the user data")
        update_record("PUT", invoke_url3, user_result, user_stream)
       

if __name__ == "__main__":
    print('Working')
    run_infinite_post_data_loop()