# AWS Real time Air Quality Visualization, prediction and LLM reporting

## Description
This cloud-based solution monitors, analyzes, forecasts air quality and generates LLM-powered reports using real-time and historical data from the OpenWeather Air Pollution API. It empowers timely interventions, promotes cleaner practices, and raises awareness, contributing to improved public health, reduced pollution, and sustainable urban development.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
<!-- - [Prerequisites](#prerequisites) -->
- [Deployment Steps](#deployment-steps)  
   1. [Data Pipeline Setup](#data-pipeline-setup)  
        - [Step 1: Set up EC2 Instance with cloud9 environment](#step-1-set-up-ec2-instance)  
        - [Step 2: Configure Kinesis Data Streams](#step-2-configure-kinesis-data-streams)  
        - [Step 3: Lambda Function Setup](#step-3-lambda-function-setup)  
        - [Step 4: Store Data in S3](#step-4-store-data-in-s3)  
        - [Step 5: Set up AWS Glue Crawlers and Tables](#step-5-set-up-aws-glue-crawlers-and-tables)  
        - [Step 6: Query Data Using Athena](#step-6-query-data-using-athena)  
        - [Step 7: Visualize with Grafana](#step-7-visualize-with-grafana)    
    2. [LLM Integration](#llm-integration)
        - [Step 1: Set Grafana Variables](#step-1-set-grafana-variables)  
        - [Step 2: Load the LLM](#step-2-load-the-llm)
        - [Step 3: Setup ngrok](#step-3-setup-ngrok)
- [Results](#results)
- [Contributing](#contributing)

## Overview
This project is designed to collect, process, and visualize real-time weather data by leveraging AWS services, OpenWeather API, and machine learning tools. The pipeline automates the retrieval of weather data, stores it efficiently in the cloud, processes it for analytics, and makes it accessible for real-time visualization and predictive analysis.

### Key Features:
#### 1. Real-time Data Ingestion:
Weather data is continuously fetched from the OpenWeather API using an EC2 instance, ensuring up-to-date weather information.

#### 2. Data Streaming & Processing:
The data is streamed through Amazon Kinesis Data Streams, providing a scalable way to handle incoming data in real time. AWS Lambda functions are triggered to process the data, transforming it into a structured format and storing it in Amazon S3.

#### 3. Data Transformation & Cataloging:
AWS Glue Crawlers automatically discover and catalog the processed data, while Amazon Athena allows users to run SQL queries on the stored data. This makes the data easily accessible for reporting and analysis.

#### 4. Visualization with Grafana:
Grafana is integrated to create dashboards that visualize key metrics like temperature, humidity, and weather conditions. This enables users to monitor trends and gain insights into the data in real time.

#### 5. Machine Learning:
AWS SageMaker is used to train and deploy machine learning models for weather predictions, such as forecasting temperature or predicting weather conditions. These models are exposed through an API Gateway and can be accessed for inference.

#### 6. Large Language Model (LLM) Integration:
Large Language Models (LLMs) are used for generating reports and gaining deeper insights into the weather data, making the information more accessible and understandable for decision-makers.

#### 7. Automated Data Management:
The entire pipeline is automated, allowing for continuous updates, error handling, and scalability, ensuring that the system can handle a large volume of weather data efficiently.

## Architecture

The following AWS services are used in the architecture:

1. **OpenWeather (API)**: Fetches real-time weather data.
2. **EC2**: Hosts a service that fetches data from OpenWeather API.
3. **Kinesis Data Stream**: Streams the weather data for further processing.
4. **Lambda**: Transforms the data and processes it.
5. **S3**: Stores the processed data in a structured format.
6. **Glue Crawlers**: Catalogs the data in S3 for querying.
7. **Athena**: Queries the data stored in S3.
8. **API Gateway**: Exposes the service to other applications or external consumers.
9. **Grafana**: Visualizes data using custom dashboards.
10. **SageMaker**: Deploys machine learning models.
11. **LLM Integration:** Large Language Models (LLMs) are integrated for report generation and deeper insights into predicted values.
12. **ngrok**: Exposes the local API Gateway for external testing.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="Images/Architecture-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="Images/Architecture-light.png">
  <img alt="Architecture Diagram" src="Images/Architecture-light.png">
</picture>

<!-- ## Prerequisites -->

## Deployment Steps
### Data Pipeline Setup

#### Step 1: Set up EC2 Instance with cloud9 environment 
1. Go to the Cloud9 dashboard in the AWS Management Console.
2. Launch a new Cloud9 environment with a new EC2 Instance.
    - Choose the instance type `t2.micro` with Amazon Linux.
    - Select the Secure Shell (SSH) connection type.
3. Open the Cloud9 IDE and install the necessary packages:
    ```bash
    sudo apt update
    sudo apt install python3-pip
    pip3 install boto3 requests csv time json io
    ```
5. Create a Python script (`fetch_data.py`) to fetch data from the OpenWeather API.
It is important to configure the Kinesis client before fetching the data and set up the AWS Credentials:
    ```python
    aws_region = "your-region-here"
    aws_access_key_id="aws-access-id"
    aws_secret_access_key="your-secret-access-keye-here"

    KINESIS_STREAM_NAME = "airpollution_data"

    kinesis_client = boto3.client('kinesis', 
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id, 
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token)
    ```
##### Note: 
- This  data stream creation is detailed in the following step.
- It is necessary to have an S3 bucket named `useful-data-bucket` that containes the csv file `countries.csv`.


#### Step 2: Configure Kinesis Data Streams 
1. Navigate to the **Kinesis** section in AWS Console and Click on **Create stream**.
2. Name your stream (e.g., `airpollution_data`), and define the number of shards based on your data volume or choose the `On-Demand` option.
3. Once the stream is created, ensure the EC2 instance has the proper IAM role to send data to Kinesis.

#### Step 3: Lambda Function Setup 
1. Go to **AWS Lambda** and create a new function.
2. Select **Author from scratch** and use an the python runtime.
3. Set permissions for Lambda to read from Kinesis and write to S3.
4. Install the necessary packages:
    ```bash
    pip install boto base64 json datetime
    ```
5. Use the Lambda function (`data_transformation.py`) to format data and write it into the S3 bucket.

#### Step 4: Store Data in S3
1. Create an S3 bucket:
   - Go to **S3** in AWS Console and click **Create Bucket** and specify a unique name (e.g. `airquality-databucket`).
   - Set permissions and configure the bucket to store the processed weather data.
   - The data is stored in folders, each folder designating a specific country and its corresponding data.
2. Ensure that the Lambda function has the appropriate IAM role to write data to S3.

#### Step 5: Set up AWS Glue Crawlers and Tables
1. Go to **AWS Glue Databases** and create a new Database with a unique name (e.g. `airquality_base`).
3. Go to **AWS Glue** and create a new Crawler.
4. - Define the source as the S3 bucket where weather data is stored.
    - Set the `airquality_base` database as the output.
    - Set up the crawler to run on a scheduled basis (e.g., every hour) to keep the Glue Catalog up-to-date.
5. After running the whole pipeline, navigate to the AWS Glue Table schema and make sure it is identical to `data_schema.json` or update it.

#### Step 6: Query Data Using Athena
1. In the **Athena** console, create a new database (for query results storage).
2. Define a table that references the Glue cataloged data in S3.
3. Run SQL queries to analyze the air quality data.
   Example query:
   ```sql
   SELECT * FROM "airquality_base"."airquality_databucket" limit 30;
   ```

#### Step 7: Visualize with Grafana

##### Install Grafana
To visualize the air pollution data, we installed Grafana on an `t2.medium` EC2 instance

##### Grafana Installation
1. Download and run Grafana:
    ```bash
    sudo yum update -y
    sudo yum install grafana -y
    sudo systemctl daemon-reload
    ```
2. Create the file `credentials`in the folder path `usr/share/grafana/.aws` and store your AWS credentials inside.
    - These tokens are available in your AWS console under:
AWS Management Console → AWS Details section when you sign in to your AWS interface.
4. Launch and enable Grafana:
    ```bash
    sudo systemctl start grafana-server
    sudo systemctl enable grafana-server.service
    ```
2. Once Grafana is running, access it at `http://<instance-address>:3000`. The default credentials are:
    - Username: `admin`
    - Password: `admin`
3. After logging in, change the password for security purposes.

##### Add Athena as a Data Source
1. In Grafana, go to **Configuration** > **Data Sources** > **Add Data Source**.
2. Select **Athena** from the list of available data sources.
3. Enter the connection details:
    - **Name**: A name for the data source (e.g., `Athena Air Pollution Data`).
    - Use the `Credentials file` as the Authentication provider and select the region where your Athena queries will run.
    - **Athena Workgroup**: Specify the workgroup you are using (or leave default).
    - Select the **Database** and the **Table** you are qureing as well as the S bucket for query results' storage.

##### Create a Dashboard in Grafana
1. After configuring the Athena data source, create a new dashboard in Grafana.
2. Add panels for visualizing weather data.
3. Configure queries for each panel.


### LLM Integration
#### Step 1: Set Grafana Variables
#### Step 2: Load the LLM
#### Step 3: Setup ngrok

## Results
### Data Visualisation Dashboard
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="Images/vis1-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="Images/vis1-light.png">
  <img alt="Data Visualisation" src="Images/vis1-light.png">
</picture>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="Images/vis2-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="Images/vis2-light.png">
  <img alt="Data Visualisation" src="Images/vis2-light.png">
</picture>
## Contributing
If you have suggestions for improving the pipeline or visualizations, feel free to fork the repository and submit pull requests.

### Contributing Guidelines:
1. **Fork** the repository and clone it locally.
2. Make your changes and ensure that new code adheres to the project's code standards.
3. **Test** your changes.
4. Create a **pull request** with a detailed description of your changes.