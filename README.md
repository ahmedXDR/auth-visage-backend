# Auth Viage Backend

## Environment

### Python

> [uv](https://github.com/astral-sh/uv) is an extremely fast Python package and project manager, written in Rust.

```bash
cd backend
uv sync --all-groups --dev
```

### [Supabase](https://supabase.com/docs/guides/local-development/cli/getting-started?queryGroups=platform&platform=linux&queryGroups=access-method&access-method=postgres)

install supabase-cli

```bash
# brew in linux https://brew.sh/
brew install supabase/tap/supabase
```

launch supabase docker containers

```bash
# under repo root
supabase start
```

> [!NOTE]
>```bash
># Update `.env`
>bash scripts/update-env.sh
>```
> modify the `.env` from the output of `supabase start` or run `supabase status` manually.


## Docker

> [!note]
> `auth_viage_backend` is your image tag name, remember replace it with yours

build

```bash
cd backend
docker build -t auth_viage_backend .
```

run

```bash
bash scripts/update-env.sh
supabase start
cd backend
docker run -p9000:9000 --env-file ../.env auth_viage_backend:latest
```
