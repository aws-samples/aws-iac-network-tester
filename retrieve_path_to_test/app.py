import json
import logging
import botocore
import boto3

cloudFormationClient = boto3.client('cloudformation')
ec2Client = boto3.client('ec2')


def lambda_handler(event, context):

    currentRouteIndex = event['globalvars']['routedetails']['currentrouteindex']
    testBatchSize = event['globalvars']['routedetails']['testbatchsize']
    allRoutes = {}

    if(currentRouteIndex == 0):
        cloudFormationStackName = event['stackName']
        routeToTestOutputKey = event['routeToTestOutputKey']
        logging.info("stack name>> " + str(cloudFormationStackName))
        logging.info("route to test output key>> " + str(routeToTestOutputKey))

        if cloudFormationStackName and routeToTestOutputKey:
            try:
                cfnStack = cloudFormationClient.describe_stacks(
                    StackName=cloudFormationStackName
                )
            except botocore.exceptions.ClientError as error:
                logging.error("Call to describe_stacks failed")
                raise error

            stackDetails = cfnStack['Stacks'][0]
            try:
                allRoutes = json.loads(get_network_path_from_cfnoutput(
                    stackDetails,
                    routeToTestOutputKey
                ))
            except botocore.exceptions.ClientError as error:
                logging.error("Call to get_network_path_from_cfoutput failed")
                raise error

        else:
            logging.error(
                "The two parameters stackNames and routeToTestOutputKey are required")
            raise botocore.exceptions.ClientError

    else:
        allRoutes = event['globalvars']['routedetails']['allroutes']

    routeDetails = inflight_routes_to_test(
        allRoutes, currentRouteIndex, testBatchSize)

    return routeDetails


def get_network_path_from_cfnoutput(stackDetails, outputName):
    completeStatus = ['CREATE_COMPLETE', 'IMPORT_COMPLETE', 'UPDATE_COMPLETE']
    if stackDetails['StackStatus'] in completeStatus:
        stackOuputs = stackDetails['Outputs']
        logging.info("cf outputs >> " + str(stackOuputs))

        for output in stackOuputs:
            if output['OutputKey'] == outputName:
                networkTestDetails = output['OutputValue']
                logging.info("cf output details >> " + str(networkTestDetails))
                return networkTestDetails
        pass


def inflight_routes_to_test(allRoutes, currentRouteIndex, testBatchSize):
    if((currentRouteIndex + testBatchSize) < len(allRoutes)):
        inflightRoutesToTest = allRoutes[currentRouteIndex:(
            currentRouteIndex + testBatchSize)]
        currentRouteIndex += testBatchSize
        isAllRoutesTested = False
    else:
        inflightRoutesToTest = allRoutes[currentRouteIndex:]
        isAllRoutesTested = True

    return {
        "inflightroutetotest": {
            "inflightroutes": inflightRoutesToTest,
            "runningtestscount": 0
        },
        "currentrouteindex": currentRouteIndex,
        "testbatchsize": testBatchSize,
        "isallroutestested": isAllRoutesTested,
        "allroutes": allRoutes,
    }
