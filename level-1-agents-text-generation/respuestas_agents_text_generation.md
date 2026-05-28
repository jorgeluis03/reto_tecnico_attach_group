# Agents & Text Generation — Respuestas

## 1. ¿Qué son las Structured Outputs, cómo funcionan internamente y por qué son útiles en producción?

Las structured outputs son un mecanismo que obliga al LLM a devolver su respuesta en un formato JSON válido y tipado, definido previamente por el desarrollador. Dado que las salidas de los modelos de lenguaje no son deterministas, sin esta restricción el modelo podría devolver texto libre, JSON malformado o campos faltantes, lo cual rompe cualquier integración downstream.

**Cómo funcionan internamente:** el proveedor del modelo (OpenAI, Google, Anthropic) recibe junto al prompt un schema JSON o una clase Pydantic que define la estructura esperada. Durante la generación token a token, el modelo restringe su sampling solo a tokens que produzcan un JSON válido conforme al schema. Esto se logra mediante constrained decoding: en cada paso se filtran los tokens que violarían la estructura definida.

**Mi experiencia:** En Rimac Seguros, dentro de una arquitectura multi-agente con Google ADK, definimos las salidas de cada agente con Pydantic (`output_schema=MyModel`). Esto permite que la salida de un agente sea directamente el input válido del siguiente sin necesidad de parsing intermedio ni validaciones manuales. Lo mismo apliqué en el proyecto GovTech con LangChain (`response_schema=MyModel`), donde el sistema jerárquico multi-agente generaba borradores de proyectos de ley con campos bien definidos (título, justificación, artículos, referencias).

**Por qué son útiles en producción:**

- Eliminan errores de parsing entre componentes del sistema
- Permiten integración directa con APIs, bases de datos u otros agentes
- Hacen el sistema predecible y testeable a pesar de la naturaleza no determinista del LLM
- Facilitan la comunicación inter-agente en arquitecturas multi-agente

---

## 2. ¿Cuál es la diferencia entre un Workflow y un Agent? ¿Cuándo usaría uno u otro?

Un **workflow** es una secuencia de pasos predefinida por el desarrollador. Tú decides el orden: A → B → C → D. El LLM ejecuta cada paso, pero no decide cuál es el siguiente. Un **agent** es un sistema donde el LLM razona y decide en tiempo de ejecución qué acción tomar según el input recibido. No conoces de antemano la secuencia de pasos.

**Cuándo usar cada uno:**

- **Workflow:** cuando conoces los pasos necesarios y su orden para completar la tarea. Ofrece predecibilidad, facilidad de debugging y control sobre el flujo.
- **Agent:** cuando no puedes anticipar qué acciones serán necesarias porque dependen del contexto del usuario. El agente razona, selecciona herramientas y decide el camino.

**Mi experiencia concreta:**

En **Rimac Seguros** implementé un copiloto para brokers como agente autónomo con Google ADK. El agente tenía acceso a múltiples tools (APIs productivas) y decidía en cada interacción cuál invocar según la pregunta del broker. No había un camino fijo: podía consultar pólizas, calcular siniestros o buscar documentación según lo que necesitara el usuario.

En el proyecto **GovTech** con LangGraph implementé un workflow: el proceso de análisis de datos sociales y generación de borradores de proyectos de ley seguía pasos definidos (recopilar información → analizar → redactar → validar), con un loop condicional donde un agente evaluador decidía si la información recopilada era suficiente o debía volver a buscar. Los pasos eran conocidos, solo la condición de loop era dinámica.

En la práctica, en producción prefiero workflows por su predecibilidad y facilidad de monitoreo. Reservo agents para escenarios donde la tarea realmente requiere razonamiento dinámico.

---

## 3. Ventajas de las LLM Skills sobre las herramientas MCP

Las **LLM Skills** son instrucciones que guían el comportamiento del agente: le indican cómo ejecutar una tarea correctamente, qué estilo seguir, qué estructura respetar. Las **herramientas MCP** (Model Context Protocol) son integraciones estandarizadas que conectan al agente con sistemas externos mediante un protocolo común.

**Ventajas de las Skills sobre MCP:**

- **Control sobre el comportamiento:** las skills definen _cómo_ debe actuar el agente, no solo _qué_ puede hacer. Puedes guiar razonamiento, formato y calidad de respuesta.
- **Sin dependencia de infraestructura externa:** no requieren servidor corriendo ni configuración de transporte (stdio/HTTP).
- **Menor latencia:** la skill es parte del contexto del prompt, no hay llamadas de red adicionales.
- **Iteración rápida:** modificar una skill es editar un archivo de texto; modificar un MCP requiere desplegar o reiniciar un servidor.
- **Composabilidad:** puedes combinar múltiples skills fácilmente en un mismo agente sin conflictos de protocolo.

