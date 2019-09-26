#!/bin/bash

# Create a Security group for neo4j
export GROUP = "neo4j-sg"

# provide the name of your ssh key (usually located in ~/.ssh/KEY_NAME.pem)
export KEY_NAME = david-IAM-keypair

# lookup your public IP address from opendns.com
# https://www.opendns.com/about/
# https://www.linuxtrainingacademy.com/determine-public-ip-address-command-line-curl/
# https://linux.die.net/man/1/dig
# export MY_IP=$(dig +short myip.opendns.com @resolver1.opendns.com)
export MY_IP=$(curl checkip.amazonaws.com)

# NOTE: in unix you can evaluate a command and store the output with:
# MyVar=$(command)

# If you haven't done it already, run aws configure and store your
# credentials and config settings.
# This will store the following information:
#
# ~/.aws/credentials
# [default]
# aws_access_key_id = XXXXXXXXXXXXXXXXXXXX
# aws_secret_access_key = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#
# ~/.aws/config
# [default]
# output = text
# region = us-west-2
#
# uncomment this comand:
# aws configure
#
# Enter the following information:
# AWS Access Key ID [None]: $AWS_ACCESS_KEY_ID
# AWS Secret Access Key [None]: $AWS_SECRET_ACCESS_KEY
# Default region name [None]: $AWS_DEFAULT_REGION
# Default output format [None]: json

# NOTE: I recommend that you set your detault output format to JSON!
# "Why?" You might ask?
# We can use JSON to describe all of the parameters to any AWS CLI command!
# For example:
# aws ec2 run-instances --cli-input-json file://ec2runinst.json
# https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-skeleton.html

# Create a new security group to assign to our instance
# See more documentation about EC2 security groups here:
# https://docs.aws.amazon.com/cli/latest/userguide/cli-services-ec2-sg.html
aws ec2 create-security-group \
  --group-name $GROUP \
  --description "Neo4j security group"

# open up the necessary ports for neo4j to function: ( SSH, HTTP, HTTPS, and Bolt ports )
# https://docs.aws.amazon.com/cli/latest/reference/ec2/authorize-security-group-ingress.html
for port in 22 7474 7473 7687; do
  # NOTE: This congifuration is NOT RECOMMENDED, because it opens all internet
  # (0.0.0.0/0), so it provides no security from unauthorized access!
  # aws ec2 authorize-security-group-ingress --group-name $GROUP --protocol tcp --port $port --cidr 0.0.0.0/0

  #  instead, restrict traffic to just MY_IP address!!
  aws ec2 authorize-security-group-ingress --group-name $GROUP --protocol tcp --port $port --cidr $MY_IP/32
done

# Locate images published by neo4j
# Not recommended at moment, because of security concerns (how to verify AMI's?)
# Instead, lets install neo4j on native Ubunto!
#aws ec2 describe-images --region us-west-2 --owner 385155106615 --query "Images[*].{ImageId:ImageId,Name:Name}"

# ami-06f2f779464715dc5 == Ubuntu Server 18.04 LTS (HVM), SSD Volume Type (64-bit x86)
# Root device type: EBS, Virtualization type: HVM, ENA Enabled: Yes
aws ec2 run-instances \
  --image-id ami-06f2f779464715dc5 \
  --count 1 \
  --instance-type m4.large \
  --key-name $KEY_NAME \
  --security-groups $GROUP \
  --query "Instances[*].InstanceId" \
  --region us-west-2 \
  --user-data neo4j_setup.sh
# NOTE: user-data tag lets us automatically run a bash on startup!
# This is a very convenient place to put installation commands!


# once we get our instanceID, we can find out more details, such as PublicDnsName
aws ec2 describe-instances \
  --instance-ids [InstanceId] \
  --query "Reservations[*].Instances[*].PublicDnsName" \
  --region us-west-2

#aws ec2 describe-instances --query "Reservations[*].Instances[*].PublicDnsName" --region us-west-2

# Next we login to our new instance by ssh
# NOTE: for added security we can use SSH Tunneling and port forwarding
# https://www.ssh.com/ssh/tunneling/
ssh -i $KEY_NAME.pem ubuntu@[PublicDnsName]

# login with browser to http://localhost:7474/browser/
# default Neo4j password: ‘neo4j’

# test the setup by insert data to neo4j database using REST API:
#curl -H "Accept: application/json; charset=UTF-8" --user "neo4j:neo4j" -H \
#"Content-Type: application/json" -X POST http://localhost:7474/db/data/cypher -d \
#'{ "query" : "CREATE (n:Person { name : {name} }) RETURN n", "params" : \
#{ "name" : "Shubham" } }'

# add another entry:
#curl -H "Accept: application/json; charset=UTF-8" --user "neo4j:neo4j" -H \
#"Content-Type: application/json" -X POST http://localhost:7474/db/data/cypher -d \
#'{ "query" : "CREATE (n:Person { name : {name} }) RETURN n", "params" : \
#{ "name" : "LinuxHint" } }'
