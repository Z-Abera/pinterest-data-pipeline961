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