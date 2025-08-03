.PHONY: deploy sync clean up down rebuild login logs generate open

DC = docker-compose
CONTAINER = personal-website-generator

deploy:
	bash deploy.sh

sync:
	aws s3 sync ./$(WEBSITE_DIR) s3://$(DOMAIN_NAME) --delete

clean:
	rm -rf .aws-sam build

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