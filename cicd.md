# Documentación de CI/CD (Integración y Despliegue Continuo)

Este documento describe el flujo completo de CI/CD para el backend/API **argly**, el cual utiliza GitHub Actions en conjunto con la librería compartida (*shared-library*).

## Diagrama de Flujo (Mermaid)

El siguiente diagrama ilustra cómo funciona la integración y el despliegue hacia AWS Lambda y ECR:

```mermaid
flowchart TD
    %% Roles y Ramas
    Dev([Desarrollador])
    PR{Pull Request\na main}
    Merge{Merge a\nmain}

    %% Repositorio Actual
    subgraph Repo Actual ["argly (Repositorio API)"]
        CI_Trigger[Se activa ci.yml]
        CD_Trigger[Se activa cd.yml]
    end

    %% Librería Compartida
    subgraph Shared Library ["xlmriosx/shared-library"]
        CI_Lib[[Workflow: ci-python.yml]]
        CD_Lib[[Workflow: AWS-Lambda-deploy.yml]]
    end

    %% Tareas CI
    subgraph Tareas CI ["Validaciones Python"]
        PySetup[Setup Python 3.12]
        Pytest[Pruebas con Pytest]
    end

    %% Tareas CD
    subgraph Tareas CD ["Construcción y Despliegue"]
        BuildImg[Construir Imagen Docker]
        PushECR[Push a Amazon ECR\nargly-api]
        OIDC[Autenticación AWS OIDC\nAsumir Rol IAM]
        UpdateLambda[Actualizar AWS Lambda\nargly-function]
    end

    %% Destino
    AWS_ECR[(Amazon ECR:\nargly-api)]
    AWS_Lambda((AWS Lambda:\nargly-function))
    Notificaciones[[Notificaciones:\nDiscord]]

    %% Flujo CI
    Dev -->|Crea o actualiza| PR
    PR --> CI_Trigger
    CI_Trigger -->|Llama a| CI_Lib
    CI_Lib --> PySetup
    PySetup --> Pytest
    Pytest -.->|Informa estado| Notificaciones

    %% Flujo CD
    Dev -->|Aprueba y fusiona| Merge
    Merge --> CD_Trigger
    CD_Trigger -->|Llama a| CD_Lib
    CD_Lib --> OIDC
    OIDC -->|Obtiene credenciales| BuildImg
    BuildImg --> PushECR
    PushECR -->|Sube imagen| AWS_ECR
    PushECR --> UpdateLambda
    UpdateLambda -->|Despliega nueva imagen| AWS_Lambda
    UpdateLambda -.->|Informa estado| Notificaciones

    %% Estilos
    classDef repo fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef shared fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef aws fill:#ffcc80,stroke:#e65100,stroke-width:2px;
```

## Explicación del Flujo

### 1. Integración Continua (CI)
- **Cuándo se ejecuta:** Cada vez que se crea o actualiza un *Pull Request* hacia la rama `main`.
- **Flujo:** 
  1. GitHub Actions detecta el evento y ejecuta el archivo `.github/workflows/ci.yml`.
  2. Éste invoca el flujo de trabajo reutilizable `ci-python.yml` alojado en `xlmriosx/shared-library`.
  3. Prepara el entorno para **Python 3.12**.
  4. Ejecuta las pruebas automáticas utilizando `pytest` en la carpeta o módulo `test`.
  5. En caso de éxito o fallo, envía una notificación al equipo a través de **Discord**.

### 2. Despliegue Continuo (CD)
- **Cuándo se ejecuta:** Al fusionar (hacer *Merge*) o pushear directamente a la rama `main`.
- **Flujo:**
  1. Se ejecuta el archivo local `.github/workflows/cd.yml`.
  2. Llama al flujo reutilizable `AWS-Lambda-deploy.yml` de la librería compartida, con permisos para escribir *id-tokens* (`id-token: write`).
  3. **Autenticación AWS (OIDC):** Asume el rol de IAM correspondiente proporcionado a través de los secretos (`AWS_ROLE_ARN`).
  4. **Construcción y Push (ECR):** Construye la imagen Docker del proyecto y la sube (*push*) al repositorio privado de **Amazon ECR** denominado `argly-api`.
  5. **Despliegue (Lambda):** Actualiza el código de la función **AWS Lambda** llamada `argly-function` apuntando a la nueva imagen Docker subida.
  6. Envía notificaciones del resultado final a Discord.

## Detalles de la Infraestructura
A diferencia del repositorio web (estático), esta API se distribuye como un contenedor:
- **Almacenamiento de imagen:** `Amazon ECR` (Repositorio: `argly-api`).
- **Cómputo / Ejecución:** `AWS Lambda` (Función: `argly-function`) desplegada en la región `sa-east-1` (São Paulo).
