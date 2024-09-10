# Security Group ENI Inspector

<br>

## Description

This script is designed to run on an AWS Lambda Function. The Lambda Function expects an event that contains Security Group IDs, and conforms to the following structure:

```
{
  "sg1": "sg-0f813c42c4c55643b",
  "sg2": "sg-0a84a401c5bf6ef9d",
  "sg3": "sg-0e4890977444a19e3"
}
```

When the Lambda Function is invoked, it will retrieve information about the ENI associations for each Security Group ID. It also checks whether the provided Security Groups are referenced by any other Security Group in the specified AWS region.

<br>

## Key Features
- Retrieves the ENI associations for the specified Security Group.
- Identifies which Security Groups in the specified AWS region reference the target Security Groups.

<br>

## Lambda Function Requirements

| Runtime | Memory | Timeout | Environment Variables |
| ------- | ------ | ------- | --------------------- |
| Python 3.10 | 1024 MB | 15 minutes (900 seconds) | Key: region_name <br> Value: <aws_region> <br><br> Example: `eu-west-1` |

<br>

## Lambda Execution Role

The Lambda Execution Role must contain the `AWSLambdaBasicExecutionRole` policy, as well as permissions to call the following APIs:

- `ec2:DescribeNetworkInterfaces`
- `ec2:DescribeSecurityGroups`

<br>

## Usage
### Event Structure

The Lambda Function expects an event that contains Security Group IDs. The event must be formatted as a dictionary with the Security Group IDs as values as follows:

```
{
  "sg1": "sg-0f813c42c4c55643b",
  "sg2": "sg-0a84a401c5bf6ef9d",
  "sg3": "sg-0e4890977444a19e3"
}
```

<br>

## Script Functions

| Function Name | Details | Args | Returns | Raises | Logs |
| ------------- | ------- | ---- | ------- | ------ | ---- |
| `sg_to_eni_mapper` | Retrieve and log information about ENI (Elastic Network Interfaces) associations for a specified Security Group. <br><br> *This function performs the following operations:* <br><br> 1. Retrieves and logs the name of the Security Group. <br><br> 2. Retrieves and logs the ENIs associated to the Security Group. <br><br> 3. Returns a dictionary that includes a list of ENI IDs associated with the specified Security Group, and the Security Group ID itself. | `securitygroup_id (str)` <br><br> The ID of the Security Group for which to retrieve ENI associations and Security Group references. | `dict`: A dictionary containing: <br><br> - `eni_ids (list(str))`: A list of ENIs associated with the specified Security Group. <br> - `securitygroup_id (str)`: The ID of the successfully processed Security Group. | Exception: Re-raises any exceptions encountered while retrieving the Security Group name or ENI associations. Exceptions are logged with error details. | `[INFO]`: Logs details about the Security Group and its associated ENIs. <br><br> `[ERROR]`: Logs any errors encountered while retrieving the Security Group details or ENI associations. |
| `main` | Main function to process the event and orchestrate the necessary operations. <br><br> *This function performs the following operations:* <br><br> 1. Iterates over the Security Group IDs provided in the event. <br><br> 2. Calls `sg_to_eni_mapper` for each Security Group ID to retrieve the ENI associations. <br><br> 3. Collects the Security Group IDs for which the ENI associations were successfully retrieved. <br><br> 4. Calls `check_sg_references` to determine which Security Groups in the specified AWS region reference the collected Security Groups, stored in `target_sgs`. <br><br> 5. Logs information about the target Security Groups. | `event (dict)` | `None` | `None` | `[INFO]`: Logs details about the target *(collected)* Security Groups. |






|  |  |  |  |  |  |










  
