# HipoMaster: despliegue y operaciones (SRE) v0.1

Estado: propuesta para revisión. Fecha: 2026-11-01.
Parte de: [ARQUITECTURA.md](ARQUITECTURA.md) (sección 6) y [SCRAPING.md](SCRAPING.md) (rama `claude/project-thread-64yb8i`).
Ficheros base: [`deploy/`](../deploy/).

## 1. Resumen

- **Una VM central** (Ubuntu 24.04, 16 GB) con Docker Compose: LangGraph server, Agent Chat UI, LiteLLM, Postgres + pgvector, Redis, Langfuse y, opcionalmente, Ollama 7B.
- **Cuatro fitlet2** con Ubuntu Server 24.04 y Ollama nativo (systemd). El nº 4 ejecuta además el scraping semanal.
- **Red privada con Tailscale** (malla WireGuard). Ningún puerto abierto a Internet. Se accede a la UI desde el móvil o portátil con la app de Tailscale.
- **Provisión con Ansible** (todos los nodos) y **CI/CD con GitHub Actions** (validación, imágenes en GHCR, despliegue con aprobación manual).
- **Coste API acotado en LiteLLM**: 4,50 USD/mes globales, topes por proveedor y por clave, alerta al 80 %.
- **Backups** diarios de Postgres cifrados con restic, copia local y externa. Prueba de restauración mensual.

## 2. Topología

```
                     Internet (solo salida: APIs, bancos, BdE)
                                  │
 ┌──────────────── tailnet (WireGuard, ACLs) ─────────────────────────────┐
 │                                                                        │
 │  core-01  VM Ubuntu 16 GB  (tag:core)                                  │
 │  ┌──────────────────────────────────────────────────────────────────┐  │
 │  │ agent-chat-ui :3000 ─▶ langgraph-api :8123 ─▶ litellm :4000      │  │
 │  │                         │        │              │                │  │
 │  │                     postgres  redis        langfuse :3001        │  │
 │  │                     +pgvector              (+clickhouse, minio)  │  │
 │  │                     ollama-mid :11434 (perfil "mid", opcional)   │  │
 │  └──────────────────────────────────────────────────────────────────┘  │
 │        │ LiteLLM llama a :11434 de cada fitlet                         │
 │  edge-01  edge-02  edge-03         edge-04  (tag:edge)                 │
 │  chat     chat     embeddings      reserva + scraper (tag:scraper)     │
 │                                                                        │
 │  Portátil / móvil de doc (tag:admin) ─▶ UI :3000, Langfuse, SSH        │
 └────────────────────────────────────────────────────────────────────────┘
```

| Host | Rol | Servicios | Exposición |
|---|---|---|---|
| core-01 | central | compose completo | solo tailnet |
| edge-01, edge-02 | chat y clasificación | Ollama `qwen2.5:3b` | :11434 solo desde tag:core |
| edge-03 | embeddings, extracción simple | Ollama `nomic-embed-text`, `qwen2.5:3b` | :11434 solo desde tag:core |
| edge-04 | reserva y scraping | Ollama `qwen2.5:3b`, contenedor scraper (timer) | :11434 desde tag:core; sale a Postgres de core-01 |

## 3. Instalación y provisión

### 3.1 Fitlet2 (una vez, a mano)
1. Comprobar disco: los modelos necesitan espacio. Mínimo SSD de 64 GB (eMMC de 32 GB se queda corto con 3B + 7B + logs).
2. BIOS: arranque tras corte de luz ("AC power loss: power on"), arranque por USB para instalar.
3. Instalar Ubuntu Server 24.04 LTS mínimo, usuario `ops`, OpenSSH con clave. Hostname `edge-0N`.
4. Reserva DHCP estática en el router (útil aunque se use Tailscale).
5. Ejecutar `tailscale up --ssh --advertise-tags=tag:edge` con una auth key de un solo uso.

A partir de aquí todo con Ansible.

