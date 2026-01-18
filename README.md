# Argly: datos públicos de Argentina, simples y accesibles 🇦🇷

![ICL](https://github.com/William10101995/datos-argentina-api/actions/workflows/icl.yml/badge.svg)
![IPC](https://github.com/William10101995/datos-argentina-api/actions/workflows/ipc.yml/badge.svg)
![Combustibles](https://github.com/William10101995/datos-argentina-api/actions/workflows/combustibles.yml/badge.svg)
[![Base URL API](https://img.shields.io/badge/website-online-brightgreen)](https://argly.com.ar)

API pública que expone índices y precios de combustibles en Argentina a partir de fuentes públicas, con actualización automática y despliegue continuo.

El proyecto está pensado como **fuente de verdad basada en JSON**, con una API liviana en Flask, preparada para producción y consumo público.

## 🚀 Características

- 📊 **Combustibles**
  - Gasolineras por provincia
  - Gasolineras por empresa
  - Precio promedio por provincia y tipo de combustible

- 📈 **ICL (Índice de Contratos de Locación)**
  - Fecha de publicación
  - Valor vigente del ICL

- 📉 **IPC (Índice de Precios al Consumidor)**
  - Valor vigente del IPC
  - Mes
  - Año
  - Fecha de publicación
  - Fecha de próxima publicación

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

**Valor y fecha de publicación**

```
GET /api/icl
```

---

### 📉 IPC

**Datos completos del IPC**

```
GET /api/ipc
```

---

## 🔄 Actualización de datos

Los datos se mantienen actualizados mediante **GitHub Actions (cron jobs)**:

- 🛢️ Combustibles: cada **15 días**
- 📈 ICL: **todos los días a las 09:00, 10:00, 11:00 y 12:00**
- 📉 IPC: **día 10, 11, 12, 13 y 14 de cada mes**

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

## 📄 Licencia

MIT License

## 👤 Autor

Proyecto desarrollado y mantenido por **William López**.

## ⭐ Contribuciones

Pull requests, sugerencias y mejoras son bienvenidas.
Este proyecto está pensado para crecer y ser útil a la comunidad.
