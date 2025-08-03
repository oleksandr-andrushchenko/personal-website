# Personal website

## Deploy example
```
aws cloudformation deploy \
  --template-file website.yaml \
  --stack-name static-website-stack \
  --parameter-overrides \
    DomainName=www.example.com \
    HostedZoneId=Z123456ABCDEFG \
    CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/abc-123... \
    Environment=production \
    Project=MarketingPortal \
    Owner=Oleksandr
  --capabilities CAPABILITY_NAMED_IAM

aws s3 sync ./dist/ s3://www.example.com --delete
```

## Workflow example
```
make up        # starts webserver.py
make open      # opens http://localhost:8000
make generate
```

## TODO

- add images for skills
- add markings (type=person and other details)
- disable indexing of websites and images (3rd parties)
- update Linkedin: move responsibilities to projects, sync with personal website