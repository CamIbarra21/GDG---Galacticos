# Build with Gemma - GDG Lima

## Galacticos Tech — Educación offline con IA para zonas rurales del Perú

> Build with Gemma - AI Competition | Track: **Local AI & Edge Intelligence**

### 🎯 Propuesta

En muchas zonas rurales del Perú, el acceso a internet es limitado o inexistente, lo que restringe severamente el acceso de niños de nivel primario a materiales de apoyo educativo, tutorías o resolución de dudas fuera del horario de clase. Los docentes suelen atender aulas con niveles muy heterogéneos y pocas herramientas para monitorear el avance individual de cada estudiante.

**Galacticos Tech** es una plataforma educativa que corre **Gemma 4 completamente local** (sin depender de internet), pensada para nivel primario, que ofrece:

- Un **tutor conversacional** que responde dudas de los estudiantes en lenguaje simple y adaptado a su edad.
- **Materiales educativos** (texto, imágenes y video) organizados por materia y tema.
- Un **test diagnóstico inicial** que determina el nivel del estudiante y personaliza su ruta de aprendizaje.
- Un **panel de monitoreo para el profesor**, con seguimiento del progreso de cada alumno.

La clave del proyecto es que **todo funciona sin conexión a internet**: un solo dispositivo actúa como "servidor local" del colegio (una laptop o mini-PC), y los estudiantes acceden desde tablets o laptops por red WiFi local, sin necesidad de una señal de datos externa.

### ODS y track

- **Track:** Local AI & Edge Intelligence
- **ODS:** 4 (Educación de Calidad), y de forma secundaria 10 (Reducción de las Desigualdades) por el
  enfoque en cerrar la brecha de acceso entre zonas urbanas y rurales.

### Fuentes de datos / contenido

- Currículo Nacional y materiales de [MINEDU](https://www.gob.pe/minedu) / [Perú Educa](https://www.perueduca.pe/).
- Datos abiertos de infraestructura educativa (conectividad rural) del [Portal de Datos Abiertos del Estado Peruano](https://www.datosabiertos.gob.pe/), usados para justificar el problema en el writeup.

---

## 🏗️ Arquitectura

La app se divide en un frontend cliente (Angular) y un backend local que corre en un único dispositivo dentro del colegio, actuando como servidor edge sin salida a internet.

```
┌─────────────────────────────────────────────┐
│              Angular (Frontend)              │
│   Corre en tablets/laptops de estudiantes     │
│              y del profesor                   │
└───────────────────┬───────────────────────────┘
                    │  HTTP / WebSocket
                    │  (RED LOCAL — sin internet)
                    ▼
┌─────────────────────────────────────────────┐
│         Backend: Python + FastAPI             │
│      Corre en el "servidor local" del colegio │
│                                                │
│   ┌──────────────┐      ┌──────────────────┐ │
│   │  Google ADK   │─────▶│      Ollama       │ │
│   │ (orquesta al  │      │  (sirve Gemma 4   │ │
│   │ agente tutor, │      │  localmente:      │ │
│   │ tools, sesión)│      │  gemma4:e2b/e4b)  │ │
│   └──────────────┘      └──────────────────┘ │
│                                                │
│   ┌──────────────┐      ┌──────────────────┐ │
│   │  Base de datos│      │  Almacenamiento   │ │
│   │ (SQLite/       │      │  de archivos      │ │
│   │  PostgreSQL)   │      │ (materiales:      │ │
│   │ usuarios,      │      │  texto/imagen/    │ │
│   │ materiales,    │      │  video, guardados │ │
│   │ progreso, test │      │  localmente)      │ │
│   └──────────────┘      └──────────────────┘ │
└─────────────────────────────────────────────┘
```

**Notas de diseño:**

- Google ADK se integra con Ollama a través del conector **LiteLLM**, lo que permite mantener una arquitectura de agente (con herramientas, memoria y sesiones) mientras el modelo corre 100% local.
- Los videos y materiales se almacenan localmente (no embebidos desde YouTube u otro servicio que requiera internet).

### Stack tecnológico

| Componente | Tecnología |
|---|---|
| Frontend | Angular |
| Diseño UI | Stitch |
| Backend / API | Python + FastAPI |
| Orquestación del agente | Google ADK |
| Modelo LLM | Gemma 4 (vía Ollama, local) |
| Control de versiones | GitHub |

---

## 🧩 Módulos principales

### Vista Estudiante

1. **Test diagnóstico inicial** — evaluación corta que determina el nivel actual del estudiante por materia.
2. **Materiales por tema/materia** — contenido organizado jerárquicamente (ej. Matemática > Fracciones > Suma de fracciones), en texto, imagen y video.
3. **Chatbot tutor** — agente basado en ADK + Gemma 4 que responde dudas en lenguaje simple, adaptado a niños de primaria.
4. **Recomendaciones** — sugerencia del siguiente tema o refuerzo, según resultados del test y progreso.
5. **Quizzes cortos por tema** — miden avance y alimentan el módulo de progreso.

### Vista Profesor

6. **Gestión de contenido** — subir y organizar materiales por materia/tema, con nivel de dificultad.
7. **Dashboard de monitoreo** — progreso general y por estudiante: temas completados, resultados de quizzes, tiempo de uso, alertas de dificultad recurrente.
8. **Vista de detalle por alumno** — historial de interacciones con el chatbot, útil para detectar en qué se traba cada estudiante.

### Prioridad para el MVP (sprint de 1 día)

1. Materiales (texto + imagen, video si alcanza el tiempo)
2. Chatbot tutor (ADK + Ollama + Gemma 4) — núcleo técnico del proyecto
3. Test diagnóstico inicial simple (5-10 preguntas)
4. Dashboard de profesor básico (lista de materiales + progreso simple)

---

## 📋 Pendientes

- [ ] Definir nombre final del proyecto
- [ ] Definir esquema de base de datos (usuarios, materiales, progreso, resultados de test)
- [ ] Definir herramientas (tools) específicas del agente ADK
- [ ] Definir set inicial de materiales/temas para la demo (currículo de qué grado/materia)
