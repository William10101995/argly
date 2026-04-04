# Argly: datos públicos de Argentina siempre al día 🇦🇷

![ICL](https://github.com/William10101995/argly/actions/workflows/icl.yml/badge.svg)
![IPC](https://github.com/William10101995/argly/actions/workflows/ipc.yml/badge.svg)
![UVA](https://github.com/William10101995/argly/actions/workflows/uva.yml/badge.svg)
![CER](https://github.com/William10101995/argly/actions/workflows/cer.yml/badge.svg)
![UVI](https://github.com/William10101995/argly/actions/workflows/uvi.yml/badge.svg)
![ICC](https://github.com/William10101995/argly/actions/workflows/construccion.yml/badge.svg)
![RIOS](https://github.com/William10101995/argly/actions/workflows/rios.yml/badge.svg)
![Combustibles](https://github.com/William10101995/argly/actions/workflows/combustibles.yml/badge.svg)
[![Base URL API](https://img.shields.io/badge/website-online-brightgreen)](https://argly.com.ar)
![GitHub stars](https://img.shields.io/github/stars/William10101995/argly)

API pública que expone índices y precios de combustibles en Argentina a partir de fuentes públicas, con actualización automática y despliegue continuo.

El proyecto está pensado como **fuente de verdad basada en JSON**, con una API liviana en Flask, preparada para producción y consumo público.

## 🚀 Características

- 📊 **Combustibles**
  - Gasolineras por provincia
  - Gasolineras por empresa
  - Precio promedio por provincia y tipo de combustible

- 📈 **ICL (Índice de Contratos de Locación)**
  - Valor vigente del ICL
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

- 🌊 **Estado de los rios**
  - Nivel de los ríos en cada puerto
  - Nivel de un río específico

- 🧱 **ICC (Índice del Costo de la Construcción)**
  - Costo de la construcción en pesos y variaciones porcentuales vigentes

- 💳 **Scoring crediticio**
  - Evaluación de perfil crediticio a partir de los datos de la central de deudores del BCRA
  - Recomendación de préstamo máximo
  - Cuota estimada del nuevo préstamo
  - Plazo sugerido según perfil de riesgo

- 💊 **Medicamentos (Vademécum Nacional)**
  - Búsqueda de medicamentos por nombre
  - Información de presentación, laboratorio y tipo de venta
  - Precios ordenados de menor a mayor

- 🌎 **Censo Demográfico y Habitacional**
  - Provincias y municipios por provincia con sus respectivos centroides geográficos.
  - Datos de población y vivienda del **Último Censo Nacional (INDEC)** de cada municipio.

## 🌐 Endpoints disponibles

La API se encuentra disponible públicamente en: `https://api.argly.com.ar`

Todos los endpoints descriptos a continuación deben utilizar esta URL como base.

### 🔥 Combustibles

**Gasolineras por provincia**

```
GET /api/combustibles/provincia/<provincia>
```

**Gasolineras por empresa**

```
GET /api/combustibles/empresa/<empresa>
```

**Precio promedio por provincia y combustible**

```
GET /api/combustibles/promedio/<provincia>/<combustible>
```

---

### 📈 ICL

**Valor y fecha de publicación del ICL del día en curso**

```
GET /api/icl
```

**Historico del ICL**

```
GET /api/icl/history
```

**ICL en un rango de fechas**

```
GET /api/icl/range?desde=AAAA-MM-DD&hasta=AAAA-MM-DD
```

---

### 📉 IPC

**Datos completos del IPC**

```
GET /api/ipc
```

**Historico del IPC**

```
GET /api/ipc/history
```

**IPC en un rango de fechas**

```
GET /api/ipc/range?desde=AAAA-MM&hasta=AAAA-MM
```

### 🛒 Canasta Básica

**Último período publicado (CBA + CBT)**

```
GET /api/canasta
```

**Histórico completo**

```
GET /api/canasta/history
```

**Canasta en un rango de fechas**

```
GET /api/canasta/range?desde=AAAA-MM&hasta=AAAA-MM
```

### 🏠 UVI

**Valor y fecha de publicación de la UVI del día en curso**

```
GET /api/uvi
```

**Historico de la UVI**

```
GET /api/uvi/history
```

**UVI en un rango de fechas**

```
GET /api/uvi/range?desde=AAAA-MM-DD&hasta=AAAA-MM-DD
```

---

### 🏦 UVA

**Valor y fecha de publicación de la UVA del día en curso**

```
GET /api/uva
```

**Historico de la UVA**

```
GET /api/uva/history
```

**UVA en un rango de fechas**

```
GET /api/uva/range?desde=AAAA-MM-DD&hasta=AAAA-MM-DD
```

---

### 📉 CER

**Valor y fecha de publicación de la CER del día en curso**

```
GET /api/cer
```

**Historico de la CER**

```
GET /api/cer/history
```

**CER en un rango de fechas**

```
GET /api/cer/range?desde=AAAA-MM-DD&hasta=AAAA-MM-DD
```

---

### 🌊 Estado de los ríos

**Nivel de los ríos en cada puerto**

```
GET /api/rios
```

**Nivel de un río específico**

```
GET /api/rios/rio/<nombre_rio>
```

---

### 🧱 ICC

**Costo de la construcción en pesos y variaciones porcentuales del mes en curso**

```
GET /api/construccion
```

---

### 💳 Scoring crediticio

**Evaluación del perfil crediticio utilizando datos públicos del
Banco Central de la República Argentina.**

El modelo utiliza heurísticas financieras basadas en:

- situación crediticia
- cantidad de entidades acreedoras
- días de atraso
- flags legales
- ratio deuda/ingreso
- TEA personalizada

```
GET /api/credito/<cuil>/<salario_mensual>/<tea>
```

- El modelo de scoring crediticio es **heurístico** y está diseñado para evaluación preliminar de riesgo.
- No reemplaza modelos estadísticos o regulatorios utilizados por entidades financieras.

---

### 💊 Medicamentos

**Búsqueda de medicamentos en el vademécum nacional**

Permite buscar medicamentos por nombre y devuelve
los resultados ordenados por precio de menor a mayor.

```
GET /api/medicamentos/<medicamento>
```

---

### 🌎 Censo Demográfico y Habitacional

**Listado completo de provincias con municipios y datos censales**

Datos geográficos de provincias y municipios de Argentina, incluyendo información de población y vivienda del **Último Censo Nacional (INDEC)** por municipio.

```
GET /api/provincias
```

## 🔄 Actualización de datos

Los datos se mantienen actualizados mediante **GitHub Actions (cron jobs)**:

- 🛢️ Combustibles: cada **15 días**
- 📈 ICL: **todos los días a las 09:00, 10:00, 11:00 y 12:00**
- 📉 IPC: **día 10, 11, 12, 13 y 14 de cada mes**
- 🏠 UVI: **todos los días a las 09:00, 10:00 y 11:00**
- 🏦 UVA: **todos los días a las 09:00, 10:00 y 11:00**
- 📉 CER: **todos los días a las 09:00, 10:00 y 11:00**
- 🌊 Ríos: **todos los días a las 12:30**
- 🧱 ICC: **día 15, 16 y 17 de cada mes**
- 🛒 Canasta: **día 12, 13, 14 y 15 de cada mes**

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

## 🤝 Contribuidores

Gracias a todas las personas que aportan a este proyecto 💙

- [@dchaves80](https://github.com/dchaves80)

## ⭐ Contribuciones

Pull requests, sugerencias y mejoras son bienvenidas.
Este proyecto está pensado para crecer y ser útil a la comunidad.

## 📄 Licencia

MIT License
