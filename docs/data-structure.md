# Estructura de Datos

Diagramas que muestran la estructura de los datos JSON.

## Diagrama de Clases (Estructura JSON)

```mermaid
classDiagram
    class Combustible {
        +String provincia
        +String empresa
        +String localidad
        +String direccion
        +String combustible
        +Precios precios
        +String vigencia
    }

    class Precios {
        +Number día
        +Number noche
    }

    class ICL {
        +String fecha
        +Number valor
        +String descripcion
    }

    class IPC {
        +Number indice_ipc
        +String mes
        +Number anio
        +String fecha_publicacion
        +String fecha_proximo_informe
    }

    Combustible "1" --> "1" Precios : contiene
```

## Estructura de Archivos

```mermaid
flowchart TB
    subgraph ROOT["data/"]
        subgraph COMB["combustibles/"]
            CL["latest.json"]
            CV1["2026-01-01.json"]
            CV2["2026-01-16.json"]
            CDOTS["..."]
        end

        subgraph ICL["icl/"]
            IL["latest.json"]
            IV1["2026-01-18.json"]
            IV2["2026-01-17.json"]
            IDOTS["..."]
        end

        subgraph IPC["ipc/"]
            PL["latest.json"]
            PV1["2026-01-13.json"]
            PV2["2025-12-13.json"]
            PDOTS["..."]
        end
    end
```

## Ejemplo: Combustible

```json
{
  "provincia": "buenos-aires",
  "empresa": "SHELL",
  "localidad": "LA PLATA",
  "direccion": "AV. 1 1234",
  "combustible": "Nafta Súper",
  "precios": {
    "día": 1899,
    "noche": 1899
  },
  "vigencia": "19/01/2026"
}
```

```mermaid
graph LR
    subgraph combustible["Objeto Combustible"]
        P[provincia: buenos-aires]
        E[empresa: SHELL]
        L[localidad: LA PLATA]
        D[direccion: AV. 1 1234]
        C[combustible: Nafta Súper]
        V[vigencia: 19/01/2026]

        subgraph precios["precios"]
            DIA[día: 1899]
            NOCHE[noche: 1899]
        end
    end
```

## Ejemplo: ICL

```json
{
  "fecha": "18/01/2026",
  "valor": 29.78,
  "descripcion": "ICL - Ley 27.551"
}
```

```mermaid
graph LR
    subgraph icl["Objeto ICL"]
        F[fecha: 18/01/2026]
        V[valor: 29.78]
        D[descripcion: ICL - Ley 27.551]
    end
```

## Ejemplo: IPC

```json
{
  "indice_ipc": 2.8,
  "mes": "diciembre",
  "anio": 2025,
  "fecha_publicacion": "13/01/26",
  "fecha_proximo_informe": "10/2/26"
}
```

```mermaid
graph LR
    subgraph ipc["Objeto IPC"]
        I[indice_ipc: 2.8]
        M[mes: diciembre]
        A[anio: 2025]
        FP[fecha_publicacion: 13/01/26]
        FN[fecha_proximo_informe: 10/2/26]
    end
```

## Flujo de Datos: latest.json vs Versionados

```mermaid
flowchart TB
    SCRAPER["Scraper ejecuta"]

    subgraph SAVE["save_dataset_json()"]
        LATEST["latest.json<br/>(sobrescribe siempre)"]
        VERSION["YYYY-MM-DD.json<br/>(archivo nuevo)"]
    end

    subgraph USE["Uso"]
        API["API lee latest.json<br/>(datos vigentes)"]
        HISTORY["Archivos versionados<br/>(histórico/auditoría)"]
    end

    SCRAPER --> LATEST
    SCRAPER --> VERSION
    LATEST --> API
    VERSION --> HISTORY
```

## Relación entre Endpoints y Datos

```mermaid
flowchart LR
    subgraph ENDPOINTS["Endpoints"]
        E1["GET /api/combustibles/provincia/:p"]
        E2["GET /api/combustibles/empresa/:e"]
        E3["GET /api/combustibles/promedio/:p/:c"]
        E4["GET /api/icl"]
        E5["GET /api/ipc"]
    end

    subgraph DATA["Data Files"]
        DC["data/combustibles/latest.json"]
        DI["data/icl/latest.json"]
        DP["data/ipc/latest.json"]
    end

    E1 --> DC
    E2 --> DC
    E3 --> DC
    E4 --> DI
    E5 --> DP
```
