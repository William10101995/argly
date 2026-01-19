# Flujo de Requests API

Diagramas que muestran cómo se procesan las peticiones HTTP.

## Flujo General de Request

```mermaid
flowchart TB
    CLIENT["👤 Cliente HTTP"]

    subgraph VERCEL["Vercel Edge"]
        EDGE["Edge Network"]
    end

    subgraph FLASK["Flask Application"]
        INDEX["index.py<br/>(WSGI entry)"]
        APP["app.py<br/>(create_app)"]

        subgraph MW["Middleware"]
            CORS["flask-cors"]
            LIMIT["flask-limiter<br/>100 req/min"]
        end

        subgraph ROUTES["Routes"]
            R1["/api/combustibles/*"]
            R2["/api/icl"]
            R3["/api/ipc"]
        end

        subgraph SERVICES["Services"]
            DL["data_loader.py"]
        end

        subgraph UTILS["Utils"]
            RESP["responses.py"]
        end
    end

    subgraph DATA["Data Layer"]
        JSON["data/*/latest.json"]
    end

    CLIENT --> |HTTPS| EDGE
    EDGE --> INDEX
    INDEX --> APP
    APP --> MW
    MW --> ROUTES
    ROUTES --> DL
    DL --> |read| JSON
    JSON --> DL
    DL --> RESP
    RESP --> |JSON response| CLIENT
```

## Endpoint: Combustibles por Provincia

```mermaid
sequenceDiagram
    participant C as Cliente
    participant R as combustibles_bp
    participant DL as data_loader
    participant FS as FileSystem

    C->>R: GET /api/combustibles/provincia/buenos-aires
    R->>DL: get_combustibles_by_provincia("buenos-aires")
    DL->>DL: normalize("buenos-aires") → "buenos aires"
    DL->>FS: read data/combustibles/latest.json
    FS-->>DL: Array[gasolineras]
    DL->>DL: filter(provincia == "buenos aires")
    DL-->>R: Array[gasolineras filtradas]
    R->>R: success(data)
    R-->>C: {"data": [...]}
```

## Endpoint: Promedio de Combustible

Este es el endpoint más complejo, con normalización de texto.

```mermaid
sequenceDiagram
    participant C as Cliente
    participant R as combustibles_bp
    participant DL as data_loader
    participant FS as FileSystem

    C->>R: GET /api/combustibles/promedio/buenos-aires/nafta-super
    R->>DL: get_promedio_combustible("buenos-aires", "nafta-super")

    Note over DL: Normalización
    DL->>DL: _normalize("buenos-aires") → "buenos aires"
    DL->>DL: _normalize("nafta-super") → "nafta super"

    DL->>FS: read data/combustibles/latest.json
    FS-->>DL: Array[gasolineras]

    Note over DL: Filtrado y cálculo
    DL->>DL: filter by provincia
    DL->>DL: filter by combustible
    DL->>DL: extract precios[día] + precios[noche]
    DL->>DL: avg = sum(precios) / len(precios)
    DL->>DL: round(avg, 2)

    DL-->>R: {provincia, combustible, precio_promedio}
    R->>R: success(data)
    R-->>C: {"data": {"precio_promedio": 1899.50}}
```

## Endpoint: ICL

```mermaid
sequenceDiagram
    participant C as Cliente
    participant R as icl_bp
    participant DL as data_loader
    participant FS as FileSystem

    C->>R: GET /api/icl
    R->>DL: get_icl()
    DL->>FS: read data/icl/latest.json
    FS-->>DL: Array[{fecha, valor}]
    DL->>DL: return last item
    DL-->>R: {fecha, valor}
    R->>R: success(data)
    R-->>C: {"data": {"fecha": "18/01/2026", "valor": 29.78}}
```

## Manejo de Errores

```mermaid
flowchart TB
    REQ["Request entrante"]

    REQ --> LIMIT{Rate Limit<br/>100/min?}
    LIMIT --> |Excedido| E429["429 Too Many Requests"]
    LIMIT --> |OK| ROUTE{Ruta existe?}

    ROUTE --> |No| E404["404 Not Found"]
    ROUTE --> |Sí| PARAM{Parámetros<br/>válidos?}

    PARAM --> |No| E400["400 Bad Request"]
    PARAM --> |Sí| DATA{Datos<br/>encontrados?}

    DATA --> |No| E404_2["404 No data"]
    DATA --> |Sí| SUCCESS["200 OK + JSON"]
```
