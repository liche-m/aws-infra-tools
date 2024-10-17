import os
import json
import logging
import boto3
import botocore.exceptions

logger = logging.getLogger()
logger.setLevel(logging.INFO)

lambda_client = boto3.client("lambda", region_name=os.environ['region_name'])


def client_error_handling(error, lambda_function, lambda_api):
    """
    Logs specific error messages for each of the following AWS client errors:
        - ResourceNotFoundException
        - ServiceException
        - InvalidParameterValueException
        - TooManyRequestsException
        - ResourceConflictException
    """

    if error.response['Error']['Code'] == "ResourceNotFoundException":
        logger.error(
            "Error Code: ResourceNotFoundException\n"
            "Error: The Lambda Function %s does not exist.\n"
            "HTTP Status Code: 404", lambda_function)
    elif error.response['Error']['Code'] == "ServiceException":
        logger.error(
            "Error Code: ServiceException\n"
            "Error: The AWS Lambda service encountered an internal error.\n"
            "HTTP Status Code: 500")
    elif error.response['Error']['Code'] == "InvalidParameterValueException":
        logger.error(
            "Error Code: InvalidParameterValueException\n"
            "Error: One of the parameters in the request is not valid.\n"
            "HTTP Status Code: 400")
    elif error.response['Error']['Code'] == "TooManyRequestsException":
        logger.error(
            "Error Code: TooManyRequestsException\n"
            "Error: Too many requests made to the %s API. Please try again later.\n"
            "HTTP Status Code: 429", lambda_api)
    elif error.response['Error']['Code'] == "ResourceConflictException":
        error_message = error.response['Error']['Message']
        logger.error(
            "Error Code: ResourceConflictException\n"
            "Error: %s\n"
            "HTTP Status Code: 409", error_message)
    else:
        logger.error(error)


def get_function_versions(lambda_function):
    """
    - This function gets the Versions for the provided Lambda Function ARN.
    - The 'list_versions_by_function' API retrieves the Versions for the Lambda Function.
    - The qualifier is extracted from the response and stored in the 'versions' list.
    """

    versions = []

    try:

        logger.info("Retrieving Lambda Function versions...")
        paginator = lambda_client.get_paginator('list_versions_by_function')
        lambda_iterator = paginator.paginate(FunctionName=lambda_function)

        for items in lambda_iterator:
            for version in items['Versions']:
                versions.append(version['Version'])

    except botocore.exceptions.ClientError as error:

        client_error_handling(error, lambda_function, "ListVersionsByFunction")
        raise error

    return versions


def delete_older_versions(lambda_function, versions_list):
    """
    This function performs the following tasks:
        - Gets the aliases (list_aliases) for the provided Lambda Function ARN.
        - Determines which Function Version the alias is pointing to.
        - Removes the Function Version from the versions_list.
        - Deletes the remaining Function Versions in the versions_list.
    """

    lambda_versions = versions_list
    original_length = len(lambda_versions)
    aliases = []

    logger.info("Getting alias information...")

    try:

        response = lambda_client.list_aliases(
            FunctionName=lambda_function
        )

        aliases = response.get('Aliases', [])

        if aliases:
            for alias in aliases:
                logger.info(
                    "Alias: %s ----------> Function Version: %s",
                    alias['Name'],
                    alias['FunctionVersion'])
                if alias.get('FunctionVersion', '') in lambda_versions:
                    lambda_versions.remove(alias.get('FunctionVersion', ''))

    except botocore.exceptions.ClientError as error:

        client_error_handling(error, lambda_function, "ListAliases")
        raise error

    logger.info("Removing versions that have an alias pointing to it...")

    if len(lambda_versions) < original_length:
        logger.info(
            "Revamped list of Lambda Function versions: %s",
            lambda_versions)

    if len(lambda_versions) == 0:
        logger.info("Nothing to delete here.")

    logger.info("Start Version: %s", int(lambda_versions[0]))
    logger.info("Last Version: %s", int(lambda_versions[-1]))

    for index, version in enumerate(lambda_versions):

        try:

            response = lambda_client.delete_function(
                FunctionName=lambda_function,
                Qualifier=str(version)
            )

            logger.info(
                "Successfully deleted: %s:%s",
                lambda_function,
                version)

        except botocore.exceptions.ClientError as error:

            client_error_handling(error, lambda_function, "DeleteFunction")
            raise error


def lambda_handler(event, context):
    """
    The AWS Handler function contains the logic to call the above functions.
    """

    lambda_versions = []

    for key, function_name in event.items():

        logger.info("Processing Lambda Function: %s", function_name)

        try:
            lambda_versions = get_function_versions(function_name)
            lambda_versions.remove('$LATEST')
            logger.info("Lambda Function versions: %s", lambda_versions)
        except Exception:
            lambda_versions = None
            pass

        if lambda_versions is None:
            print()

        elif len(lambda_versions) >= 1:

            print(lambda_versions)

            try:
                delete_older_versions(function_name, lambda_versions)
                print()
            except Exception:
                pass

        else:
            logger.info("Nothing to delete here: %s", lambda_versions)

    return {
        'statusCode': 200,
        'body': json.dumps('Code executed successfully!')
    }
