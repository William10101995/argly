from api.utils.vademecum_client import buscar_medicamentos


def obtener_medicamentos(nombre):

    data = buscar_medicamentos(nombre)

    resultados = []

    for item in data:
        precio = item.get("PRECIO")

        try:
            precio = float(precio)
        except:
            precio = None

        resultados.append(
            {
                "nombre": item.get("NOMBRE"),
                "presentacion": item.get("PRESENTACION"),
                "laboratorio": item.get("LABORATORIO"),
                "precio": precio,
                "tipo_venta": item.get("TIPO_DE_VENTA"),
                "forma": item.get("FORMA"),
                "via": item.get("VIA"),
                "accion": item.get("ACCION"),
                "droga": item.get("DROGA"),
                "fecha_actualizacion": item.get("FECHA"),
            }
        )

    # ordenar de menor a mayor
    resultados = sorted(
        resultados,
        key=lambda x: x["precio"] if x["precio"] is not None else float("inf"),
    )

    # tomar los primeros 10
    # resultados = resultados[:200]

    return {"query": nombre, "total": len(resultados), "results": resultados}
