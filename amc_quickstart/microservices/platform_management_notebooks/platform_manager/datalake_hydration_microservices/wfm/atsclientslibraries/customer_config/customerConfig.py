# Copyright 2022 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
import pandas as pd

## DynamoDB serialzation
def deserializeDyanmoDBItem(item):
    return {k: TypeDeserializer().deserialize(value=v) for k, v in item.items()}

def set_customer_config(customer_details, TEAM_NAME, ENV):
    dynamodb_client_wr= boto3.resource('dynamodb')
    
    customer_table = dynamodb_client_wr.Table(f'wfm-{TEAM_NAME}-CustomerConfig-{ENV}')
    
    dynamodb_resp_wr = customer_table.put_item(Item=customer_details)
    
    return dynamodb_resp_wr

## DynamoDB scan with pagination
def dump_table(table_name, dynamodb_client_rd):
    results = []
    last_evaluated_key = None
    while True:
        if last_evaluated_key:
            response = dynamodb_client_rd.scan(
                TableName=table_name,
                ExclusiveStartKey=last_evaluated_key
            )
        else: 
            response = dynamodb_client_rd.scan(TableName=table_name)
        last_evaluated_key = response.get('LastEvaluatedKey')
        
        results.extend(response['Items'])
        
        if not last_evaluated_key:
            break
    return results

## retrieve custoemr config table details
def get_customer_config(TEAM_NAME, ENV):
    dynamodb_client_rd= boto3.client('dynamodb')
    dynamodb_resp_rd = dump_table(table_name=f'wfm-{TEAM_NAME}-CustomerConfig-{ENV}', dynamodb_client_rd=dynamodb_client_rd)
    
    cust_dtls_list =[]
    for itm in dynamodb_resp_rd:
        itm_dict = deserializeDyanmoDBItem(itm)
        cust_dtls_list.append(itm_dict)   
        
    df = pd.DataFrame(cust_dtls_list)
    
    return df

## delete a customer config record
def delete_customer_config(customerId, TEAM_NAME, ENV):
    dynamodb_client_wr= boto3.resource('dynamodb')
    
    customer_table = dynamodb_client_wr.Table(f'wfm-{TEAM_NAME}-CustomerConfig-{ENV}')
    
    response = customer_table.delete_item(
        Key = {
            'customerId': customerId
        }
    ) 
    
    return response
    
    
    