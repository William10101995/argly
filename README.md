# Argly: datos públicos de Argentina siempre al día 🇦🇷

![ICL](https://github.com/William10101995/argly/actions/workflows/icl.yml/badge.svg)
![IPC](https://github.com/William10101995/argly/actions/workflows/ipc.yml/badge.svg)
![UVA](https://github.com/William10101995/argly/actions/workflows/uva.yml/badge.svg)
![UVI](https://github.com/William10101995/argly/actions/workflows/uvi.yml/badge.svg)
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

- 🏠 **UVI (Unidad de Vivienda)**
  - Valor vigente del UVI
  - Histórico
  - Histórico por rango de fechas

- 🏦 **UVA (Unidad de Valor Adquisitivo)**
  - Valor vigente del UVA
  - Histórico
  - Histórico por rango de fechas

- 🌊 **Estado de los rios**
  - Nivel de los ríos en cada puerto
  - Nivel de un río específico

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

### 🌊 Estado de los ríos

**Nivel de los ríos en cada puerto**

```
GET /api/rios
```

**Nivel de un río específico**

```
GET /api/rios/<nombre_rio>
```

## 🔄 Actualización de datos

Los datos se mantienen actualizados mediante **GitHub Actions (cron jobs)**:

- 🛢️ Combustibles: cada **15 días**
- 📈 ICL: **todos los días a las 09:00, 10:00, 11:00 y 12:00**
- 📉 IPC: **día 10, 11, 12, 13 y 14 de cada mes**
- 🏠 UVI: **todos los días a las 09:00, 10:00 y 11:00**
- 🏦 UVA: **todos los días a las 09:00, 10:00 y 11:00**
- 🌊 Ríos: **todos los días a las 09:30 y 12:30**

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
