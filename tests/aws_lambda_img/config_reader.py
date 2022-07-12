""" cfn config reader"""
import os
import boto3
from botocore.exceptions import ClientError
import shutil


VPC = "rsavpc"
REGION = 'us-east-1'
BUCKET_NAME = f"{VPC}-deployment-archive"
STACK_NAME = 'teststack'
DELETE_STACK = False
CREATE_OR_UPDATE = True

with open('cfn/cfn.config') as file:
    props = dict(line.strip().split('=', 1) for line in file)

s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)
if not bucket.creation_date:
    s3.create_bucket(Bucket=BUCKET_NAME)
file_name = 'lambda'
shutil.make_archive(file_name, 'zip', os.getcwd())
response = s3.meta.client.upload_file('./lambda.zip', BUCKET_NAME, f'{file_name}.zip')
code_file = 'https://xyz123-deployment-archive.s3.amazonaws.com/lambda.zip'

# creating cf state
if CREATE_OR_UPDATE:
    response = s3.meta.client.upload_file('./cfn/cftemplate.json', BUCKET_NAME, f'cftemplate.json')
    client = boto3.client('cloudformation', region_name=REGION)
    try:
        response = client.create_stack(StackName='teststack', TemplateURL='https://xyz123-deployment-archive.s3.amazonaws.com/cftemplate.json', Capabilities=['CAPABILITY_NAMED_IAM'])
        print(response)
    except ClientError as exc:
        if exc.response['Error']['Code'] == 'AlreadyExistsException':
            print("User already exists: Updating")
            response = client.update_stack(StackName='teststack',
                                           TemplateURL='https://xyz123-deployment-archive.s3.amazonaws.com/cftemplate.json',
                                           Capabilities=['CAPABILITY_NAMED_IAM'])
            print(response)
        else:
            print("Unexpected error: %s" % exc)


if DELETE_STACK:
    response = client.delete_stack(StackName=STACK_NAME)
    print(response)


