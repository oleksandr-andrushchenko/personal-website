DC = docker-compose
CONTAINER = personal-website-generator

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
