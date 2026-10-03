import json
import boto3

# Create Amazon Comprehend client
comprehend = boto3.client("comprehend")


def lambda_handler(event, context):

    try:
        # Get request body
        body = event.get("body", event)

        if isinstance(body, str):
            body = json.loads(body)

        # Get customer feedback
        feedback = body.get("feedback", "").strip()

        # Validate input
        if not feedback:
            return response(
                400,
                {
                    "error": "Please enter customer feedback."
                }
            )

        # Amazon Comprehend has a 5 KB limit for DetectSentiment
        if len(feedback.encode("utf-8")) > 5000:
            return response(
                400,
                {
                    "error": "Feedback must be less than 5 KB."
                }
            )

        # Analyze sentiment
        result = comprehend.detect_sentiment(
            Text=feedback,
            LanguageCode="en"
        )

        # Get sentiment scores
        scores = result["SentimentScore"]

        output = {
            "feedback": feedback,
            "sentiment": result["Sentiment"],
            "scores": {
                "positive": round(scores["Positive"] * 100, 2),
                "negative": round(scores["Negative"] * 100, 2),
                "neutral": round(scores["Neutral"] * 100, 2),
                "mixed": round(scores["Mixed"] * 100, 2)
            }
        }

        return response(200, output)

    except Exception as e:

        print("Error:", str(e))

        return response(
            500,
            {
                "error": str(e)
            }
        )


def response(status_code, body):

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }