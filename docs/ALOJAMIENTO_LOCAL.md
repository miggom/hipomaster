# HipoMaster: alojamiento local (v0.1)

Estado: propuesta. Fecha: 2026-11-10.
Amplía [DESPLIEGUE.md](DESPLIEGUE.md). No cambia la topología: 4 fitlet2 + VM Ubuntu 16 GB en casa.

## 1. Dos modos

| | `hibrido` (actual) | `local` (nuevo) |
|---|---|---|
| Modelos | edge + VM + DeepSeek/Claude con tope 4,50 USD | solo edge + VM |
| Config LiteLLM | `config.yaml` | `config.local.yaml` |
| Datos del cliente fuera de casa | anonimizados a APIs | nunca |
| Calidad del análisis final | frontier | Qwen 7B (más lento y menos fino) |
| Coste | ≤ 5 USD/mes + luz | luz |

Cambio de modo: en `deploy/vm/.env` poner `HIPO_MODO=local` y `LITELLM_CONFIG=config.local.yaml`, y levantar con el perfil `mid`:

```
docker compose --profile mid --profile obs up -d
```

El grafo no cambia: en `config.local.yaml` los nombres `deepseek-*` y `claude-*` son alias de `mid-local`. Con `HIPO_MODO=local` el Redactor añade al informe: "Análisis hecho solo con modelos locales; sin validación por un modelo avanzado".

Recomendación: empezar en `local` mientras se prueba con la hipoteca propia (cero coste, cero salida de datos) y pasar a `hibrido` solo para comparar calidad en evals.

## 2. Qué corre dónde (modo local)

| Host | Modelos | Tareas |
|---|---|---|
| edge-01, edge-02 | `qwen2.5:3b` | clasificación, Q&A corta, Redactor corto |
| edge-03 | `nomic-embed-text`, `qwen2.5:3b` | embeddings RAG, extracción simple |
| edge-04 | `qwen2.5:3b`, `qwen2.5:7b` (reserva) | scraping, BdE diario, reserva del nivel mid |
| core-01 (VM) | `qwen2.5:7b` 16k (perfil `mid`) | extracción de documentos, normalización de ofertas, Analista, evaluación final |

Presupuesto de RAM de la VM: el de DESPLIEGUE §4.1 (~15,5 GB con `obs` y `mid`). Si falta, primero bajar `ollama-mid` a 8k de contexto; Langfuse a la nube ya no es opción en modo local.

## 3. Ajustes por agente en modo local

| Tarea | Híbrido | Local | Cambio |
|---|---|---|---|
| Gestor: evaluación final | frontier, 64k | mid-local, 16k | entrada resumida: solo `ScoredOffer` top 5 + escenarios ya calculados |
| Coordinador: planificación | mid | mid | igual |
| Analista | mid 16-32k | mid 16k | RAG con top-k 4 en lugar de 8 |
| Redactor informe largo | mid | mid | max salida 1,5k |

Las cifras no dependen del modelo: las da la calculadora (`src/hipomaster/calc/`). El modelo local solo extrae y explica, por eso el modo local es viable.

Latencia esperada sin GPU (a medir): Q&A en edge 5-20 s; estudio completo 10-30 min, en segundo plano. La UI avisa con interrupción al terminar.

## 4. Dependencias de nube que quedan y sustitutos

| Pieza | Hoy | Sustituto local | Recomendación |
|---|---|---|---|
| Red privada | Tailscale (servidor de control en su nube) | Headscale en core-01 o WireGuard plano | Tailscale para empezar; Headscale si se quiere 0 nube |
| HTTPS | `tailscale serve` (`*.ts.net`) | Caddy con CA interna | ligado a la anterior |
| Latido de tareas | healthchecks.io | monitores push de Uptime Kuma (ya desplegado) | Uptime Kuma |
| Alertas | Telegram | ntfy autoalojado o correo SMTP | ntfy en core-01 (requiere salida a Internet para avisar fuera de casa) |
| Backup externo | B2 o S3 | disco USB cifrado + copia rotada fuera de casa | USB + restic; S3 opcional |
| Imágenes y CI | GHCR + GitHub Actions | `docker build` en core-01 con Ansible | build local; Actions solo para tests |
| LangGraph server | imagen `langgraph-api` (pide clave LangSmith/licencia) | servidor propio FastAPI + `langgraph` (MIT) + checkpointer Postgres, compatible con Agent Chat UI; o un servidor abierto compatible (verificar proyecto y licencia) | decidir en Fase 1 |
| Modelos | descarga de Ollama | caché local en cada nodo (`/usr/share/ollama`) | igual |

Lo que siempre necesita Internet (solo salida): scraping de bancos y series del BdE. Si no hay conexión, el sistema usa la última copia de Postgres e indica la fecha de los datos.

## 5. Electricidad y disponibilidad

- 4 fitlet2 ≈ 6-10 W cada uno; VM según host. Orden de 40-80 W en total (medir con enchufe medidor).
- SAI pequeño para VM y router: evita corrupción de Postgres en cortes.
- BIOS "power on after AC loss" en todo (DESPLIEGUE §3.1).
- Sin SLA: es un sistema personal. Escalar a AWS solo con los disparadores de DESPLIEGUE §13.

## 6. Decisiones para doc

1. Modo por defecto en MVP: **local** (recomendado) o híbrido.
2. ¿0 nube estricto? Si sí: Headscale + Caddy + backup solo USB.
3. LangGraph server: servidor propio FastAPI (recomendado si la imagen oficial exige licencia) o imagen oficial.
