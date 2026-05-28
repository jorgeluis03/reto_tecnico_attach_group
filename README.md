# Reto Técnico — AI Engineer

Repositorio con mis respuestas al reto técnico para el puesto de AI Engineer en Attach Group.

---

## Sobre mi perfil

Mi experiencia fuerte está en **agentes de IA, RAG y automatización con LLMs** (Level 1) y en **ingeniería de software aplicada a producción** (Level 0). En los niveles de generación creativa y deep learning (Levels 2-3) soy transparente sobre qué he implementado y qué no — donde no tengo experiencia directa, propongo arquitecturas fundamentadas en investigación técnica en lugar de inventar experiencia.

---

## Estructura del repositorio

| Carpeta                                                                          | Nivel                         | Contenido                                                                |
| -------------------------------------------------------------------------------- | ----------------------------- | ------------------------------------------------------------------------ |
| [`level-0-fundamenta-software-engineer/`](level-0-fundamenta-software-engineer/) | Fundamentos de Software       | Respuestas sobre Docker, IaC, shell, gestión de paquetes                 |
| [`level-1-agents-text-generation/`](level-1-agents-text-generation/)             | Agentes y Generación de Texto | Structured outputs, RAG, agents vs workflows, MCP/Skills, LLM-as-a-Judge |
| [`level-2-creative-pipeline/`](level-2-creative-pipeline/)                       | Generación Creativa           | Pipeline funcional (con código) + respuestas teóricas                    |
| [`level-3-voice-conversion/`](level-3-voice-conversion/)                         | Deep Learning y Voz           | Diseño de sistema de voice conversion en tiempo real                     |
| [`level-4-gcp-video-batch/`](level-4-gcp-video-batch/)                           | Caso Abierto GCP              | Arquitectura batch para generación de video con Veo 3.1                  |

---

## Cómo navegar cada nivel

Cada carpeta contiene uno o dos archivos principales:

- **`respuestas_*.md`** — Respuestas directas a las preguntas conceptuales del reto (experiencia, comparaciones, explicaciones).
- **`README.md`** — Solución técnica detallada al problema de diseño/arquitectura del nivel (cuando aplica). Incluye diagramas, justificación de decisiones y trade-offs.

### Guía rápida por archivo

| Archivo                                                                                                               | Qué encontrar ahí                                                                            |
| --------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| [Level 0 — respuestas_fundamentos.md](level-0-fundamenta-software-engineer/respuestas_fundamentos.md)                 | Docker, IaC (Serverless Framework), shell scripting, lenguajes, puerto 22                    |
| [Level 1 — respuestas_agents_text_generation.md](level-1-agents-text-generation/respuestas_agents_text_generation.md) | Structured outputs, workflows vs agents, RAG, few-shot vs fine-tuning, LLM-as-a-Judge        |
| [Level 2 — respuestas_generacion_creativa.md](level-2-creative-pipeline/respuestas_generacion_creativa.md)            | Experiencia con modelos de imagen y avatares (honesto: no es mi área fuerte)                 |
| [Level 2 — README.md](level-2-creative-pipeline/README.md)                                                            | **Pipeline funcional** que garantiza fidelidad de brand assets con IA generativa para fondos |
| [Level 3 — respuestas_deep_learning.md](level-3-voice-conversion/respuestas_deep_learning.md)                         | Validación de clasificadores de imagen (honesto: experiencia limitada)                       |
| [Level 3 — README.md](level-3-voice-conversion/README.md)                                                             | **Diseño completo** de sistema de voice conversion en tiempo real con RVC                    |
| [Level 4 — README.md](level-4-gcp-video-batch/README.md)                                                              | **Arquitectura GCP** para batch de 25 videos/día con Veo 3.1                                 |

---

## Niveles con código funcional

El **Level 2** incluye un pipeline ejecutable:

```bash
cd level-2-creative-pipeline
uv sync
uv run python src/cli.py \
  --prompt "tropical beach sunset" \
  --template post \
  --headline "SUMMER SALE" \
  --legal-text "Términos y condiciones aplican."
```

Requiere: Python 3.13+, `uv`, cuenta de Google Cloud con Vertex AI habilitado. Ver [instrucciones completas](level-2-creative-pipeline/README.md#instalacion-paso-a-paso).

---

## Disclaimer de honestidad

En varias respuestas digo explícitamente "no tengo experiencia con esto" o "no lo he llevado a producción". Es intencional. Prefiero ser directo sobre mis límites actuales que fabricar experiencia que no podría defender en una conversación técnica.

Mis áreas fuertes: agentes con Google ADK, arquitecturas RAG, pipelines con LangChain/LangGraph, infraestructura serverless en AWS, y automatización con LLMs en producción (Rimac Seguros / Personal).

Mis áreas en desarrollo: generación de imágenes/video, deep learning aplicado a visión, GCP a nivel productivo (aunque diseño sobre GCP en este reto con fundamento técnico sólido).
