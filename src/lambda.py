import json
import boto3
import os

sns = boto3.client("sns")
origin = os.environ["ALLOWED_ORIGIN"]
topic_arn = os.environ["CONTACT_TOPIC_ARN"]


def handler(event, context):
    try:
        allowed_origin = origin
        request_origin = event.get("headers", {}).get("origin", "")

        if request_origin != allowed_origin:
            return {
                "statusCode": 403,
                "headers": {
                    "Access-Control-Allow-Origin": request_origin,
                    "Access-Control-Allow-Methods": "POST,OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                },
                "body": json.dumps({"message": "Forbidden"})
            }

        method = event.get("requestContext", {}).get("http", {}).get("method")
        if method == "OPTIONS":
            return {
                "statusCode": 204,
                "headers": {
                    "Access-Control-Allow-Origin": request_origin,
                    "Access-Control-Allow-Methods": "POST,OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Content-Type": "application/json",
                    "Content-Length": "0"
                }
            }

        body = json.loads(event["body"])
        name = body.get("name")
        email = body.get("email")
        message = body.get("message")

        if not name or not email or not message:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": request_origin,
                    "Access-Control-Allow-Methods": "POST,OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                },
                "body": json.dumps({"message": "Missing form fields"})
            }

        text = f"New contact form submission:\nName: {name}\nEmail: {email}\nMessage: {message}"

        sns.publish(
            TopicArn=topic_arn,
            Message=text,
            Subject="New Contact Form Submission"
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": request_origin,
                "Access-Control-Allow-Methods": "POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"message": "Message sent"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": request_origin,
                "Access-Control-Allow-Methods": "POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"message": str(e)})
        }
