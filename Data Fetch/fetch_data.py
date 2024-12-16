import boto3
import requests
import csv
import time
import json
import io 

# AWS Configuration
aws_region = "us-east-1" 
aws_access_key_id="your-id"
aws_secret_access_key="your-access-key"
aws_session_token="your-session-token"

# Initialize Kinesis Client
KINESIS_STREAM_NAME = "airpollution_data"

kinesis_client = boto3.client('kinesis', 
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id, 
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token)

# S3 Client
s3_client = boto3.client(
    's3',
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token
)

# Fetch the S3 file
S3_BUCKET_NAME = "useful-data-bucket"
S3_FILE_KEY = "countries.csv"

# Data fetching from the API
def fetch_api_data(lat, lon):
    key="your-key"
    response = requests.get(f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={key}")
    response.raise_for_status()
    return response.json()

# Send data to Kinesis without formatting
def send_to_kinesis(data):
    partition_key = data["region"]
    response = kinesis_client.put_record(
        StreamName=KINESIS_STREAM_NAME,
        Data=json.dumps(data),
        PartitionKey=partition_key
    )
    print(f"Record sent to Kinesis: {response}")
    

if __name__ == "__main__":
    try:
        s3_response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_FILE_KEY)
        file_content = s3_response['Body'].read().decode('utf-8')
        csv_reader = csv.reader(io.StringIO(file_content))
        header = next(csv_reader)

        while True:
            for row in csv_reader:
                api_data = fetch_api_data(row[1], row[2])
                api_data["region"]=row[0]
                api_data["continent"]=row[3]
                send_to_kinesis(api_data)
                time.sleep(3)
            time.sleep(120)
    except Exception as e:
        print(f"An error occurred: {e}")
