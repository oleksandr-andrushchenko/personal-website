# Personal website

## Workflow example

You should have AWS account and "aws" client installed and configured.
So in the end you should have these files: ~/.aws/credentials and ~/.aws/config

```
make up                 # raise up docker container(-s)
make logs               # display docker container logs
make login              # bash into docker container
make open               # open http://localhost:8000
cp .env.example .env    # create default .env
vim .env                # update .env (or nano .env)
vim data.json           # update data.json (or nano data.json)
make generate           # generates website folder ready to test locally and then upload to S3, default= ./output
make deploy-cert        # deploy cert for HTTPs (AWS)
make get-cert-arn       # display cert and update .env
make deploy-infra       # deploy infra (AWS)
make get-infra-details  # display deployed infra, for debug purposes, usually if smth went wrong
make destroy-infra      # (if deploy has been failed use this one) desroy failed infra (AWS), then after usually - update cf.yml and redeploy infra
make get-lambda-url     # display contact form lambda url and update .env
make deploy-site        # deploy website (upload website folder to S3)
make invalidate         # clear cache (AWS, cloud front distribution)
make down               # drop docker container(-s)

```

## TODO

- add images for skills
- disable indexing of websites and images (3rd parties)
- add pricing
- add credentials to licenses and education

## Links

- favicon generation: https://realfavicongenerator.net/
- circle image: https://crop-circle.imageonline.co/