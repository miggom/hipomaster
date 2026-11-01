# deploy/

Base de despliegue. Detalle en [docs/DESPLIEGUE.md](../docs/DESPLIEGUE.md).

| Carpeta | Contenido |
|---|---|
| `vm/` | Docker Compose de la VM central (core-01), config de LiteLLM, init de Postgres, Dockerfile de Agent Chat UI |
| `edge/` | Override de Ollama y timers del scraper para los fitlet2 |
| `ansible/` | Inventario y playbook de provisión |
| `tailscale/` | ACL de la tailnet |
| `scripts/` | Backup y verificación |
| `secrets/` | Secretos cifrados con sops + age (nunca en claro) |

Arranque en core-01:
```bash
cd deploy/vm
cp .env.example .env   # o generado por Ansible desde secrets/ con sops
docker compose up -d                       # núcleo
docker compose --profile obs up -d         # + Langfuse
docker compose --profile mid up -d         # + Ollama 7B local
```
