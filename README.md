<div align="center">

# Argly: datos públicos de Argentina siempre al día 🇦🇷

<a href="https://github.com/sponsors/William10101995">
  <img src="https://img.shields.io/badge/Sponsor_via_GitHub-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white" alt="Sponsor en GitHub" />
</a>
<a href="https://cafecito.app/williamjuanjoselopez">
  <img src="https://img.shields.io/badge/Invitame_un_café-FFC000?style=for-the-badge&logo=buymeacoffee&logoColor=black" alt="Invitame un café en Cafecito" />
</a>

<br><br>

<img src="https://github.com/William10101995/argly/actions/workflows/icl.yml/badge.svg" alt="ICL">
<img src="https://github.com/William10101995/argly/actions/workflows/ipc.yml/badge.svg" alt="IPC">
<img src="https://github.com/William10101995/argly/actions/workflows/uva.yml/badge.svg" alt="UVA">
<img src="https://github.com/William10101995/argly/actions/workflows/cer.yml/badge.svg" alt="CER">
<img src="https://github.com/William10101995/argly/actions/workflows/uvi.yml/badge.svg" alt="UVI">
<img src="https://github.com/William10101995/argly/actions/workflows/construccion.yml/badge.svg" alt="ICC">
<img src="https://github.com/William10101995/argly/actions/workflows/smvm.yml/badge.svg" alt="SMVM">
<img src="https://github.com/William10101995/argly/actions/workflows/rios.yml/badge.svg" alt="RIOS">
<img src="https://github.com/William10101995/argly/actions/workflows/combustibles.yml/badge.svg" alt="Combustibles">
<img src="https://github.com/William10101995/argly/actions/workflows/canasta.yml/badge.svg" alt="CBA y CBT">
<img src="https://github.com/William10101995/argly/actions/workflows/personas.yml/badge.svg" alt="Desaparecidos">

<br>

<a href="https://argly.com.ar">
  <img src="https://img.shields.io/badge/website-online-brightgreen" alt="Base URL API">
</a>
<img src="https://img.shields.io/github/stars/William10101995/argly" alt="GitHub stars">

</div>

API pública que expone índices y precios de combustibles en Argentina a partir de fuentes públicas, con actualización automática y despliegue continuo.

El proyecto está pensado como **fuente de verdad basada en JSON**, con una API liviana en Flask, preparada para producción y consumo público.

## 🚀 Características

- 📊 **Combustibles**
  - Gasolineras por provincia
  - Gasolineras por empresa
  - Precio promedio por provincia y tipo de combustible

- 📈 **ICL (Índice de Contratos de Locación)**
  - Valor vigente del ICL
  - Proyección de los próximos 15 días
  - Histórico
  - Histórico por rango de fechas

- 📉 **IPC (Índice de Precios al Consumidor)**
  - Valor vigente del IPC
  - Histórico
  - Histórico por rango de fechas

* 🛒 **Canasta Básica (CBA y CBT)**
  - Último período publicado completo
  - Histórico completo
  - Histórico por rango de fechas

- 🏠 **UVI (Unidad de Vivienda)**
  - Valor vigente del UVI
  - Histórico
  - Histórico por rango de fechas

- 🏦 **UVA (Unidad de Valor Adquisitivo)**
  - Valor vigente del UVA
  - Histórico
  - Histórico por rango de fechas

- 📉 **CER (Coeficiente de Estabilización de Referencia)**
  - Valor vigente del CER
  - Histórico
  - Histórico por rango de fechas

- ⚠️ **Riesgo País**
  - Valor vigente del Riesgo País
  - Valor del día anterior
  - Histórico por rango de fechas

- 💼 **SMVM (Salario Mínimo, Vital y Móvil)**
  - Valor vigente del SMVM
  - Histórico
  - Histórico por rango de fechas

- 🌊 **Estado de los rios**
  - Nivel de los ríos en cada puerto
  - Nivel de un río específico

- 🧱 **ICC (Índice del Costo de la Construcción)**
  - Costo de la construcción en pesos y variaciones porcentuales vigentes

- 💊 **Medicamentos (Vademécum Nacional)**
  - Búsqueda de medicamentos por nombre
  - Información de presentación, laboratorio y tipo de venta
  - Precios ordenados de menor a mayor

