#!/bin/bash

set -e

source .env

STACK_NAME=static-website-contact
BUCKET_NAME=$DOMAIN_NAME

echo "🚀 Deploying CloudFormation stack for $DOMAIN_NAME..."

aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name "$STACK_NAME" \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    DomainName="$DOMAIN_NAME" \
    HostedZoneId="$HOSTED_ZONE_ID" \
    NotificationEmail="$NOTIFICATION_EMAIL" \
    NotificationPhone="$NOTIFICATION_PHONE" \
    TagProject="$TAG_PROJECT" \
    TagOwner="$TAG_OWNER" \
    TagEnvironment="$TAG_ENVIRONMENT"
  --tags \
    Project=$TAG_PROJECT \
    Owner=$TAG_OWNER \
    Environment=$TAG_ENVIRONMENT

echo "✅ Stack deployed. Syncing website files to S3..."

aws s3 sync ./$WEBSITE_DIR s3://$BUCKET_NAME --delete

echo "🔄 Waiting for CloudFront distribution to propagate..."

DISTRIBUTION_ID=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[?Aliases.Items[?contains(@, '$DOMAIN_NAME')]].Id" \
  --output text)

if [ -n "$DISTRIBUTION_ID" ]; then
  echo "⚡ Invalidating CloudFront cache for distribution $DISTRIBUTION_ID..."
  aws cloudfront create-invalidation \
    --distribution-id "$DISTRIBUTION_ID" \
    --paths "/*"
else
  echo "⚠️  CloudFront distribution not found for $DOMAIN_NAME — skipping invalidation."
fi

echo "✅ Website deployed and cache invalidated."