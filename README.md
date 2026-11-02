# CodificaMed — Codificación Automática CIE-10 de Historias Clínicas con PLN

Sistema inteligente basado en **Procesamiento de Lenguaje Natural (PLN)** y la metodología **CRISP-ML(Q)** para la codificación automática de diagnósticos **CIE-10** a partir de notas médicas de evolución en texto libre, con extracción de evidencia justificativa y detección robusta de negaciones/descartes.

Materia: **Base de Conocimiento**  
Unidad: **Procesamiento de Lenguaje Natural**  
Institución: **Facultad de Informática y Electrónica (FIE) - ESPOCH**  
Docente: **Ing. Isaac Torres**

---

## 1. Problemática y Objetivos de Negocio

En la Red Pública Integral de Salud (MSP, IESS) y clínicas privadas del Ecuador, cada atención médica ambulatoria o de emergencia debe registrarse con sus códigos **CIE-10**. Estos códigos determinan:
1. La facturación médica y cruce de cuentas entre prestadores.
2. La prevención de **glosas médicas** (objeciones de pago por auditoría).
3. Las estadísticas epidemiológicas nacionales y asignación de presupuesto hospitalario.

Actualmente, la codificación es manual: un médico auditor lee texto libre con abreviaturas no estandarizadas (*"HTA"*, *"DM2"*, *"dolor abd"*), errores de tipeo y estructuras de negación (*"niega fiebre"*, *"se descarta neumonía"*). Un error en la asignación retrasa los pagos y distorsiona las estadísticas de morbilidad.

**CodificaMed** recibe una nota médica en texto libre y sugiere los códigos CIE-10 pertinentes con su **evidencia textual exacta**, distinguiendo con rigor un diagnóstico confirmado de uno negado o descartado.

---

## 2. Metodología: Las 6 Fases de CRISP-ML(Q)

El proyecto sigue formalmente el estándar *Cross-Industry Standard Process for Machine Learning with Quality Assurance* (Studer et al., 2021):

| Fase CRISP-ML(Q) | Implementación en CodificaMed | Archivo(s) Responsable(s) |
| :--- | :--- | :--- |
| **1. Comprensión del Negocio y Datos** | Definición de objetivos clínicos (facturación, prevención de glosas, auditoría con evidencia). Restricción ética: prohibición estricta de historias clínicas reales (uso de corpus CodiEsp / sintéticos). | `README.md`, `INFORME_EJECUTIVO_CODIFICAMED.md` |
| **2. Ingeniería de Datos** | Normalización Unicode (NFC), expansión canónica de abreviaturas médicas frecuentes (*HTA*, *DM2*, *ITU*, *IAM*, etc.), segmentación de oraciones y delimitación de signos vitales. | `app/pipeline/preprocesamiento.py` |
| **3. Ingeniería del Modelo** | Pipeline híbrido de PLN: <br>a) **Recuperación RAG:** Búsqueda léxica BM25 sobre catálogo oficial CIE-10.<br>b) **Detección de Negaciones:** Motor NegEx en español con gatillos pre/post negación y delimitadores de ámbito.<br>c) **Inferencia Estructurada:** Generación JSON Schema garantizada con LLM local (Ollama) o cloud (Claude). | `app/pipeline/catalogo.py`, `indexacion.py`, `negacion.py`, `app/llm/` |
| **4. Aseguramiento de Calidad** | Auditoría automática en vivo: verificación de existencia oficial en catálogo CIE-10, comprobación de presencia literal de la evidencia textual en la nota, y evaluación cuantitativa (Precisión, Recall, F1-Score). | `app/pipeline/evaluacion.py`, `app/pipeline/orquestador.py` |
| **5. Despliegue** | API REST asíncrona con FastAPI, base de datos SQLite embebida, arquitectura desacoplada en capas e interfaz web SPA accesible e intuitiva. | `app/main.py`, `app/db.py`, `app/static/` |
| **6. Monitoreo y Mantenimiento** | Registro histórico en SQLite, telemetría de latencias por etapa, conteo de tokens/caracteres, auditoría de confirmados vs descartados, y benchmark comparativo Local vs Nube. | `app/db.py`, `app/pipeline/orquestador.py` |

---

## 3. Guía de Instalación y Ejecución

