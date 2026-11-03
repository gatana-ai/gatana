# Gatana with Docker Compose

Gatana, Postgres, the Code Mode worker and the web fetcher on one machine. The guide is at https://docs.gatana.ai/docker-compose.

```sh
curl -LO https://raw.githubusercontent.com/gatana-ai/gatana/main/self-host/compose/docker-compose.yml \
  && curl -LO https://raw.githubusercontent.com/gatana-ai/gatana/main/self-host/compose/.env.example \
  && cp .env.example .env \
  && docker compose up -d --wait
```

Then open http://localhost:8080.

- Settings: `.env`. Its comments say what to change before other people can reach the install.
- Upgrade: download `docker-compose.yml` again, then `docker compose up -d --wait`.
- Backup: `docker compose exec postgres pg_dump -U gatana gatana | gzip > gatana.sql.gz`, and a copy of `.env`.
- Logs: `docker compose logs app`.
