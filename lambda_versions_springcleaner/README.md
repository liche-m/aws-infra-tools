# Lambda Versions Springcleaner

<br>

## Description

This script is designed to run on an AWS Lambda Function. The Lambda Function expects an event that contains Lambda Function ARNs, and conforms to the following structure:

```
{
  "lambda1": "arn:aws:lambda:eu-west-1:444555666777:function:red-velvet-cupcake",
  "lambda2": "arn:aws:lambda:eu-west-1:444555666777:function:chocolate-cupcake",
  "lambda3": "arn:aws:lambda:eu-west-1:444555666777:function:vanilla-cupcake"
}
```

When the Lambda Function is invoked, it will retrieve information about the Versions and Aliases for each Lambda Function ARN. It then deletes the older and unused Versions of the Lambda Function, that do not have an Alias pointing to it.

<br>

## Key Features
- Retrieves information about the Versions and Aliases for the specified Lambda Function ARN.
- Deletes the older and unused Versions of the specified Lambda Function.

<br>

## Lambda Function Requirements

| Runtime | Memory | Timeout | Environment Variables |
| ------- | ------ | ------- | --------------------- |
| Python 3.10 | 1024 MB | 15 minutes (900 seconds) | Key: region_name <br> Value: <aws_region> <br><br> Example: `eu-west-1` |

<br>

## Lambda Execution Role

The Lambda Execution Role must contain the `AWSLambdaBasicExecutionRole` policy, as well as permissions to call the following APIs:

- `lambda:ListAliases`
- `lambda:ListVersionsByFunction`
- `lambda:DeleteFunction`

<br>

## Usage
### Event Structure

The Lambda Function expects an event that contains Lambda Function ARNs. The event must be formatted as a dictionary with the Lambda Function ARNs as values as follows:

```
{
  "lambda1": "arn:aws:lambda:eu-west-1:444555666777:function:red-velvet-cupcake",
  "lambda2": "arn:aws:lambda:eu-west-1:444555666777:function:chocolate-cupcake",
  "lambda3": "arn:aws:lambda:eu-west-1:444555666777:function:vanilla-cupcake"
}
```

<br>

## Script Functions

| Function Name | Details | Args | Returns | Raises | Logs |
| ------------- | ------- | ---- | ------- | ------ | ---- |
| `client_error_handling` | Logs specific error messages for each of the following AWS client errors: <br><br> `ResourceNotFoundException` <br><br> `ServiceException` <br><br> `InvalidParameterValueException` <br><br> `TooManyRequestsException` <br><br> `ResourceConflictException` | `error (str)` - The error that is thrown for a specific AWS Lambda API call. <br><br> `lambda_function (str)` - The ARN of the Lambda Function for which the error was thrown. <br><br> `lambda_api (str)` - The AWS Lambda API call that failed. | `None` | `None` | `[ERROR]` - Logs any errors encountered whilst making calls to the AWS Lambda APIs. |
| `get_function_versions` | 1. Calls the `ListVersionsByFunction` API to retrieve the Versions for the specified Lambda Function ARN. <br><br> 2. Extracts the Versions qualifier from the API response and stores it in the `versions` list. | `lambda_function (str)` - The ARN of the specified Lambda Function. | `versions (list)` - A list of all the Versions associated with the specified Lambda Function. | Exception: Re-raises any exceptions encountered while calling the `ListVersionsByFunction` API. Exceptions are logged with error details. <br><br> **NOTE:** Any exceptions encountered will be propagated to the calling function (i.e. `lambda_handler`) where they will be handled. | `[INFO]` - Logs a statement prior to calling the `ListVersionsByFunction` API. |
| `delete_older_versions` | 1. Calls the `ListAliases` API to retrieve the Aliases for the specified Lambda Function ARN. <br><br> 2. Determines which Function Version(s) the Alias(es) are pointing to. <br><br> 3. Removes the Function Version(s) from the `versions_list`. <br><br> 4. Deletes the older Versions of the Lambda Function specified in the `versions_list`. | `lambda_function (str)` - The ARN of the specified Lambda Function. <br><br> `versions_list (list)` - A list of all the Versions associated with the specified Lambda Function. | `None` | Exception: Re-raises any exceptions encountered while calling the `ListAliases` and `DeleteFunction` APIs. Exceptions are logged with error details. <br><br> **NOTE:** Any exceptions encountered will be propagated to the calling function (i.e. `lambda_handler`) where they will be handled. | `[INFO]` - Logs details about the Versions and Aliases associated with the specified Lambda Function. Logs each Version of the Lambda Function that is deleted. | 
| `lambda_handler` | Contains the logic to call the above functions. | `event (dict)` - An event containing Lambda Function ARNs. <br><br> `context (LambdaContext)` - The context object provided by the AWS Lambda service *(not used in this script)*. | `dict` - A dictionary containing: <br><br> `statusCode (int)` - HTTP status code indicating the result of the code execution. A `200` status code indicates that the code executed successfully. <br><br> *Sample output:* <pre>return {<br>    'statusCode': 200,<br>    'body': json.dumps('Code executed successfully!')<br>}</pre> | `None` | `[INFO]` - Logs details about the Lambda Function being processed. Logs statements above and below each method call. |

<br>

## Setup

1. Navigate to the AWS CloudShell console.
2. Upload `app.py` and `deploy_lambda_versions_springcleaner.sh`:
   - Click on `Actions` ----> `Upload file`.
   - Browse to the location on your pc where the files are stored.
3. Once the files have been uploaded, add execute permissions to `deploy_lambda_versions_springcleaner.sh`:
   `chmod +x deploy_lambda_versions_springcleaner.sh`
4. Run the script to deploy the Lambda Function:
   `./ deploy_lambda_versions_springcleaner.sh`

<br>
   
## Author
#### Author: Liché Moodley
#### Email: lichem@ozow.com