- 🌎 **Censo Demográfico y Habitacional**
  - Provincias y municipios por provincia con sus respectivos centroides geográficos.
  - Datos de población y vivienda del **Último Censo Nacional (INDEC)** de cada municipio.

- 👤 **Personas Desaparecidas y Extraviadas (SIFEBU)**
  - Listado completo de personas desaparecidas y extraviadas de Argentina, con información detallada de cada caso.

- 🗳️ **Diputados**
  - Listado completo de los Diputados Nacionales actuales.
  - Diputados por distrito.
  - Diputados por bloque.

## 🌐 Endpoints disponibles

La API se encuentra disponible públicamente en: `https://api.argly.com.ar`

Todos los endpoints descriptos a continuación deben utilizar esta URL como base.

### 🔥 Combustibles

**Gasolineras por provincia**

```
GET /v1/combustibles?provincia=<provincia>
```

**Gasolineras por empresa**

```
GET /v1/combustibles?empresa=<empresa>
```

**Precio promedio por provincia y combustible**

```
GET /v1/combustibles/promedio?provincia=<provincia>&combustible<combustible>
```

---

### 📈 ICL

**Valor y fecha de publicación del ICL del día en curso**

```
GET /v1/icl
```

**Proyección del ICL a 15 días (adelanto publicado por el BCRA)**

```
GET /v1/icl/adelanto
```

**Historico del ICL**

```
GET /v1/icl?historico=true
```

**ICL en un rango de fechas**

```
GET /v1/icl?desde=AAAA-MM-DD&hasta=AAAA-MM-DD
```

---

### 📉 IPC

**Datos completos del IPC**

```
GET /v1/ipc
```

**Historico del IPC**

```
GET /v1/ipc?historico=true
```

**IPC en un rango de fechas**

```
GET /v1/ipc?desde=AAAA-MM&hasta=AAAA-MM
```

### 🛒 Canasta Básica

**Último período publicado (CBA + CBT)**

```
GET /v1/canasta
```

**Histórico completo**

```
GET /v1/canasta?historico=true
```

**Canasta en un rango de fechas**

```
GET /v1/canasta?desde=AAAA-MM&hasta=AAAA-MM
```

### 🏠 UVI

**Valor y fecha de publicación de la UVI del día en curso**

```
GET /v1/uvi
```

**Historico de la UVI**

```
GET /v1/uvi?historico=true
```

**UVI en un rango de fechas**

```
GET /v1/uvi?desde=AAAA-MM-DD&hasta=AAAA-MM-DD
```

---

### 🏦 UVA

**Valor y fecha de publicación de la UVA del día en curso**

```
GET /v1/uva
```

**Historico de la UVA**

```
GET /v1/uva?historico=true
```

**UVA en un rango de fechas**

```
GET /v1/uva?desde=AAAA-MM-DD&hasta=AAAA-MM-DD
```

---

### 📉 CER

**Valor y fecha de publicación de la CER del día en curso**

```
GET /v1/cer
```

**Historico de la CER**

```
GET /v1/cer?historico=true
```

**CER en un rango de fechas**

```
GET /v1/cer?desde=AAAA-MM-DD&hasta=AAAA-MM-DD
```

---

### ⚠️ Riesgo País

**Valor del Riesgo País del día en curso**

```
GET /v1/riesgo-pais
```

**Valor del Riesgo País del día anterior**

```
GET /v1/riesgo-pais?anterior=true
```

**Valor del Riesgo País en un rango de fecha**

```
GET /v1/riesgo-pais?desde=AAAA-MM-DD&hasta=AAAA-MM-DD
```

---

### 💼 SMVM

**Valor y fecha de publicación del SMVM del día en curso**

```
GET /v1/smvm
```

**Historico del SMVM**

```
GET /v1/smvm?historico=true
```

**SMVM en un rango de fechas**

```
GET /v1/smvm?desde=AAAA-MM-DD&hasta=AAAA-MM-DD
```

---

### 🌊 Estado de los ríos

**Nivel de los ríos en cada puerto**

```
GET /v1/rios
```

**Nivel de un río específico**

```
GET /v1/rios?nombre=<nombre_rio>
```

---

### 🧱 ICC

**Costo de la construcción en pesos y variaciones porcentuales del mes en curso**

