# BookMemory

A search engine for bookmarks. 🧠✨

▶ https://bookmemory.io

## Overview

BookMemory is a bookmark management and search engine tool.
It’s built as a monorepo with a web client, an API, and shared packages.

The default development experience is mock-first, with an opt-in full local stack.

## Prerequisites

- Node.js 18+
- pnpm
- Docker Desktop (only required for dev:full)

## Local Development

Install dependencies:

```bash
pnpm install
```

### Default (mock mode)

Runs the web app using MSW mocks. No API or database required.

```bash
pnpm dev
```

Web: http://localhost:5174

### Full local stack (API + Postgres)

```bash
docker ps # verify docker desktop is running
pnpm dev:full
```

Services:

- Web: http://localhost:5174
- API: http://localhost:8000

### Run services individually

```bash
pnpm dev       # web app (expects local API to already be running)
pnpm dev:mock  # web app with mock service workers (no API needed)
pnpm dev:api   # local API server
pnpm dev:full  # web app + local API + watchers
```

## Database

```bash
docker ps # verify docker desktop is running
pnpm db:up
pnpm db:down
pnpm db:reset # local only
```

## Environment Variables

API:

```bash
cp apps/api/.env.example apps/api/.env
```

Web:

```bash
cp apps/web/.env.example apps/web/.env.local
```

## Database Migrations (SQLAlchemy + Alembic)

```bash
pnpm db:migrate "name your migration here"
pnpm db:upgrade
pnpm db:downgrade
```

## API Contracts

- Swagger UI (local): http://localhost:8000/docs
- Swagger UI (prod): https://api.bookmemory.io/docs

## Production

```bash
pnpm install
pnpm build
pnpm preview
```

If you find this useful or learned something new, consider starring the repo ⭐
