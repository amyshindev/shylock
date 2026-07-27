import boto3


def list_buckets():
    s3 = boto3.client("s3")
    response = s3.list_buckets()
    for bucket in response["Buckets"]:
        print(bucket["Name"])


if __name__ == "__main__":
    list_buckets()
