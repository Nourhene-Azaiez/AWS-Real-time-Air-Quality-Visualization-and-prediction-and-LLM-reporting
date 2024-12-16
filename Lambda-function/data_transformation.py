import boto3
import base64
import json
import csv
from io import StringIO
from datetime import datetime

def format_response(data):
    Longitude=data['coord']['lon']
    Latitude=data['coord']['lat']
    region=data['region']
    continent=data['continent']
    aqi=data['list'][0]["main"]["aqi"]
    co=float(data['list'][0]["components"]["co"])
    no=float(data['list'][0]["components"]["no"])
    no2=float(data['list'][0]["components"]["no2"])
    o3=float(data['list'][0]["components"]["o3"])
    so2=float(data['list'][0]["components"]["so2"])
    pm2_5=float(data['list'][0]["components"]["pm2_5"])
    pm10=float(data['list'][0]["components"]["pm10"])
    nh3=float(data['list'][0]["components"]["nh3"])
    timestamp=datetime.fromtimestamp(data['list'][0]["dt"]).isoformat()
    value=["Good","Fair","Moderate","Poor","Very Poor"]
    
    response = {
        "Timestamp": timestamp,
        "Region": region,
        "Continent": continent,
        "Longitude": Longitude,
        "Latitude": Latitude,
        "AQI": aqi,
        "AQI_quality": value[aqi-1],
        "CO": co,
        "NO": no,
        "NO2": no2,
        "O3": o3,
        "SO2": so2,
        "PM2_5": pm2_5,
        "PM10": pm10,
        "NH3": nh3
    }
    return response


def lambda_handler(event, context):
    bucket_name = 'airquality-databucket' 
    s3 = boto3.client('s3')


    for record in event['Records']:
        try:
            decoded_data = base64.b64decode(record['kinesis']['data']).decode('utf-8')
            record_data = json.loads(decoded_data)
            record_data= format_response(record_data)

            # Extract region and timestamp
            folder_name = record_data["Region"]
            file_name = f"{record_data['Timestamp']}.json"
            
            for x in ["Longitude","Latitude","CO", "NO", "NO2", "O3", "SO2", "PM2_5", "PM10","NH3"]:
                record_data[x]=float(record_data[x])

            # Upload to S3
            s3.put_object(
                Body=json.dumps(record_data),
                Bucket=bucket_name,
                Key=f"{folder_name}/{file_name}"
            )
            return { 
                'statusCode': 200, 
                'body': 'File uploaded successfully.' 
            }
        except Exception as e:
            print(f"An error occurred {e}")
            raise e
    print(f"Successfully processed {len(event['Records'])} records.")