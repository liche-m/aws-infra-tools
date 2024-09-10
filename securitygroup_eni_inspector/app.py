import os
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2_client = boto3.client('ec2', region_name=os.environ['region_name'])


def sg_to_eni_mapper(securitygroup_id):
    """
    Retrieve and log information about ENI (Elastic Network Interfaces) associations
    for a specified Security Group.
    """

    eni_ids = []

    try:

        sg_response = ec2_client.describe_security_groups(
            GroupIds=[
                securitygroup_id
            ]
        )

        logger.info(
            "Processing Security Group: %s | %s", securitygroup_id, sg_response['SecurityGroups'][0]['GroupName'])

    except Exception as e:
        logger.info("Processing Security Group: %s", securitygroup_id)
        logger.error(
            "There was an issue retrieving details for the Security Group (%s): %s", securitygroup_id, e)
        raise e

    try:

        logger.info("Retrieving ENI associations...")
        response = ec2_client.describe_network_interfaces(
            Filters=[
                {
                    'Name': 'group-id',
                    'Values': [securitygroup_id]
                }
            ]
        )

        if response['NetworkInterfaces'] == []:

            logger.info(
                "No ENI associations found for the Security Group (%s).", securitygroup_id)

        else:

            for eni in response['NetworkInterfaces']:
                eni_ids.append(eni['NetworkInterfaceId'])

            logger.info("%d ENI associations found: %s", len(eni_ids), eni_ids)

    except Exception as e:
        logger.error(
            "There was an issue retrieving the ENI associations for %s: %s", securitygroup_id, str(e))

    return {
        'eni_ids': eni_ids,
        'securitygroup_id': securitygroup_id
    }


def check_sg_references(event_sgs):
    """
    Check which Security Groups in the region are referencing the specified
    Security Groups in event_sgs.
    """

    all_sgs = []          # The SGs in the region.
    referencing_sgs = []  # Store the SGs that reference each sg in event_sgs.

    try:

        logger.info(
            "Retrieving all Security Groups in %s...", os.environ['region_name'])

        # Initialize a paginator for the 'describe_security_groups' API.
        paginator = ec2_client.get_paginator('describe_security_groups')
        page_iterator = paginator.paginate()

        # Iterate over pages and collect all Security Groups.
        for page in page_iterator:
            all_sgs.extend(page['SecurityGroups'])

    except Exception as e:
        logger.error(
            "There was an issue retrieving all Security Groups in %s: %s", os.environ['region_name'], str(e))
        raise e

    for sg in all_sgs:

        sg_id = sg['GroupId']
        inbound_rules = sg['IpPermissions']
        outbound_rules = sg['IpPermissionsEgress']

        inbound_references = False
        outbound_references = False

        for target_sg in event_sgs:

            inbound_references = any(
                any(group_pair.get('GroupId') ==
                    target_sg for group_pair in rule.get('UserIdGroupPairs', []))
                for rule in inbound_rules
            )

            outbound_references = any(
                any(group_pair.get('GroupId') ==
                    target_sg for group_pair in rule.get('UserIdGroupPairs', []))
                for rule in outbound_rules
            )

            if inbound_references or outbound_references:
                referencing_sgs.append({
                    "Target Security Group ID:": target_sg,
                    "Referenced by this Security Group:": sg_id
                })

    if not referencing_sgs:
        logger.info("No Security Group references found.")
    else:
        for item in referencing_sgs:
            logger.info(item)

    return referencing_sgs


def main(event):
    """
    Main function to process the event and orchestrate the necessary operations.
    """

    logger.info("ENI ASSOCIATIONS:")
    result = {}
    target_sgs = []

    for key, securitygroup_id in event.items():
        try:
            result = sg_to_eni_mapper(securitygroup_id)

            if result['securitygroup_id']:
                target_sgs.append(securitygroup_id)

        except Exception:
            pass

    logger.info("SECURITY GROUP ASSOCIATIONS:")
    logger.info("Target Security Groups: %s", target_sgs)
    sg_references = check_sg_references(target_sgs)


def lambda_handler(event, context):
    """
    AWS Lambda Function handler.
    """

    try:

        if len(event) > 0:

            main(event)

            return {
                'statusCode': 200,
                'body': json.dumps('Code executed successfully!')
            }

        else:

            logger.info("No Security Groups specified in the event!")

            return {
                'statusCode': 200,
                'body': json.dumps('Event not processed')
            }

    except Exception as e:

        logger.error("Code did not execute successfully!")

        return {
            'statusCode': 500,
            'body': json.dumps(f'Code did not execute successfully: {str(e)}')
        }
