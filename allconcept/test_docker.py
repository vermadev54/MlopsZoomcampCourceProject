import requests
import json


event ={
    "Records": [
        {
        "kinesis": {
            "kinesisSchemaVersion": "1.0",
            "partitionKey": "1",
            "sequenceNumber": "49632672741856698858034338568813035242133890721111867394",
            "data": "eyJwcm9maWxlIjogeyJDdXN0b21lcl9BZ2UiOiA0NSwgIkdlbmRlciI6ICJNIiwgIkRlcGVuZGVudF9jb3VudCI6IDMsICJFZHVjYXRpb25fTGV2ZWwiOiAiSGlnaCBTY2hvb2wiLCAiTWFyaXRhbF9TdGF0dXMiOiAiTWFycmllZCIsICJJbmNvbWVfQ2F0ZWdvcnkiOiAiJDYwSyAtICQ4MEsiLCAiQ2FyZF9DYXRlZ29yeSI6ICJCbHVlIiwgIk1vbnRoc19vbl9ib29rIjogMzksICJUb3RhbF9SZWxhdGlvbnNoaXBfQ291bnQiOiA1LCAiTW9udGhzX0luYWN0aXZlXzEyX21vbiI6IDEsICJDb250YWN0c19Db3VudF8xMl9tb24iOiAzLCAiQ3JlZGl0X0xpbWl0IjogMTI2OTEuMCwgIlRvdGFsX1Jldm9sdmluZ19CYWwiOiA3NzcsICJBdmdfT3Blbl9Ub19CdXkiOiAxMTkxNC4wLCAiVG90YWxfQW10X0NobmdfUTRfUTEiOiAxLjMzNSwgIlRvdGFsX1RyYW5zX0FtdCI6IDExNDQsICJUb3RhbF9UcmFuc19DdCI6IDQyLCAiVG90YWxfQ3RfQ2huZ19RNF9RMSI6IDEuNjI1LCAiQXZnX1V0aWxpemF0aW9uX1JhdGlvIjogMC4wNjF9LCAicHJvZmlsZV9pZCI6IDEwfQ==",
            "approximateArrivalTimestamp": 1661424222.822
        },
        "eventSource": "aws:kinesis",
        "eventVersion": "1.0",
        "eventID": "shardId-000000000000:49632672741856698858034338568813035242133890721111867394",
        "eventName": "aws:kinesis:record",
        "invokeIdentityArn": "arn:aws:iam::818606151817:role/lambda-kinesis-role",
        "awsRegion": "us-east-1",
        "eventSourceARN": "arn:aws:kinesis:us-east-1:818606151817:stream/profile_predictions"
        }
    ]
    }

url = 'http://localhost:8080/2015-03-31/functions/function/invocations'
actual_response = requests.post(url, json=event).json()
print(actual_response)