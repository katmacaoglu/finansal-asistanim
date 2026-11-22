#!/usr/bin/env python3
"""Snapshot JSON dosyasını şemaya göre doğrular. Sadece standart kütüphane kullanır."""
import json
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCHEMA = json.loads((Path(__file__).parent.parent / "schema.json").read_text(encoding="utf-8"))


def check(obj, schema, path, errors):
    if "enum" in schema:
        if obj not in schema["enum"]:
            errors.append(f"{path}: '{obj}' izinli değil {schema['enum']}")
        return
    types = schema.get("type")
    if types:
        types = types if isinstance(types, list) else [types]
        py = {"object": dict, "array": list, "string": str, "boolean": bool,
              "integer": int, "number": (int, float), "null": type(None)}
        ok = any(isinstance(obj, py[t]) and not (t in ("number", "integer") and isinstance(obj, bool))
                 for t in types)
        if not ok:
            errors.append(f"{path}: tip {types} bekleniyordu, {type(obj).__name__} geldi")
            return
    if isinstance(obj, dict):
        for req in schema.get("required", []):
            if req not in obj:
                errors.append(f"{path}: zorunlu alan eksik '{req}'")
        for key, sub in schema.get("properties", {}).items():
            if key in obj:
                check(obj[key], sub, f"{path}.{key}", errors)
    if isinstance(obj, list) and "items" in schema:
        for i, item in enumerate(obj):
            check(item, schema["items"], f"{path}[{i}]", errors)


def main():
    if len(sys.argv) != 2:
        sys.exit("Kullanım: validate.py <snapshot.json>")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    errors = []
    check(data, SCHEMA, "$", errors)
    try:
        date.fromisoformat(data.get("tarih", ""))
    except ValueError:
        errors.append("$.tarih: YYYY-MM-DD formatında olmalı")
    for i, b in enumerate(data.get("borclar", [])):
        if b.get("aylik_faiz_orani") is not None and b["aylik_faiz_orani"] > 20:
            errors.append(f"$.borclar[{i}]: aylık faiz %{b['aylik_faiz_orani']} çok yüksek, yıllık mı girildi?")
    if errors:
        print("GEÇERSİZ")
        print("\n".join(f"- {e}" for e in errors))
        sys.exit(1)
    print(f"GEÇERLİ: {len(data['varliklar'])} varlık, {len(data['borclar'])} borç")


if __name__ == "__main__":
    main()