### 3.2 VM central (una vez)
1. Ubuntu Server 24.04, 4+ vCPU, 16 GB, disco de 100 GB mínimo (modelos, Postgres, ClickHouse). Si es posible, disco cifrado (LUKS) porque guarda documentos del cliente.
2. Usuario `ops`, SSH con clave, Tailscale con `tag:core`.
3. Ansible instala Docker Engine + plugin compose, y despliega `deploy/vm/`.

### 3.3 Ansible (`deploy/ansible/`)
- `inventory.ini`: hosts por nombre de Tailscale (MagicDNS).
- Rol `base` (todos): `unattended-upgrades`, `ufw` (deny entrante salvo `tailscale0`), `fail2ban` desactivado en SSH público porque no hay, zram para swap, `chrony`, `node_exporter`, journald con límite de 500 MB.
- Rol `ollama` (edge): instala Ollama, override systemd (`deploy/edge/ollama.override.conf`), descarga los modelos del host (`ollama_models` en el inventario), `OLLAMA_HOST` solo en la IP de Tailscale.
- Rol `docker` (core y edge-04).
- Rol `scraper` (edge-04): imagen del scraper y `systemd` timer.
- Idempotente: se reejecuta tras cada cambio de configuración (`ansible-playbook site.yml --limit edge`).

### 3.4 Ollama en los fitlet2
```
OLLAMA_HOST=<ip-tailscale>:11434
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=2
OLLAMA_KEEP_ALIVE=30m
OLLAMA_CONTEXT_LENGTH=4096
```
Ollama no tiene autenticación. Por eso escucha solo en la interfaz de Tailscale y las ACL permiten el puerto 11434 solo desde `tag:core`.

## 4. Servicios de la VM (Docker Compose)

Fichero: [`deploy/vm/docker-compose.yml`](../deploy/vm/docker-compose.yml). Perfiles:
- por defecto: postgres, redis, litellm, langgraph-api, agent-chat-ui, uptime-kuma.
- `obs`: Langfuse v3 (web, worker, ClickHouse, MinIO).
- `mid`: Ollama local con Qwen 7B.

### 4.1 Presupuesto de memoria (16 GB)

| Servicio | Límite | Notas |
|---|---|---|
| SO + Docker | 1,5 GB | |
| postgres (pgvector) | 1,5 GB | `shared_buffers=512MB` |
| redis | 256 MB | `noeviction`, compartido (db 0 LangGraph, db 1 Langfuse) |
| litellm | 768 MB | |
| langgraph-api | 1 GB | |
| agent-chat-ui | 384 MB | |
| uptime-kuma | 256 MB | monitorización, :3002 |
| langfuse web + worker | 1,5 GB | perfil `obs` |
| clickhouse | 2 GB | perfil `obs` |
| minio | 256 MB | perfil `obs` |
| ollama-mid (Qwen 7B Q4, 16k ctx) | 6 GB | perfil `mid` |
| **Total** | **~15,5 GB** | justo; ver 4.2 |

### 4.2 Si falta memoria
En este orden:
1. Bajar el contexto de `ollama-mid` a 8k.
2. Mover Langfuse a Langfuse Cloud (plan gratuito) enviando solo trazas anonimizadas. Libera ~3,7 GB.
3. Quitar el perfil `mid` y usar DeepSeek flash como nivel medio (coste API sube).
4. Ampliar la VM o pasar a AWS (sección 13).

### 4.3 Acceso
- Los puertos se publican solo en la IP de Tailscale de core-01 (`BIND_IP` en `.env`).
- HTTPS: `tailscale serve` delante de la UI y de Langfuse (certificado automático `*.ts.net`). Sin Caddy ni dominio propio en el MVP.
- Acceso público a clientes finales: fuera del MVP. Cuando haga falta, Cloudflare Tunnel o ALB en AWS, con autenticación (OIDC) delante de la UI.

