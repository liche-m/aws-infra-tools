# Detect Idle Lambda Functions

## Description

This script is designed to run on an AWS Lambda Function. The Lambda Function does **NOT** expect an event or any type of input. When the Lambda Function is invoked, it will generate a list of Lambda Functions that have not been invoked for the past **90 days**. Thereafter, it will write this data to a **CSV file** and upload the **CSV file** to an Amazon S3 Bucket.

<br>

## Lambda Function Requirements

| Runtime | Memory | Timeout | Environment Variables |
| ------- | ------ | ------- | --------------------- |
| Python 3.10 | 1024 MB | 15 minutes (900 seconds) | Key: region_name <br> Value: <aws_region> <br><br> Example: `eu-west-1` |

<br>

## Lambda Execution Role

The Lambda Execution Role must contain the `AWSLambdaBasicExecutionRole` policy, as well as permissions to call the following APIs:

- `cloudwatch:GetMetricData`
- `lambda:GetFunction`
- `lambda:ListFunctions`
- `s3:PutObject`

<br>

## Script Functions

| Function Name | Details | Args | Returns | Logs |
| ------------- | ------- | ---- | ------- | ---- |
| `get_lambda_functions` | 1. Gets a list of all the Lambda Functions in `eu-west-1` by calling the `ListFunctions` API. <br><br> 2. Generates a separate list that only contains the Lambda Function names *(and no other metadata)*. <br><br> 3. Returns a `list` called `all_functions` containing the Lambda Function names. | None | `all_functions: list(string)` - A list containing the Lambda Function names. | 1. Number of Lambda Functions in `eu-west-1`. <br><br> 2. Lambda Function names stored in `all_functions`. |
| `get_invocation_data` | 1. Gets the `Invocations` data for a Lambda Function for the past **90 days**. <br><br> 2. Returns a `dictionary` called `response` that contains the `Invocations` data for a particular Lambda Function. | `lambda_function: str` - The name of the Lambda Function. | `response: dict` - A dictionary containing the `Invocations` data for a particular Lambda Function. | None |
| `unused_lambda_functions` | Determines whether or not a Lambda Function is **idle**. A Lambda Function is considered to be idle if it has not been invoked for the past **90 days**. | `response: dict` - A dictionary containing the `Invocations` data for a particular Lambda Function. <br><br> `lambda_function: str` - The name of the Lambda Function. | `idle_lambda_function: str` - Set to `None` or the name of the idle Lambda Function. | None |
| `show_tags` | 1. Retrieves the `Application`, `Service` and `Team` tags configured for the idle Lambda Function. <br><br> 2. Returns a dictionary called `idleness` that contains the name of the idle Lambda Function along with its associated tags. | `idle_lambda_function: str` - The name of the idle Lambda Function. | `idleness: dict` - A dictionary containing the name of the idle Lambda Function and its associated tags. | None |
| `write_to_csv` | Takes the data from `idleness_list` and writes it to a CSV file, stored in the `/tmp` directory. | `idleness_list: list(dict)` - A list of dictionaries containing the name of the idle Lambda Function and its associated tags. | `bool` - Returns `True` if the writing of data to the CSV file is successful, and `False` if otherwise. | Any exception encountered when writing data to the CSV file. |
| `upload_to_s3` | Uploads the CSV file stored in `/tmp` to the S3 Bucket. | None | None | 1. The successful upload of the CSV file to the S3 Bucket. <br><br> 2. Any exception encountered when uploading the CSV file to the S3 Bucket. |
| `main` | Contains the logic to call the aforementioned functions. | None | None | 1. Number of idle Lambda Functions. <br><br> 2. List of idle Lambda Functions and their associated tags. |
| `lambda_handler` | 1. Calls the function: `main` <br><br> 2. Called when the Lambda Function is invoked. | `event: dict` - Not used in this script. <br><br> `context(LambdaContext)` - Not used in this script. | None | None |

<br>
   
## Author
#### Author: Liché Moodley
#### Email: moodleyliche@gmail.com