```
GET /v1/construccion
```

---

### 💊 Medicamentos

**Búsqueda de medicamentos en el vademécum nacional**

Permite buscar medicamentos por nombre y devuelve
los resultados ordenados por precio de menor a mayor.

```
GET /v1/medicamentos?nombre=<nombre_medicamento>
```

---

### 🌎 Censo Demográfico y Habitacional

**Listado completo de provincias con municipios y datos censales**

Datos geográficos de provincias y municipios de Argentina, incluyendo información de población y vivienda del **Último Censo Nacional (INDEC)** por municipio.

```
GET /v1/provincias
```

### 👤 Personas Desaparecidas y Extraviadas (SIFEBU)

**Listado completo de personas desaparecidas y extraviadas de Argentina**

Datos detallados de todas las personas desaparecidas y/o extraviadas de argentina, incluyendo nombre y apellido, fecha de desaparición, descripción y si se ofrece recompensa o no. Datos obtenidos del **SIFEBU (Sistema Federal de Busqueda de Personas Desaparecidas y Extraviadas).**

```
GET /v1/personas-desaparecidas
```

**Listado de personas desaparecidas y extraviadas por año**

```
GET /v1/personas-desaparecidas?anio=AAAA
```

---

### 🗳️ Diputados Nacionales

**Listado completo de los Diputados Nacionales actuales**

```
GET /v1/diputados
```

**Listado de Diputados por distrito**

```
GET /v1/diputados?distrito=<distrito>
```

**Listado de Diputados por bloque**

```
GET /v1/diputados?bloque=<bloque>
```

## 🔄 Actualización de datos

Los datos se mantienen actualizados mediante **GitHub Actions (cron jobs)**:

- 🛢️ Combustibles: cada **15 días**
- 📈 ICL: **todos los días a las 09:00, 10:00, 11:00 y 12:00**
- 📉 IPC: **día 10, 11, 12, 13 y 14 de cada mes**
- 🏠 UVI: **todos los días a las 09:00, 10:00 y 11:00**
- 🏦 UVA: **todos los días a las 09:00, 10:00 y 11:00**
- 📉 CER: **todos los días a las 09:00, 10:00 y 11:00**
- ⚠️ Riesgo País: **en sincronia con ambito.com**
- 💼 SMVM: **el día 5 de cada mes**
- 🌊 Ríos: **todos los días a las 12:30**
- 🧱 ICC: **día 15, 16 y 17 de cada mes**
- 🛒 Canasta: **día 12, 13, 14 y 15 de cada mes**
- 👤 Personas desaparecidas: **día 12 de cada mes.**

## 🧪 Desarrollo local

### 1️⃣ Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate
```

### 2️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3️⃣ Levantar la API

```bash
python -m flask run
```

La API quedará disponible en:

```
http://localhost:5000
```

## ⚠️ Consideraciones

- Los datos se exponen tal como fueron recolectados.
- No se garantiza exactitud legal o comercial.
- Uso bajo responsabilidad del consumidor.

## 📚 Documentación

Diagramas de arquitectura y flujos del sistema:

| Documento                                     | Descripción                                  |
| --------------------------------------------- | -------------------------------------------- |
| [Arquitectura General](docs/arquitectura.md)  | Vista completa del sistema y sus componentes |
| [Pipeline CI/CD](docs/ci-cd.md)               | Flujo de integración y despliegue continuo   |
| [Flujo de API](docs/api-flow.md)              | Cómo se procesan las peticiones HTTP         |
| [Flujo de Scraping](docs/scraping.md)         | Proceso de recolección de datos              |
| [Estructura de Datos](docs/data-structure.md) | Estructura de los JSONs y archivos           |

## 👤 Autor

Proyecto desarrollado y mantenido por **William López**.

## 🤝 Colaboradores

¡Un enorme agradecimiento a las personas que aportan su tiempo y conocimiento para que este proyecto siga creciendo! 💙

<a href="https://github.com/William10101995/argly/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=William10101995/argly" alt="Colaboradores de Argly" />
</a>

## ⭐ Contribuciones

Pull requests, sugerencias y mejoras son bienvenidas.
Este proyecto está pensado para crecer y ser útil a la comunidad.

## 📄 Licencia

MIT License
