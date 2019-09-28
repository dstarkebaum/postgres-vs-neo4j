#!/bin/bash

#export KEY_NAME = david-IAM-keypair
#export GROUP = "postgresql-sg"

aws ec2 run-instances \
--image-id ami-06f2f779464715dc5 \
--count 1 \
--instance-type m5.large \
--key-name david-IAM-keypair \
--security-groups "postgresql-sg" \
--region us-west-2 \
--user-data postgres_setup-v2.sh
#--query "Instances[*].InstanceId" \

#ssh -i ~/.ssh/david-IAM-keypair.pem ubuntu@ec2-34-219-251-62.us-west-2.compute.amazonaws.com