**Cuándo MCP es mejor:** cuando necesitas acceso determinista a sistemas externos (bases de datos, APIs, servicios cloud) con un protocolo estandarizado que cualquier cliente MCP pueda consumir.

**Mi experiencia con Skills:**

- Skills de Anthropic para structuring de prompts y evaluación
- Skills de Google (design-an-interface, diagnose, tdd) orientadas a fundamentos de software engineering, que recientemente Google DeepMind ha enfatizado como más importantes que nunca para el desarrollo con IA
- Skills propias para definir estándares de código y arquitectura antes de implementar

**Mi experiencia con MCP:**

- **MCPs custom construidos en Rimac:** servidores MCP propios para consultar MySQL, Oracle y DynamoDB, ya que en su momento no existían soluciones oficiales confiables para nuestro caso de uso.
- **MCPs oficiales de AWS:** CloudWatch (monitoreo y logs), DynamoDB, Aurora MySQL, Lambda, S3, IAM, y AWS Documentation MCP Server para acceso a documentación actualizada.
- **Otros MCPs:** Jira (gestión de tareas), Git, GitHub, Filesystem.

---

## 4. ¿Cómo funciona Retrieval Augmented Generation (RAG)?

RAG es una arquitectura que combina búsqueda de información relevante (retrieval) con generación de texto (generation) para que el LLM responda basándose en datos específicos y actualizados, no solo en su conocimiento de entrenamiento.

**Flujo básico:**

1. El usuario hace una pregunta
2. La pregunta se convierte en un vector (embedding)
3. Se buscan los documentos más similares en una base de datos vectorial
4. Los documentos recuperados se inyectan como contexto en el prompt
5. El LLM genera una respuesta fundamentada en esos documentos

**Modelos de embeddings:**

- OpenAI: text-embedding-3-small, text-embedding-3-large
- Google: Gemini Embeddings (el que uso vía Vertex AI)
- Open-source: sentence-transformers, BGE

**Métricas de distancia:**

- **Cosine similarity:** mide el ángulo entre vectores, ideal cuando importa la dirección semántica más que la magnitud. Es la más usada.
- **Euclidean (L2):** distancia geométrica directa entre puntos. Sensible a la magnitud.
- **Dot product:** similar a cosine pero sin normalizar. Útil cuando la magnitud del vector tiene significado.

**Variantes de RAG:**

- **Naive RAG:** flujo básico descrito arriba, query → retrieve → generate.
- **Advanced RAG:** incluye mejoras en la indexación (semantic chunking) y en el retrieval (re-ranking, hybrid search).
- **Agentic RAG / Self-RAG:** un agente evalúa si la información recuperada es suficiente y decide si generar la respuesta o volver a buscar con una query reformulada.

**Casos de uso:**

- Asistentes sobre documentación interna de empresa
- Chatbots legales sobre legislación vigente
- Soporte técnico basado en knowledge bases
- Q&A sobre documentos financieros o de seguros

**Mi experiencia:**

En **Legalizate** indexé +1,970 páginas de legislación peruana usando ChromaDB con Gemini Embeddings. Implementé semantic chunking para respetar la estructura de los artículos legales y top-k retrieval con re-ranking para mejorar la relevancia.

En **Rimac Seguros** usamos Pinecone (por su soporte enterprise y escalabilidad) con Gemini Embeddings vía Vertex AI para que los agentes consulten documentación técnica interna.

En **GovTech** implementé Agentic RAG: un agente orquestador lanzaba agentes RAG en paralelo para buscar información legal, recibía sus resultados y decidía si eran suficientes o debía reformular la búsqueda. Esto se implementó como un loop condicional en LangGraph.

Para evaluación, usé un enfoque de golden Q&A: definí preguntas cuya respuesta esperada conocía, ejecuté el pipeline RAG y comparé si la respuesta contenía la información correcta. Si no, iteraba sobre el prompt, los parámetros de retrieval (top-k, umbral de similaridad) o la estrategia de chunking.

---

## 5. Diferencia entre Few-shot Prompting, Prompt-chaining y Fine-tuning

**Few-shot prompting** consiste en incluir ejemplos concretos dentro del prompt para que el modelo entienda el formato, estilo o patrón esperado de respuesta. No modificas el modelo, solo le muestras cómo debe responder.

