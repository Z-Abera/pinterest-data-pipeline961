# pinterest-data-pipeline961

## Milestone 3
Keypair was created to securely connect to EC2 instance. The file (rsa.pem) that contains the private key has been added to the .gitignore file so that it doesn't get accidently exposed.
Using SSH to connect to the EC2 instance. 
TO DO: add the commands used.
### Task 3: Set up Kafka on the EC2 instance 
To connect to a predefined MSK cluster (this set up was done before this project), installing the appropriate packages was required.
Install the IAM MSK authentication package (wget https://github.com/aws/aws-msk-iam-auth/releases/download/v1.1.5/aws-msk-iam-auth-1.1.5-all.jar) on your client EC2 machine within the Kafka libs folder (kafka_2.12-2.8.1/libs). This package is necessary to connect to MSK clusters that require IAM authentication, like the one you have been granted access to.
Within the bashrc file we need to update the classpath export CLASSPATH=/home/ec2-user/kafka_2.12-2.8.1/libs/aws-msk-iam-auth-1.1.5-all.jar . The CLASSPATH environment variable is used by Java applications to specify the directories or JAR files that contain the required classes and resources. By adding the path to the aws-msk-iam-auth-1.1.5-all.jar file to the CLASSPATH, the Kafka client will be able to locate and utilize the necessary Amazon MSK IAM libraries when executing commands.
Before you are ready to configure your EC2 client to use AWS IAM for cluster authentication, by setting up a role.
Doing so we will be able to assume the <your_UserId>-ec2-access-role, which contains the necessary permissions to authenticate to the MSK cluster. 
Configure your Kafka client to use AWS IAM authentication to the cluster. To do this, you will need to modify the client.properties file, inside your kafka_folder/bin directory accordingly. 
To configure a Kafka client to use AWS IAM for authentication you should first navigate to your Kafka installation folder, and then in the bin folder.
Here, you should create a client.properties file, using the following command:
nano client.properties
To create a topic, you will first need to retrieve some information about the MSK cluster, specifically: the Bootstrap servers string and the Plaintext Apache Zookeeper connection string. Make a note of these strings, as you will need them in the next step. 

You will have to retrieve them using the MSK Management Console, as for this project you have not been provided with login credentials for the AWS CLI, so you will not be able to retrieve this information using the CLI. 
Next we create the following the topics using the below command.
Topics:
<your_UserId>.pin for the Pinterest posts data
<your_UserId>.geo for the post geolocation data
<your_UserId>.user for the post user data
Command:
./kafka-topics.sh --bootstrap-server BootstrapServerString --command-config client.properties --create --topic <topic_name>
### Milestone 4: Batch Processing: Connect a MSK cluster to a S3 bucket
The focus of this milstone is to use a MSK Connect to connect the MSK cluster to a S3 bucket, such that any data going through the cluster will be automaically save and stored in a dedicate S3 bucket.
#### Sub-tasks
1. get S3 bucket name
bucket name: user-0eb84f80c29b-bucket
 download Confluent.io Amazon S3 Connector and copy it to the S3 bucket
create directory where we will save our connector 
mkdir kafka-connect-s3 && cd kafka-connect-s3
download connector from Confluent
wget https://d1i4a15mxbxib1.cloudfront.net/api/plugins/confluentinc/kafka-connect-s3/versions/10.0.3/confluentinc-kafka-connect-s3-10.0.3.zip
2. copy connector to our S3 bucket
aws s3 cp ./confluentinc-kafka-connect-s3-10.0.3.zip s3://<BUCKET_NAME>/kafka-connect-s3/
3. Create a custom plugin in the MSK Connect
This was created via the MSK UI console.
4. Create a connector with MSK connect
Now that you have built the plugin-connector pair, data passing through the IAM authenticated cluster, will be automatically stored in the designated S3 bucket.
### Milestone 5: Batch Processing: configuring an API in API Gateway
To replicate the Pinterest's experimental data pipeline we will need to build our own API. This API will send data to the MSK cluster, which in turn will be stored in an S3 bucket, using the connector we have build in the previous milestone.
TASK 1: Build a Kafka REST proxy integration method for the API
SUBTASKS:
1. Create a resource that allows you to build a proxy integration for your API.
2. For the above created resource, create a HTTP ANY method. When setting up the Endpoint URL
Endpoint URL: http://ec2-52-90-167-165.compute-1.amazonaws.com:8082/{proxy}
By creating a proxy resource with the {proxy+} parameter and the ANY method, you can provide your integration with access to all available resources.
3. Deploy the API and make a note of the Invoke URL
TASK 2: Set up the Kafka REST proxy on the EC2 client 
SUBTASKS:
1. First, install the Confluent package for the Kafka REST Proxy on your EC2 client machine. 
Commands:
sudo wget https://packages.confluent.io/archive/7.2/confluent-7.2.0.tar.gz
tar -xvzf confluent-7.2.0.tar.gz 
To enable the downloaded REST proxy to connect to the MSK cluster. We need to update the confluent-7.2.0/etc/kafka-rest/kafka-rest.properties file, with the corresponding Boostrap server string and Plaintext Apache Zookeeper connection string respectively.
2. Allow the REST proxy to perform IAM authentication to the MSK cluster by modifying the kafka-rest.properties file. 
The below needs to be added to the kafka-rest.properties file.
# Sets up TLS for encryption and SASL for authN.
client.security.protocol = SASL_SSL

# Identifies the SASL mechanism to use.
client.sasl.mechanism = AWS_MSK_IAM

# Binds SASL client implementation.
client.sasl.jaas.config = software.amazon.msk.auth.iam.IAMLoginModule required awsRoleArn="Your Access Role";

# Encapsulates constructing a SigV4 signature based on extracted credentials.
# The SASL client bound by "sasl.jaas.config" invokes this class.
client.sasl.client.callback.handler.class = software.amazon.msk.auth.iam.IAMClientCallbackHandler
3. Start the REST proxy on the EC2 client machine. 
navigate to the confluent-7.2.0/bin folder, and then run the following command:
./kafka-rest-start /home/ec2-user/confluent-7.2.0/etc/kafka-rest/kafka-rest.properties
If everything went well, and your proxy is ready to received requests from the API, you should see a INFO Server started, listening for requests... in your EC2 console.
TASK 3: Send data to the API
You are ready to send data to your API, which in turn will send the data to the MSK Cluster using the plugin-connector pair previously created. 
API Gateway -> Rest proxy -> EC2 cluster -> MSK kafka connector -> S3 bucket
Ensure that the Request paths has been set within the 'any' Method request.
### Milestone 6: Batch Processing Databricks
Task 1: set your own Databricks account
Task 2: Mount a S3 bucket to Databricks
In order to clean and query your batch data, you will need to read this data from your S3 bucket into Databricks. To do this, you will need to mount the desired S3 bucket to the Databricks account. 

When reading in the JSONs from S3, make sure to include the complete path to the JSON objects, as seen in your S3 bucket (e.g topics/<your_UserId>.pin/partition=0/). 

You should create three different DataFrames:
df_pin for the Pinterest post data
df_geo for the geolocation data
df_user for the user data.

### Milestone 7: Batch Processing Databricks
Here we used spark to clean the three datasets and run some queries to draw insights from the dataset.
For instance, we were able to discover the most popular category to post for each year between 2018 and 2022. 

### Milestone 8: Batch Processing: AWS MWAA
Task 1: Create and upload a DAG to a MWAA environment
Task 2: Trigger a DAG that runs a Databricks Notebook
Amazon Managed Workflows for Apache Airflow (MWAA) is a managed service that was designed to help you integrate Apache Airflow straight in the cloud, with minimal setup and the quickest time to execution. Apache Airflow is a tool used to schedule and monitor different sequences of processes and tasks, referred to as workflows. In this project MWAA was used to automate the scheduling and running the batch jobs on Databricks. The jobs have been defined to run daily, the configuration details are specified in the file 0eb84f80c29b_dag.py. DAG is a directed acyclic graph (DAG) that manages the running of the batch processing databricks notebook.

### Milestone 9: Stream Processing: AWS Kinesis
Task 1: Create data streams using Kinesis Data Streams
Using Kinesis Data Streams create three data streams, one for each Pinterest table. 

Your AWS account has only been granted permissions to create and describe the following streams:
streaming-0eb84f80c29b-pin
streaming-0eb84f80c29b-geo
streaming-0eb84f80c29b-user




