import boto3, traceback, json
import subprocess
from botocore.exceptions import ClientError
from sflogger import sfLogger
from termcolor import cprint
import os

class awsTester:
    def __init__(self, pkgid, accesskey, secretkey, stoken, region, logger=""):
        self.pkgid = pkgid
        self.accesskey = accesskey
        self.secretkey = secretkey
        self.stoken = stoken
        self.region = region
        self.logger = logger
        
    def configure(self):
        subprocess.call("aws configure set aws_access_key_id %s"%self.accesskey, shell=True)
        subprocess.call("aws configure set aws_secret_access_key %s"%self.secretkey, shell=True)
        if self.stoken != None:
            subprocess.call("aws configure set aws_session_token %s"%self.stoken, shell=True)
        subprocess.call("aws configure set region %s"%self.region, shell=True)

    def manual_check(self, cmd):
        # cmd is from user input : ex) "aws s3 ls s3://bucketname"
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        data = []
        while res.poll() is None:
            l = res.stdout.readline() # This blocks until it receives a newline.
            cprint (l, 'blue')
            data.append(str(l, "utf-8").strip())
        print(data)
        return data

    def message_send(self, data):
        if self.logger != "":
            self.logger.info(json.dumps(data))

    def s3_check(self, bucket, command):
        s3 = boto3.resource(
            's3',
            aws_access_key_id=self.accesskey,
            aws_secret_access_key=self.secretkey,
            aws_session_token=self.stoken,
            region_name=self.region
        )
        if command == 'ls':
            self.message_send({"service":"s3", "type":"start", "msg":"[*] S3 Service Check Start : "+bucket})
            try:
                res = s3.Bucket(bucket)
                if res:
                    result = res.meta.client.list_objects(Bucket=bucket, Delimiter='/')
                    for o in result.get('CommonPrefixes'):
                        cprint(o.get('Prefix'), 'blue')
                        self.message_send({"service":"s3", "type":"list", "msg":o.get('Prefix')})
                    cprint ("[!] This Cloud-Backend is vulnerable", 'blue')
                    self.message_send({"service":"s3", "type":"vuln", "msg":"[!] This Cloud-Backend service is vulnerable"})
                                        
            except ClientError as e:
                print (e)
                cprint ("[!] This Cloud-Backend is not vulnerable", 'blue')
                self.message_send({"service":"s3", "type":"novuln", "msg":"[!] This Cloud-Backend service is not vulnerable"})

    def kinesis_check(self, command):
        client = boto3.client(
            "kinesis",
            aws_access_key_id=self.accesskey,
            aws_secret_access_key=self.secretkey,
            aws_session_token=self.stoken,
            region_name=self.region
        )
        if command == 'list_streams':
            self.message_send({"service":"kinesis", "type":"start", "msg":"[*] Kinesis Service Check Start"})
            try:
                if client.list_streams() :
                    cprint ("[!] This Cloud-Backend is vulnerable", 'blue')
                    self.message_send({"service":"kinesis", "type":"vuln", "msg":"[!] This Cloud-Backend service is vulnerable"})
                    cprint (client.list_streams(),'blue')
                    self.message_send({"service":"kinesis", "type":"list_streams", "msg":client.list_streams()})

            except ClientError as e:
                print (e)
                cprint ("[!] This Cloud-Backend is not vulnerable", 'blue')
                self.message_send({"service":"kinesis", "type":"novuln", "msg":"[!] This Cloud-Backend service is not vulnerable"})
    
    def firehose_check(self, command):
        client = boto3.client(
            "firehose",
            aws_access_key_id=self.accesskey,
            aws_secret_access_key=self.secretkey,
            aws_session_token=self.stoken,
            region_name=self.region
        )
        if command == 'list_delivery_streams':
            self.message_send({"service":"firehose", "type":"start", "msg":"[*] Firehose Service Check Start"})
            try:
                res = client.list_delivery_streams()
                if res :
                    cprint ("[!] This Cloud-Backend is vulnerable", 'blue')
                    self.message_send({"service":"firehose", "type":"vuln", "msg":"[!] This Cloud-Backend service is vulnerable"})
                    cprint (res,'blue')
                    self.message_send({"service":"firehose", "type":"list_delivery_streams", "msg":res})

            except ClientError as e:
                print (e)
                cprint ("[!] This Cloud-Backend is not vulnerable", 'blue')
                self.message_send({"service":"firehose", "type":"novuln", "msg":"[!] This Cloud-Backend service is not vulnerable"})