### 4.4 LangGraph server
- Imagen propia generada con `langgraph build -t ghcr.io/miggom/hipomaster-agents:<sha>` desde el código de agentes.
- Requiere `DATABASE_URI` (Postgres) y `REDIS_URI`.
- **Pendiente de comprobar**: el servidor autoalojado de LangGraph ha pedido históricamente una clave de LangSmith o licencia. Si en el momento de implementar sigue así y no hay plan gratuito, alternativa: servir el grafo con FastAPI propio compatible con la API que usa Agent Chat UI.

### 4.5 Agent Chat UI
- Se construye desde el repositorio de LangChain con un commit fijado (`deploy/vm/agent-chat-ui/Dockerfile`).
- Variables: `NEXT_PUBLIC_API_URL` (LangGraph) y `NEXT_PUBLIC_ASSISTANT_ID=hipomaster`.

## 5. Red y acceso seguro

- **Tailscale** (plan personal gratuito, hasta 100 dispositivos). Alternativa sin terceros: Headscale en la VM, o WireGuard manual.
- ACL (política en la consola de Tailscale, versión en `deploy/tailscale/acl.hujson`):
  - `tag:admin` → todo (SSH, UI, Langfuse).
  - `tag:core` → `tag:edge:11434`.
  - `tag:scraper` → `tag:core:5432` (solo Postgres) y `tag:core:4000` (LiteLLM, para el respaldo DeepSeek).
  - Nada más. Los fitlet2 no se ven entre sí.
- SSH solo por Tailscale SSH o por clave sobre la tailnet. Contraseñas desactivadas.
- Salida a Internet: libre en el MVP. Más adelante, lista blanca en ufw para edge-04 (bancos, BdE).
- Postgres: usuarios distintos por servicio (`hipomaster`, `litellm`, `langfuse`, `scraper`), el del scraper solo con permisos sobre `offers` y `offer_history`.

## 6. Secretos

- Nunca en Git. Solo `deploy/vm/.env.example` con nombres.
- **sops + age**: `deploy/secrets/vm.enc.env` cifrado en el repo. La clave privada age vive en el portátil de doc y en core-01 (`/etc/hipomaster/age.key`, `600`). Ansible descifra y escribe `deploy/vm/.env` con permisos `600`.
- Copia de la clave age en el gestor de contraseñas de doc. Sin ella no se recuperan backups ni secretos.
- Claves de API:
  - Cada consumidor usa una **virtual key de LiteLLM** con su propio tope. Las claves reales de DeepSeek y Anthropic solo están en LiteLLM.
  - Anthropic: fijar además un límite de gasto en la consola del proveedor. DeepSeek es prepago: el saldo es el tope natural.
- Rotación: claves de proveedores cada 6 meses o ante sospecha; contraseñas internas al reconstruir.

## 7. Datos, backups y restauración

| Dato | Dónde | Backup | Retención |
|---|---|---|---|
| Postgres (estado LangGraph, ofertas, RAG, LiteLLM, Langfuse meta) | volumen `pgdata` | `pg_dumpall` diario 03:00 | 7 diarios, 4 semanales, 6 mensuales |
| Documentos del cliente (cifrados) | volumen `docs` | restic diario | según RGPD: borrar al cerrar el estudio o a los 30 días |
| ClickHouse (trazas Langfuse) | volumen | no se respalda | TTL 30 días; reproducibles |
| Modelos Ollama | discos locales | no | se vuelven a descargar |
| Configuración | Git + sops | Git | |

- Herramienta: `deploy/scripts/backup.sh` con **restic** (cifrado). Destinos: disco de edge-04 por SFTP sobre tailnet, y uno externo (Backblaze B2 o S3, < 1 USD/mes para pocos GB).
- Ping a healthchecks.io al terminar; si no llega, alerta.
- **Restauración probada** el primer domingo de cada mes en un contenedor temporal (`backup.sh verify`). RPO 24 h, RTO 2 h.

## 8. Monitorización y alertas

