# Safe same-server deployment: grammarb2.imannasr.com

This deployment profile is intentionally isolated from the existing Grammar Mastery stack.

## Fixed isolation choices

- Existing Compose project: `grammar-mastery`
- Existing host ports: frontend `127.0.0.1:3005`, backend `127.0.0.1:8005`
- Advanced Compose project: `grammar-mastery-advanced`
- Advanced host ports: frontend `127.0.0.1:3006`, backend `127.0.0.1:8006`
- Advanced PostgreSQL volume: `grammar-mastery-advanced-postgres-data`
- Advanced Docker network: `grammar-mastery-advanced-app`
- Advanced public hostname: `grammarb2.imannasr.com`
- PostgreSQL is not published to the host.

The container-internal ports remain `frontend:3000`, `backend:8000`, and `postgres:5432`. They do not conflict because the Advanced stack has its own Docker network.

## 1. Create the server-only environment file

From the Advanced repository root:

```bash
cp docker.env.example .env.docker
chmod 600 .env.docker
```

Replace every required `CHANGE_ME` value. Generate **three independent secrets** for:

- `DJANGO_SECRET_KEY`
- `POSTGRES_PASSWORD`
- `STAGE21_JWT_SIGNING_KEY`

Do not copy any of those values from the existing site. `.env.docker` is ignored by Git and must never be committed.

## 2. Run the non-destructive preflight

```bash
bash ops/deploy/preflight.sh
```

The script aborts if ports `3006` or `8006` are occupied, if the project name is wrong, or if Compose cannot render the configuration. It does not modify the old stack or the new stack.

If either new port is occupied by some unrelated service, change `FRONTEND_PORT` / `BACKEND_PORT` in `.env.docker` **and update the two `proxy_pass` ports in both Nginx files before continuing**.

## 3. Build and start only the Advanced stack

Always specify the Advanced project explicitly:

```bash
docker compose --env-file .env.docker -p grammar-mastery-advanced build
docker compose --env-file .env.docker -p grammar-mastery-advanced up -d
```

Verify:

```bash
docker compose --env-file .env.docker -p grammar-mastery-advanced ps
curl -fsS http://127.0.0.1:8006/health/ready
curl -I http://127.0.0.1:3006/fa/login
```

Do **not** run `docker compose down`, `docker compose down -v`, `docker system prune -a`, or `docker volume prune` from an ambiguous directory. The explicit `-p grammar-mastery-advanced` is a safety boundary.

## 4. Install the temporary Nginx vhost

Create the ACME webroot:

```bash
sudo mkdir -p /var/www/letsencrypt/.well-known/acme-challenge
```

Install only the new host configuration:

```bash
sudo cp ops/deploy/nginx/grammarb2.imannasr.com.bootstrap.conf \
  /etc/nginx/sites-available/grammarb2.imannasr.com
sudo ln -sfn /etc/nginx/sites-available/grammarb2.imannasr.com \
  /etc/nginx/sites-enabled/grammarb2.imannasr.com
sudo nginx -t
sudo systemctl reload nginx
```

The existing site's Nginx file is not edited.

## 5. Obtain the certificate without modifying the old vhost

```bash
sudo certbot certonly --webroot \
  -w /var/www/letsencrypt \
  -d grammarb2.imannasr.com
```

Do not switch to the final TLS file until the certificate command succeeds.

## 6. Switch only grammarb2.imannasr.com to HTTPS

```bash
sudo cp ops/deploy/nginx/grammarb2.imannasr.com.conf \
  /etc/nginx/sites-available/grammarb2.imannasr.com
sudo nginx -t
sudo systemctl reload nginx
```

Then test:

```bash
curl -fsS https://grammarb2.imannasr.com/health/ready
curl -I https://grammarb2.imannasr.com/fa/login
```

The final vhost forwards only the two read-only health endpoints to port `8006`; all application traffic goes to Next.js on port `3006`. Both host ports are loopback-only.

## 7. Password recovery and cookie boundary

Production environment values are prepared for the new host:

```text
DJANGO_ALLOWED_HOSTS=grammarb2.imannasr.com,...
DJANGO_CSRF_TRUSTED_ORIGINS=https://grammarb2.imannasr.com
GMP_SESSION_COOKIE_SECURE=true
PASSWORD_RESET_PUBLIC_ORIGIN=https://grammarb2.imannasr.com
STAGE21_JWT_ISSUER=grammar-mastery-advanced
STAGE21_JWT_AUDIENCE=grammar-mastery-advanced-api
```

The Django settings replacement also explicitly keeps Django cookies host-only (`SESSION_COOKIE_DOMAIN = None`, `CSRF_COOKIE_DOMAIN = None`). The Next.js access-token cookie already has no `Domain` attribute, so it remains host-only as well.

## 8. Database migration warning

The current repository's Stage 26 operations contract still marks production release as blocked until the Advanced canonical content/release gate is regenerated. This patch deliberately does **not** bypass that control and does **not** add automatic migrations to container startup.

Do not run production schema/content migration merely because the containers are healthy. Follow the repository's Stage 26 release procedure when that production gate is ready.

## 9. Rollback of the new web exposure only

If the new host has a problem, disable only its Nginx symlink and reload Nginx:

```bash
sudo rm -f /etc/nginx/sites-enabled/grammarb2.imannasr.com
sudo nginx -t
sudo systemctl reload nginx
```

To stop only the Advanced containers:

```bash
docker compose --env-file .env.docker -p grammar-mastery-advanced stop
```

Neither command targets the existing `grammar-mastery` project.
