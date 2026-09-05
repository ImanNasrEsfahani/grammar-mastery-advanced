# grammarb2 deployment isolation patch

Prepared against repository:

- `ImanNasrEsfahani/grammar-mastery-advanced`
- source commit: `176c6dd95f1d8c3feb8495c0697b925947e7e8ec`
- public host: `grammarb2.imannasr.com`

## Replace existing files

1. `docker-compose.yml`
2. `docker.env.example`
3. `docker/backend/gmp_runtime/settings.py`

## Add new files

1. `ops/deploy/preflight.sh`
2. `ops/deploy/DEPLOY_GRAMMARB2.md`
3. `ops/deploy/nginx/grammarb2.imannasr.com.bootstrap.conf`
4. `ops/deploy/nginx/grammarb2.imannasr.com.conf`
5. `ops/deploy/PATCH_MANIFEST.md`

## What the patch isolates

- Compose project identity
- Docker network
- PostgreSQL volume
- PostgreSQL database/user defaults
- host frontend/backend ports
- Django host/CSRF origin
- JWT issuer/audience/signing secret slot
- password-reset public origin
- secure host-only cookie policy
- Nginx virtual host and TLS certificate path
- deployment commands and preflight checks

No GitHub write operation was performed while preparing this package.
