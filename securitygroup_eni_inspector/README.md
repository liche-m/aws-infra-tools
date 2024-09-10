# Security Group ENI Inspector

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