**Prompt-chaining** es descomponer una tarea compleja en múltiples llamadas secuenciales al LLM, donde la salida de una se convierte en la entrada de la siguiente. Cada paso resuelve una subtarea específica.

**Fine-tuning** es reentrenar el modelo (o una capa de adaptación) con datos propios para modificar su comportamiento base. Cambia los pesos del modelo.

**Cuándo usar cada uno:**

| Técnica         | Usar cuando...                                               | No usar cuando...                                              |
| --------------- | ------------------------------------------------------------ | -------------------------------------------------------------- |
| Few-shot        | Necesitas formato/estilo consistente sin modificar el modelo | Tienes miles de ejemplos y el prompt se vuelve demasiado largo |
| Prompt-chaining | La tarea es compleja y dividirla en pasos mejora la calidad  | La tarea es simple y una sola llamada basta                    |
| Fine-tuning     | Necesitas cambiar el comportamiento fundamental del modelo   | La información cambia constantemente (mejor usar RAG)          |

**Mi experiencia:**

**Few-shot:** En Rimac, el agente de migración de conexiones MySQL a OCI tenía en sus prompts y skills ejemplos concretos de cómo estructurar el código y las carpetas del proyecto. Sin estos ejemplos, cada ejecución producía una estructura diferente que aunque funcionaba, no mantenía el estándar del equipo. También uso few-shot para definir el formato exacto de output e input entre agentes.

**Prompt-chaining:** Es exactamente lo que implementé en GovTech con LangGraph. El proceso de generar un borrador de proyecto de ley se divide en pasos: primero recopilar datos relevantes, luego analizarlos, después redactar secciones específicas, y finalmente consolidar. Cada paso recibe el output del anterior como contexto.

**Fine-tuning:** No lo he realizado en producción, pero sé cuándo sería necesario: cuando quieres modificar el comportamiento base del modelo (por ejemplo, que siempre responda en terminología específica de seguros sin necesidad de instrucciones). Sin embargo, para información que cambia constantemente, como documentación técnica o pólizas actualizadas, un RAG es mejor opción porque no requiere reentrenar el modelo cada vez.

---

## 6. ¿Qué es LLM-as-a-Judge? Position bias y verbosity bias

**LLM-as-a-Judge** es usar un modelo de lenguaje como evaluador automático de la calidad de respuestas generadas por otro modelo (o por el mismo sistema). En lugar de depender exclusivamente de evaluación humana, se le pide al LLM que puntúe, compare o califique outputs según criterios definidos.

**Mi experiencia:**

Lo apliqué en el proceso de prompt engineering y evaluación en Rimac, siguiendo la guía de Anthropic. El flujo era:

1. Un agente genera casos de input (preguntas representativas del dominio)
2. El agente principal procesa esos inputs y genera respuestas
3. Un agente juez evalúa cada respuesta asignando un puntaje y un razonamiento
4. Se promedian los puntajes para obtener una métrica general

Esto lo visualizaba en una interfaz con Streamlit donde podía ver la evolución del score. Luego aplicaba técnicas de prompt engineering, volvía a iterar y medía si el puntaje mejoraba. Este proceso permitió que modelos más económicos como Haiku, Gemini Flash o GPT-4o mini hicieran bien el trabajo, ahorrando costos significativos en producción.

**Modos de fallo principales:**

**Position bias:** el LLM evaluador tiende a favorecer respuestas según su posición en el prompt. Si comparas Respuesta A vs Respuesta B, el modelo puede preferir sistemáticamente la primera (o la última), independientemente de su calidad real. Para mitigarlo se puede hacer swap de posiciones (evaluar A vs B y luego B vs A) y promediar, o evaluar cada respuesta por separado en lugar de comparativamente.

**Verbosity bias:** el LLM evaluador tiende a puntuar mejor las respuestas más largas y detalladas, asumiendo que más texto implica más calidad. Esto es problemático porque una respuesta concisa y precisa puede ser superior a una extensa pero redundante. Para mitigarlo se pueden incluir criterios explícitos en el prompt del juez que penalicen redundancia, o usar métricas específicas como "¿responde la pregunta directamente?" en lugar de evaluaciones generales de calidad.

Otros sesgos relevantes: **self-enhancement bias** (el modelo tiende a preferir respuestas generadas por sí mismo) y **limited reasoning** (el juez puede no captar errores sutiles de dominio específico). Por eso LLM-as-a-Judge funciona mejor como complemento de evaluación humana, no como reemplazo total.