MVP, ligero:
- **Uptime Kuma** (contenedor de ~150 MB en core-01): comprueba UI, LangGraph `/ok`, LiteLLM `/health/liveliness`, Langfuse y Ollama de cada fitlet2. Avisos por **Telegram**.
- **healthchecks.io** (gratis): latido de tareas programadas (scraping semanal, Euríbor diario, backup diario, informe de coste diario).
- **Langfuse**: latencia, tokens y coste por agente y por nivel de modelo; % de escalados.
- **LiteLLM**: gasto por clave y proveedor.

Alertas:

| Alerta | Umbral | Canal |
|---|---|---|
| Servicio caído | 2 comprobaciones fallidas (2 min) | Telegram |
| Nodo edge caído | 5 min | Telegram |
| Gasto API | 80 % del mensual o 0,50 USD en un día | Telegram |
| Scraping no terminó | sin latido el lunes 06:00 | Telegram + email |
| Backup no terminó | sin latido a las 05:00 | Telegram |
| Disco | > 85 % | Telegram |
| RAM VM | > 90 % durante 10 min | Telegram |

Fase 2: Prometheus + node_exporter + Grafana si se necesitan series históricas de recursos.

## 9. Logging

- Docker: driver `json-file` con `max-size=10m`, `max-file=5` por contenedor.
- Fitlet2: journald, máx. 500 MB.
- Aplicación: logs JSON (structlog), con `thread_id` y `run_id` de LangGraph para cruzar con Langfuse.
- **PII**: no registrar contenido de documentos ni prompts con datos personales. Langfuse recibe entradas enmascaradas (función de masking del SDK). Retención de trazas 30 días.
- Fase 2: Loki + Promtail si hace falta buscar en logs de varios nodos.

## 10. CI/CD

Repositorio: `miggom/hipomaster`. GitHub Actions (gratis en repos públicos; en privados, 2.000 min/mes).

| Pipeline | Cuándo | Qué hace |
|---|---|---|
| `ci.yml` | cada push y PR | ruff, mypy, pytest (calculadora y esquemas), `docker compose config`, yamllint, ansible-lint |
| `build.yml` | merge a `main` | `langgraph build`, imágenes del scraper y UI → GHCR con tag del commit |
| `deploy.yml` | manual, con environment `produccion` y aprobación | conecta a la tailnet (auth key efímera con `tag:ci`), ejecuta Ansible: `docker compose pull && up -d` en core-01, scraper en edge-04 |
| `evals.yml` | semanal y en PR que toque `prompts/` | casos sintéticos de ARQUITECTURA.md §8 contra modelos edge; DeepSeek/Claude solo con etiqueta `run-paid-evals` |

- Versionado de prompts: `prompts/<agente>/vN.md`. Un cambio de prompt es un PR con evals.
- Rollback: volver al tag de imagen anterior en `.env` (`AGENTS_IMAGE_TAG`) y `up -d`. Migraciones de BD con Alembic, siempre compatibles hacia atrás una versión.
- Primero hace falta una rama `main` en el repo (hoy no existe).

## 11. Tareas programadas

Todas con `systemd` timers (no cron): registran en journald, reintentan y no solapan.

| Tarea | Host | Cuándo (Europe/Madrid) | Notas |
|---|---|---|---|
| Scraping de ofertas | edge-04 | domingo 02:00 | `deploy/edge/hipomaster-scraper.timer`; `RandomizedDelaySec=30m`; tope de duración 3 h |
| Euríbor y tipos BdE | edge-04 | diario 07:30 | ligero, solo HTTP |
| Caducar ofertas > 30 días | core-01 | diario 04:00 | SQL |
| Backup | core-01 | diario 03:00 | sección 7 |
| Informe de gasto API | core-01 | diario 08:00 | consulta LiteLLM, manda resumen a Telegram |
| Evals | GitHub Actions | lunes 06:00 | |

El scraping corre en edge-04 en un contenedor con Playwright, usa el Ollama local para extraer y escribe en Postgres de core-01. El respaldo a DeepSeek flash pasa por LiteLLM con la clave virtual `scraper` (tope 0,20 USD/mes). Mientras corre, edge-04 deja de recibir tráfico de chat: LiteLLM le asigna peso 0 (o se usa solo como reserva).

