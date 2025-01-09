from datetime import datetime, timedelta, timezone
import json
import csv
import logging
import os
import boto3
from botocore.exceptions import ClientError

# Boto3 clients
cloudwatch_client = boto3.client("cloudwatch")
lambda_client = boto3.client("lambda", region_name="eu-west-1")
s3_client = boto3.client("s3")

# Global variables
utc = timezone.utc
file_path = "/tmp/idle-lambda-functions.csv"


def get_lambda_functions():
    """
    - This function gets a list of the Lambda Functions in eu-west-1.
    - It makes a separate list containing the Lambda Function names.
    """

    # Store the names of the Lambda Functions.
    all_functions = []

    benchmark_date = datetime.now(utc) - timedelta(days=90)
    date_format = "%Y-%m-%dT%H:%M:%S.%f%z"

    # Paginator for the list_functions API.
    paginator = lambda_client.get_paginator("list_functions")
    lambda_iterator = paginator.paginate()

    # Iterate through listed functions and store the FunctionName in
    # all_functions.
    for items in lambda_iterator:
        for function in items["Functions"]:

            last_modified = datetime.strptime(
                function["LastModified"], date_format)

            # Only add Lambda Functions that were created >= 90 days ago.
            if last_modified <= benchmark_date:
                all_functions.append(function["FunctionName"])

    # Print to CloudWatch logs.
    print("Number of Lambda Functions:", len(all_functions))
    print("List of Lambda Functions:", all_functions)

    return all_functions


def get_invocation_data(lambda_function):
    """
    - This function gets the invocation data for the past 90 days for a Lambda Function.
    - Period = 86 400 seconds (1 day)
    - The EndTime is today's date.
    - The StartTime is the date 90 days before today.
    """

    response = cloudwatch_client.get_metric_data(
        MetricDataQueries=[
            {
                "Id": "getInvocationData",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/Lambda",
                        "MetricName": "Invocations",
                        "Dimensions": [
                            {"Name": "FunctionName", "Value": f"{lambda_function}"}
                        ],
                    },
                    "Period": 86400,
                    "Stat": "Sum",
                },
                "ReturnData": True,
            },
        ],
        StartTime=datetime.now(utc) - timedelta(days=90),
        EndTime=datetime.now(utc)

    )

    return response


def unused_lambda_functions(response, lambda_function):
    """
    - A Lambda Function is idle if it has not been invoked for 3 months.
    - This function determines whether or not a Lambda Function is idle.
    """

    # Store the Function name of the idle/unused Lambda Function.
    idle_lambda_function = None

    # Timestamps for the Lambda Function invocations.
    timestamps = response["MetricDataResults"][0]["Timestamps"]

    # The sum of the invocations for each timestamp.
    values = response["MetricDataResults"][0]["Values"]

    # Empty lists indicate that the Lambda Function has not been invoked for 3
    # months.
    if len(timestamps) == 0 and len(values) == 0:
        idle_lambda_function = lambda_function

    return idle_lambda_function


def show_tags(idle_lambda_function):
    """
    - This function retrieves the tags configured for the idle Lambda Function.
    - In particular, the Application, Team and Service tags.
    """

    # Store the name and tags (if any) of the idle Lambda Function.
    idleness = {"Idle Lambda Function": idle_lambda_function}

    # Store the tags for the idle Lambda Function.
    tags_dict = {}

    response = lambda_client.get_function(FunctionName=idle_lambda_function)

    # Check whether Tags is in the response.
    if "Tags" in response:

        # Check for standard tags on the idle Lambda Function.
        contains_standard_tags = False
        standard_tags = ["Application", "Team", "Service"]

        # Strip the leading and trailing white spaces from each key-value pair.
        tags = response["Tags"]
        tags = {key.strip(): value.strip() for key, value in tags.items()}

        for tag in standard_tags:

            """
            - Set contains_standard_tags to True if the Lambda Function has a standard tag.
            - Add the tag to the tags dictionary (tags_dict).
            """

            if tag in tags:
                contains_standard_tags = True
                tags_dict[tag] = tags[tag]

        if contains_standard_tags:
            # Add the tags dictionary to idleness if there are standard tags.
            idleness["Tags"] = tags_dict
        else:
            # The Lambda Function has no standard tags.
            idleness[
                "Tag Status"] = f"No Application/Team/Service tag configured for:{idle_lambda_function}"

    else:
        # The Lambda Function does not have any tags at all.
        idleness["Tag Status"] = f"No tags configured for:{idle_lambda_function}"

    return idleness


def write_to_csv(idleness_list):
    """
    - This function creates a csv file in the /tmp directory.
    - It takes the data from the idleness_list and writes it to the csv file.
    """

    headers = [
        "Idle Lambda Function",
        "Application",
        "Team",
        "Service",
        "Tag Status"]

    flattened_data = []

    for item in idleness_list:
        flattened_entry = {
            "Idle Lambda Function": item.get("Idle Lambda Function"),
            "Application": item.get("Tags", {}).get("Application", ""),
            "Team": item.get("Tags", {}).get("Team", ""),
            "Service": item.get("Tags", {}).get("Service", ""),
            "Tag Status": item.get("Tag Status", "")
        }

        flattened_data.append(flattened_entry)

    try:

        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(flattened_data)
        return True

    except Exception as e:

        print(f"Error writing to CSV file: {e}")
        return False


def upload_to_s3():
    """
    This function uploads the csv file to a S3 Bucket.
    """

    s3_bucket = os.environ.get("s3_bucket")

    # Get the current date and time.
    current_date = datetime.now()
    file_name = current_date.strftime(
        "%Y-%m-%dT%H:%M:%S") + "-" + "idle-lambda-functions.csv"

    try:
        s3_client.upload_file(file_path, s3_bucket, file_name)
    except ClientError as e:
        logging.error(e)
        print("File failed to be uploaded to S3 Bucket.")

    print(f"File ({file_name}) successfully uploaded to S3 Bucket!")


def main():
    """
    - This function contains the logic to call the above functions.
    """

    # Store dictionary objects. Dictionary object = Name + Tag.
    idle_lambdas = []

    # Get a list of all the Lambda Functions in the eu-west-1 region.
    all_lambda_functions = get_lambda_functions()

    # Iterate through the list of Lambda Functions.
    for lambda_function in all_lambda_functions:

        # Get the invocation data for each Lambda Function.
        response = get_invocation_data(lambda_function)

        # Determine if the Lambda Function is idle/unused.
        idle_lambda_function = unused_lambda_functions(
            response, lambda_function)

        if idle_lambda_function is not None:

            # Get the necessary tags configured for the idle Lambda Function.
            idle_function = show_tags(idle_lambda_function)
            idle_lambdas.append(idle_function)

    # Print to CloudWatch logs.
    print("Number of idle Lambda Functions:", len(idle_lambdas))
    print("List of idle Lambda Functions:", json.dumps(idle_lambdas))

    csv_file_status = write_to_csv(idle_lambdas)

    if csv_file_status:
        print(f"CSV file ({file_path}) successfully created!")
        upload_to_s3()
    else:
        print("CSV file failed to create.")


def lambda_handler(event, context):

    # Call the main function.
    main()
