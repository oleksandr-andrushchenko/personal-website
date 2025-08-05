# Load .env into Makefile environment
ifneq (,$(wildcard .env))
  include .env
  export
endif

.PHONY: deploy-cert get-cert-arn deploy-infra get-infra-details destroy-infra deploy-site invalidate up down rebuild login logs generate open

DC = docker-compose
CONTAINER = personal-website-generator

deploy-cert:
	@echo "🔐 Deploying ACM certificate for $(DOMAIN_NAME) in us-east-1..."
	aws cloudformation deploy \
		--profile "$(AWS_PROFILE_NAME)" \
		--region "us-east-1" \
		--template-file cf-cert.yml \
		--stack-name "$(STACK_NAME)-cert" \
		--capabilities CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			DomainName="$(DOMAIN_NAME)" \
			HostedZoneId="$(HOSTED_ZONE_ID)" \
			TagProject="$(TAG_PROJECT)" \
			TagOwner="$(TAG_OWNER)" \
			TagEnvironment="$(TAG_ENVIRONMENT)" \
			TagRegion="us-east-1" \
		--tags \
			Project="$(TAG_PROJECT)" \
			Owner="$(TAG_OWNER)" \
			Environment="$(TAG_ENVIRONMENT)" \
			Region="us-east-1"
	@echo "✅ Certificate deployment triggered. Waiting for DNS validation..."

get-cert-arn:
	@echo "🔍 Fetching ACM Certificate ARN for $(DOMAIN_NAME) in us-east-1..."
	@ARN=$$(aws cloudformation describe-stacks \
		--stack-name "$(STACK_NAME)-cert" \
		--region "us-east-1" \
		--profile "$(AWS_PROFILE_NAME)" \
		--query "Stacks[0].Outputs[?OutputKey=='CertificateArn'].OutputValue" \
		--output text); \
	if [ -z "$$ARN" ]; then \
		echo "❌ Certificate ARN not found. Make sure the certificate stack was deployed successfully."; \
	else \
		echo "✅ Certificate ARN for $(DOMAIN_NAME): $$ARN"; \
		if grep -q "^CLOUDFRONT_CERTIFICATE_ARN=" .env; then \
			sed -i.bak "s|^CLOUDFRONT_CERTIFICATE_ARN=.*|CLOUDFRONT_CERTIFICATE_ARN=$$ARN|" .env; \
			rm -f .env.bak; \
		else \
			echo "CLOUDFRONT_CERTIFICATE_ARN=$$ARN" >> .env; \
		fi; \
		echo "📝 Updated .env with CLOUDFRONT_CERTIFICATE_ARN"; \
	fi

deploy-infra:
	@echo "🚀 Deploying CloudFormation stack for $(DOMAIN_NAME)..."
	@if [ -z "$(CLOUDFRONT_CERTIFICATE_ARN)" ]; then \
		echo "❌ CLOUDFRONT_CERTIFICATE_ARN is not defined. Run \`make get-cert-arn\` or export it in .env"; \
		exit 1; \
	fi
	aws cloudformation deploy \
		--profile "$(AWS_PROFILE_NAME)" \
		--region "$(AWS_REGION)" \
		--template-file cf.yml \
		--stack-name "$(STACK_NAME)" \
		--capabilities CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			DomainName="$(DOMAIN_NAME)" \
			HostedZoneId="$(HOSTED_ZONE_ID)" \
			CertificateArn="$(CLOUDFRONT_CERTIFICATE_ARN)" \
			NotificationEmail="$(NOTIFICATION_EMAIL)" \
			NotificationPhone="$(NOTIFICATION_PHONE)" \
			TagProject="$(TAG_PROJECT)" \
			TagOwner="$(TAG_OWNER)" \
			TagEnvironment="$(TAG_ENVIRONMENT)" \
			TagRegion="$(AWS_REGION)" \
		--tags \
			Project="$(TAG_PROJECT)" \
			Owner="$(TAG_OWNER)" \
			Environment="$(TAG_ENVIRONMENT)"

	@echo "📤 Stack outputs:"
	@aws cloudformation describe-stacks \
		--stack-name "$(STACK_NAME)" \
		--profile "$(AWS_PROFILE_NAME)" \
		--region "$(AWS_REGION)" \
		--query "Stacks[0].Outputs" \
		--output table

get-infra-details:
	aws cloudformation describe-stack-events \
		--stack-name "$(STACK_NAME)" \
		--profile "$(AWS_PROFILE_NAME)" \
		--region "$(AWS_REGION)"

destroy-infra:
	aws cloudformation delete-stack \
		--stack-name "$(STACK_NAME)" \
		--region "$(AWS_REGION)" \
		--profile "$(AWS_PROFILE_NAME)"
	@echo "🧼 Waiting for stack to be fully deleted..."
	aws cloudformation wait stack-delete-complete \
		--stack-name "$(STACK_NAME)" \
		--region "$(AWS_REGION)" \
		--profile "$(AWS_PROFILE_NAME)"
	@echo "✅ Stack $(STACK_NAME) deleted."

get-lambda-url:
	@echo "📡 Fetching Lambda Function URL..."
	@LAMBDA_URL=$$(aws cloudformation describe-stacks \
		--stack-name "$(STACK_NAME)" \
		--query "Stacks[0].Outputs[?OutputKey=='ContactFormEndpoint'].OutputValue" \
		--output text \
		--region "$(AWS_REGION)" \
		--profile "$(AWS_PROFILE)"); \
	if grep -q "^LAMBDA_URL=" .env; then \
		sed -i.bak "s|^LAMBDA_URL=.*|LAMBDA_URL=$$LAMBDA_URL|" .env; \
		rm -f .env.bak; \
	else \
		echo "\nLAMBDA_URL=$$LAMBDA_URL" >> .env; \
	fi; \
	echo "✅ Saved LAMBDA_URL=$$LAMBDA_URL to .env"

deploy-site:
	aws s3 sync ./$(WEBSITE_DIR) s3://$(DOMAIN_NAME) \
		--delete \
		--profile "$(AWS_PROFILE_NAME)" \
		--region "$(AWS_REGION)"

invalidate:
	@echo "🔎 Finding CloudFront distribution for $(DOMAIN_NAME)..."
	@DISTRIBUTION_ID=$$(aws cloudfront list-distributions \
		--profile "$(AWS_PROFILE_NAME)" \
		--region "$(AWS_REGION)" \
		--query "DistributionList.Items[?Aliases.Items[?contains(@, '$(DOMAIN_NAME)')]].Id" \
		--output text); \
	if [ -n "$$DISTRIBUTION_ID" ]; then \
		echo "⚡ Invalidating CloudFront cache for distribution $$DISTRIBUTION_ID..."; \
		aws cloudfront create-invalidation \
			--profile "$(AWS_PROFILE_NAME)" \
			--region "$(AWS_REGION)" \
			--distribution-id "$$DISTRIBUTION_ID" \
			--paths "/*"; \
	else \
		echo "⚠️  CloudFront distribution not found for $(DOMAIN_NAME) — skipping invalidation."; \
	fi

up:
	$(DC) up -d --remove-orphans

down:
	$(DC) down

rebuild:
	$(DC) down
	$(DC) build
	$(DC) up -d --remove-orphans

login:
	docker exec -it $(CONTAINER) bash

logs:
	docker logs -f $(CONTAINER)

generate:
	docker exec -it $(CONTAINER) python generate.py

open:
	@echo "🌐 Visit http://localhost:3000 in your browser manually."