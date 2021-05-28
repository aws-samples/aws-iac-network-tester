import logging
import botocore
import boto3

ec2Client = boto3.client('ec2')


def lambda_handler(event, context):
    inflight_network_test_details = event['globalvars']['routedetails']['inflightroutetotest']['inflightroutes']

    logging.info("inflight network tests >> " +
                 str(inflight_network_test_details))

    updated_next_route_to_test = []
    runningtestscount = 0

    # Populating Test Results
    if inflight_network_test_details:
        for test_detail in inflight_network_test_details:
            logging.info("test detail >> " + str(test_detail))
            try:
                response = ec2Client.describe_network_insights_analyses(
                    NetworkInsightsAnalysisIds=[
                        test_detail['NetworkInsightsAnalysisId']],
                    NetworkInsightsPathId=test_detail['NetworkInsightsPathId']
                )
            except botocore.exceptions.ClientError as error:
                logging.error(
                    "Call to describe_network_insights_analyses failed")
                raise error

            test_status = response['NetworkInsightsAnalyses'][0]['Status']

            updated_route_details = {
                'Source': test_detail['Source'],
                'Destination': test_detail['Destination'],
                'RouteTag': test_detail['RouteTag'],
                'NetworkInsightsPathId': test_detail['NetworkInsightsPathId'],
                'NetworkInsightsAnalysisId': test_detail['NetworkInsightsAnalysisId'],
                'Status': test_status
            }

            if (test_status == 'succeeded'):
                updated_route_details['NetworkPathFound'] = response['NetworkInsightsAnalyses'][0]['NetworkPathFound']
                if not updated_route_details['NetworkPathFound']:
                    updated_route_details['Explanations'] = response['NetworkInsightsAnalyses'][0]['Explanations']

            if(test_status == 'running'):
                runningtestscount += 1

            updated_next_route_to_test.append(updated_route_details)

        return {
            "inflightroutes": updated_next_route_to_test,
            "runningtestscount": runningtestscount

        }
