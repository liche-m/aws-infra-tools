import json
import os
import boto3

lambda_client = boto3.client("lambda", region_name=os.environ['Region'])


def get_function_versions(lambda_function):
    """
    - This function gets the Versions for the provided Lambda Function ARN.
    - The 'list_versions_by_function' API retrieves the Versions for the Lambda Function.
    - The qualifier is extracted from the response and stored in the 'versions' list.
    """

    versions = []

    paginator = lambda_client.get_paginator('list_versions_by_function')
    lambda_iterator = paginator.paginate(FunctionName=lambda_function)

    for items in lambda_iterator:
        for version in items['Versions']:
            versions.append(version['Version'])

    return versions


def delete_older_versions(lambda_function, versions_list):
    """
    - This function deletes the older published Versions of a Lambda Function.
    - It excludes the $LATEST version: startVersion = int(versions_list[1])
    - It excludes the most recent published Version:
      lastVersion = int(versions_list[len(versions_list) - 2])
    """

    if len(versions_list) > 2:

        start_version = int(versions_list[1])
        last_version = int(versions_list[len(versions_list) - 2])

        print(f"Start Version: {start_version}")
        print(f"Last Version: {last_version}")

        for version in range(start_version, last_version + 1):

            response = lambda_client.delete_function(
                FunctionName=lambda_function,
                Qualifier=str(version)
            )

            print(f"Successfully deleted: {lambda_function}:{version}")

    else:
        print(f"Nothing to delete here: {versions_list}")


def main(event):
    """
    - This function contains the logic to call the other functions defined above.
    """

    for key, function_name in event.items():

        print(f"Processing Lambda Function: {function_name}")
        versions = get_function_versions(function_name)
        print(f"Lambda Function versions: {versions}")
        delete_older_versions(function_name, versions)

        print()


def lambda_handler(event, context):
    """
    - This function is executed when the Lambda Function is invoked.
    """

    main(event)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
