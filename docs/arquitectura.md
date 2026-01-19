# Arquitectura General

Diagrama que muestra la arquitectura completa del sistema Argly.

```mermaid
flowchart TB
    subgraph GH["GitHub Actions (Cron Jobs)"]
        CRON_COMB["⏰ Combustibles<br/>Días 1 y 16"]
        CRON_ICL["⏰ ICL<br/>4x/día"]
        CRON_IPC["⏰ IPC<br/>Días 10-14/mes"]
    end

    subgraph SCRAPERS["Scrapers (Python + BeautifulSoup)"]
        SC["scraper_combustibles.py"]
        SI["scraper_icl.py"]
        SP["scraper_ipc.py"]
    end

    subgraph SOURCES["Fuentes Públicas"]
        COMB_AR["combustibles.ar"]
        BCRA["bcra.gob.ar"]
        INDEC["indec.gob.ar"]
    end

    subgraph DATA["Capa de Datos (JSON)"]
        DC["data/combustibles/<br/>latest.json"]
        DI["data/icl/<br/>latest.json"]
        DP["data/ipc/<br/>latest.json"]
    end

    subgraph API["API REST (Flask)"]
        APP["app.py"]
        subgraph ROUTES["Blueprints"]
            RC["combustibles_bp"]
            RI["icl_bp"]
            RIP["ipc_bp"]
        end
        DL["data_loader.py"]
    end

    subgraph DEPLOY["Despliegue"]
        VERCEL["Vercel"]
        URL["api.argly.com.ar"]
    end

    CLIENT["👤 Cliente HTTP"]

    %% Flujo de Scraping
    CRON_COMB --> SC
    CRON_ICL --> SI
    CRON_IPC --> SP

    SC --> |HTTP GET| COMB_AR
    SI --> |HTTP GET| BCRA
    SP --> |HTTP GET| INDEC

    SC --> |save_dataset_json| DC
    SI --> |save_dataset_json| DI
    SP --> |save_dataset_json| DP

    %% Flujo de API
    DC --> DL
    DI --> DL
    DP --> DL

    DL --> RC
    DL --> RI
    DL --> RIP

    RC --> APP
    RI --> APP
    RIP --> APP

    APP --> VERCEL
    VERCEL --> URL

    CLIENT --> |GET /api/*| URL
```

## Componentes Principales

| Componente | Descripción |
|------------|-------------|
| **GitHub Actions** | Ejecuta scrapers automáticamente según cronograma |
| **Scrapers** | Recolectan datos de fuentes públicas argentinas |
| **Data Layer** | Almacena JSONs con datos históricos y vigentes |
| **Flask API** | Expone endpoints REST para consumo público |
| **Vercel** | Hosting serverless con deploy automático |
