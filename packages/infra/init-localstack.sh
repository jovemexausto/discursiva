#!/bin/bash
set -e

AWS="aws --endpoint-url=http://localhost:4566 --region us-east-1"

echo ">>> Criando bucket S3..."
$AWS s3 mb s3://discursiva-submissions || true

echo ">>> Criando DLQ..."
$AWS sqs create-queue \
  --queue-name corrections-dlq \
  --attributes MessageRetentionPeriod=86400

DLQ_ARN=$($AWS sqs get-queue-attributes \
  --queue-url http://localhost:4566/000000000000/corrections-dlq \
  --attribute-names QueueArn \
  --query 'Attributes.QueueArn' --output text)

echo ">>> Criando fila principal com redrive para DLQ..."
cat > /tmp/sqs-attrs.json <<EOF
{
  "VisibilityTimeout": "60",
  "MessageRetentionPeriod": "3600",
  "RedrivePolicy": "{\"deadLetterTargetArn\":\"$DLQ_ARN\",\"maxReceiveCount\":\"3\"}"
}
EOF
$AWS sqs create-queue \
  --queue-name corrections-queue \
  --attributes file:///tmp/sqs-attrs.json

echo ">>> LocalStack init concluído."