## 12. Control de coste API (~5 USD/mes)

Capas, de la más dura a la más blanda:
1. **Proveedor**: DeepSeek prepago (recargas pequeñas); Anthropic con límite de gasto mensual en consola.
2. **LiteLLM global**: `max_budget: 4.5`, `budget_duration: 30d`. Al llegar, rechaza llamadas de pago y el router se queda en local.
3. **LiteLLM por proveedor**: DeepSeek 3,00 USD/30d; Anthropic 1,50 USD/30d.
4. **LiteLLM por clave virtual** (30 días):

| Clave | Uso | Tope |
|---|---|---|
| `agents` | grafo LangGraph | 4,00 USD |
| `scraper` | respaldo extracción | 0,20 USD |
| `evals` | evals de pago | 0,30 USD |

5. **Por estudio**: el Coordinador lleva un contador de coste en el estado; más de 0,15 USD por estudio pide confirmación (human-in-the-loop).
6. **Alertas** al 80 % y resumen diario (sección 8).

Si se agota: el sistema sigue con edge y mid locales y el informe indica que no hubo validación frontier.

## 13. Escalado a AWS

Disparadores para escalar (medidos en Langfuse y Uptime Kuma):
- p95 de respuesta interactiva > 30 s de forma sostenida.
- RAM de core-01 > 90 % habitual o necesidad de modelos > 8B.
- Usuarios externos (clientes finales) o necesidad de disponibilidad > 99 %.

Fases:
1. **Backups a S3** (ya posible desde el día 1). Coste: céntimos.
2. **GPU bajo demanda**: instancia g6.xlarge o g5.xlarge (24 GB) con vLLM u Ollama, unida a la tailnet. Se enciende para lotes (extracción masiva, evals) y se apaga con un script o Lambda programada. Spot cuando se pueda. Coste orientativo ~0,5-1 USD/hora; verificar precios en eu-south-2 (Madrid) o eu-west-1. LiteLLM la añade como nivel `mid` con prioridad sobre DeepSeek.
3. **Servicios centrales a AWS**: misma composición en EC2 (t4g.large/xlarge, ARM) o ECS; Postgres a RDS con pgvector; documentos a S3 con SSE-KMS. Los fitlet2 siguen como edge vía tailnet o Site-to-Site VPN.
4. **Producción para terceros**: ALB + WAF + Cognito/OIDC delante de la UI, Secrets Manager en lugar de sops, CloudWatch para logs y alarmas.

Diseño para facilitarlo desde hoy: todo en contenedores, configuración por variables de entorno, nada con rutas fijas al host, Postgres como único estado.

Región: preferir eu-south-2 (España) o eu-west-3/eu-central-1 por RGPD. Los datos personales no salen del EEE.

## 14. Runbooks (resumen)

- **Fitlet2 caído**: LiteLLM lo saca del balanceo tras 3 fallos (`allowed_fails`, `cooldown_time`). Revisar alimentación y `journalctl -u ollama`. Reinstalar: Ubuntu + `ansible-playbook site.yml --limit edge-0N`.
- **VM caída**: sin servicio. Restaurar de backup en otra VM con Ansible + `backup.sh restore` (RTO 2 h).
- **Presupuesto agotado**: revisar en LiteLLM qué clave consumió; ajustar router; no subir el tope sin decisión de doc.
- **Scraping falla**: revisar cola de revisión manual y logs del timer; un banco bloqueado pasa a modo PDF o manual (SCRAPING.md §9).

## 15. Decisiones abiertas

1. ¿Tailscale (recomendado) o Headscale/WireGuard propio?
2. ¿Langfuse autoalojado (3,7 GB de RAM) o Langfuse Cloud con trazas anonimizadas?
3. ¿Destino externo de backups: Backblaze B2 o S3?
4. ¿Telegram como canal de alertas?
5. Disco real de los fitlet2 y de la VM.
6. Licencia del LangGraph server autoalojado (sección 4.4).
7. Crear rama `main` para habilitar PR y CI/CD.