### Requisitos Previos
* **Python 3.11 o superior** (asegúrate de marcar *"Add python.exe to PATH"* durante la instalación).
* **Ollama** (para ejecución con modelo local). Descárgalo de [https://ollama.com](https://ollama.com).

### Paso 1: Instalar Dependencias
En Windows, haz doble clic en `instalar.bat` o ejecuta en consola:
```bash
python -m pip install -r requirements.txt
```

### Paso 2: Descargar el Modelo Local
Inicia Ollama y descarga el modelo recomendado según tu equipo:
```bash
# Modelo ligero y rápido (funciona en CPU y RAM estándar):
ollama pull llama3.2:latest

# Alternativa para equipos con 8 GB o más de VRAM / RAM:
ollama pull mistral:latest
```

### Paso 3: Configurar Variables de Entorno
Copia el archivo de plantilla a `.env`:
```bash
# En Windows:
copy .env.example .env

# En Linux / Mac:
cp .env.example .env
```
Edita `.env` si deseas ajustar el modelo o ingresar tu clave de Claude:
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:latest
ANTHROPIC_API_KEY=sk-ant-api...  # Opcional si solo usas el modelo local
PUERTO=8001
```

### Paso 4: Iniciar la Aplicación
Haz doble clic en `iniciar.bat` (o ejecuta `./iniciar.sh` en Mac/Linux).
Abre tu navegador en:
**http://localhost:8001**

---

## 4. Estructura del Proyecto

```
codificamed/
├── .env.example                 # Plantilla de configuración
├── .gitignore                   # Exclusión de credenciales y base de datos
├── README.md                    # Documentación técnica completa
├── requirements.txt             # Dependencias de Python
├── iniciar.bat / iniciar.sh     # Script de arranque del servidor
├── instalar.bat / instalar.sh   # Script de instalación de dependencias
├── INFORME_EJECUTIVO_CODIFICAMED.md # Informe formal de las 6 fases de CRISP-ML(Q)
├── GUIA_GRABACION_VIDEO.md      # Guion y pautas para el video demostrativo (<= 10 min)
├── app/
│   ├── __init__.py
│   ├── config.py                # Lectura de variables de entorno
│   ├── db.py                    # Persistencia transaccional SQLite
│   ├── main.py                  # API REST FastAPI y servidor web
│   ├── llm/                     # Capa desacoplada de modelos
│   │   ├── base.py              # Clase abstracta ProveedorLLM y extracción JSON
│   │   ├── ollama.py            # Conector Ollama (modelo local)
│   │   ├── claude.py            # Conector Claude API (Anthropic Tool Use)
│   │   └── simulado.py          # Conector mock para tests unitarios
│   ├── pipeline/                # Lógica del pipeline de PLN
│   │   ├── catalogo.py          # Catálogo estructurado CIE-10 oficial
│   │   ├── preprocesamiento.py  # Expansión de siglas y normalización
│   │   ├── negacion.py          # Motor NegEx clínico en español
│   │   ├── indexacion.py        # Recuperación léxica BM25
│   │   ├── evaluacion.py        # Casos patrón anotados y métricas (P, R, F1)
│   │   └── orquestador.py       # Coordinador de las 6 fases del pipeline
│   └── static/                  # Frontend Web SPA
│       ├── index.html           # Estructura semántica accesible
│       ├── styles.css           # Tokens de diseño y estilos clínicos
│       └── app.js               # Enrutamiento, eventos e interacción
├── ejemplos/                    # Notas clínicas de ejemplo (CodiEsp / Sintéticas)
│   ├── casos_clinicos_ficticios.json
│   └── caso_01_dm2_itu.txt
└── tests/
    ├── prueba_pipeline.py       # Batería automatizada de pruebas end-to-end
    └── test_ollama_real.py      # Test de inferencia clínica real con Ollama
```

---

## 5. Pruebas y Validación Automatizada

Para ejecutar la batería completa de pruebas que valida el preprocesamiento, la detección de negación, el índice BM25, el cálculo de métricas y los endpoints REST:
```bash
python tests/prueba_pipeline.py
```

---

## 6. Consideraciones Éticas y Limitaciones

* **Privacidad de Datos de Salud:** Por normativa bioética y legal (Ley Orgánica de Salud del Ecuador y normativas internacionales HIPAA/GDPR), **está estrictamente prohibido procesar historias clínicas reales sin anonimización certificada**. La aplicación fue diseñada para operar con casos del corpus público CodiEsp o casos sintéticos/ficticios.
* **Modelo Local como Garantía de Privacidad:** El uso del modelo local en Ollama asegura que ninguna información médica salga del equipo del hospital o prestador hacia servidores de terceros en internet.
* **Prototipo de Soporte:** El sistema es un asistente para el codificador humano (*human-in-the-loop*); la decisión y validación final de la codificación diagnóstica recae en el profesional de salud.
