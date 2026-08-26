from pathlib import Path
from datetime import date
import json
from datetime import datetime


def formatear_fecha_bcra(fecha_str):
    """Convierte fecha de YYYY-MM-DD a DD/MM/YYYY."""
    return datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y")


def save_dataset_json(dataset: str, data, versioned: bool = True):
    """
    Guarda data/<dataset>/latest.json
    y opcionalmente data/<dataset>/YYYY-MM-DD.json
    """

    base_dir = Path(__file__).resolve().parents[1]
    out_dir = base_dir / "data" / dataset
    out_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()

    if versioned:
        dated_file = out_dir / f"{today}.json"
        with dated_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    latest_file = out_dir / "latest.json"
    with latest_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"📁 Dataset '{dataset}' guardado en {out_dir}")


def upload_json_to_s3(dataset: str, data, key: str | None = None) -> None:
    """
    Sube el dataset directo a S3 (ademas de git). No falla el scraper si
    S3_DATA_BUCKET no esta configurado o si algo sale mal -- solo loguea.
    El scraper sigue commiteando a git igual que siempre (historico y
    auditoria); S3 es la fuente que lee el Lambda en runtime para este
    dataset puntual, para no tener que redesplegar la app cada vez que
    se actualiza (ver decision de arquitectura: dolares corre cada
    20 min y no puede disparar un deploy completo cada vez).

    El bucket argly-data vive en us-east-1 (confirmado con
    aws s3api get-bucket-location), no en sa-east-1 -- se fija la region
    explicita via S3_DATA_REGION para evitar un redirect extra.
    """
    import os
    import json as _json

    bucket = os.environ.get("S3_DATA_BUCKET")
    if not bucket:
        print("ℹ S3_DATA_BUCKET no configurado, se omite upload a S3")
        return

    region = os.environ.get("S3_DATA_REGION", "us-east-1")
    key = key or f"{dataset}/latest.json"

    try:
        import boto3

        s3 = boto3.client("s3", region_name=region)
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=_json.dumps(data, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
        )
        print(f"☁ Subido a s3://{bucket}/{key}")
    except Exception as e:
        # No bloqueante a proposito: si S3 falla, el commit a git ya se hizo
        # (o se hace despues igual) y el proximo ciclo del scraper reintenta.
        print(f"⚠ Error subiendo a S3 (no bloqueante): {e}")