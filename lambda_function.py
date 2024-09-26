# Serialize

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket = event['s3_bucket']
    
    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    s3.download_file(bucket, key, "/tmp/image.png")
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }


# Classifier
import json

import boto3

import base64

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2024-09-26-20-47-22-733"
runtime_client = boto3.client('sagemaker-runtime')

def lambda_handler(event, context):

   # Decode the image data
    image = base64.b64decode(event['body']['image_data'])

    # Make a prediction
    invokedEnpointRes = runtime_client.invoke_endpoint(EndpointName=ENDPOINT,ContentType='image/png',Body=image)
    event["inferences"] = json.loads(invokedEnpointRes['Body'].read().decode('utf-8'))

    # Return the inferences
    return {
        'statusCode': 200,
        'body': {
            'image_data': event['body']['image_data'],
            's3_bucket': event['body']['s3_bucket'],
            's3_key': event['body']['s3_key'],
            'inferences': event['inferences']
        }
        
    }

# Filter 
import json
THRESHOLD = .93

def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = event['body']['inferences']
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(list(inferences))>THRESHOLD
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
