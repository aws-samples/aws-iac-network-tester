import logging


def lambda_handler(event, context):
    logging.info("event>>> " + str(event))

    numberOfTimesToWait = event['analysisWaitCount']
    index = event['globalvars']['timerdetails']['testtimerindex']
    step = event['analysisDuration']

    totalWait = numberOfTimesToWait * step
    index += step

    return {
        "testtimerindex": index,
        "continue": index < totalWait,
    }
