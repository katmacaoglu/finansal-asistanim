#!/usr/bin/env python3
"""Finansal Asistanım kurulum script'i.

Kullanıcıya özel ayarları üretir. Bu dosyalar .gitignore'dadır, repoya girmez:
  - veri/ayarlar.json            : kaynak klasör yolu ve tercihler
  - .claude/settings.local.json  : kaynak klasörü salt okunur yapan izinler
  - veri/profil.md               : profil şablonunun kişisel kopyası

Kullanım:
  python3 kurulum.py                          # etkileşimli
  python3 kurulum.py --kaynak "/yol/Finans"   # etkileşimsiz
  python3 kurulum.py --kontrol                # mevcut kurulumu kontrol et
"""
import argparse
import json
import platform
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

KOK = Path(__file__).resolve().parent
AYARLAR = KOK / "veri" / "ayarlar.json"
LOCAL_SETTINGS = KOK / ".claude" / "settings.local.json"
PROFIL = KOK / "veri" / "profil.md"
PROFIL_ORNEK = KOK / "veri" / "profil.ornek.md"
VARSAYILAN_KAYNAK = KOK / "veri" / "kaynak"


def drive_onerileri():
    ev = Path.home()
    adaylar = [
        ev / "Google Drive" / "My Drive",
        ev / "Google Drive",
        ev / "Library" / "CloudStorage",  # macOS: GoogleDrive-<e-posta>/My Drive
        Path("G:/My Drive"),
        Path("G:/Drive'ım"),
    ]
    bulunan = []
    for a in adaylar:
        if a.name == "CloudStorage" and a.exists():
            bulunan += [p / "My Drive" for p in a.glob("GoogleDrive-*") if (p / "My Drive").exists()]
        elif a.exists():
            bulunan.append(a)
    return bulunan


def izin_yolu(p: Path) -> str:
    """Claude Code izin sözdizimi: mutlak yol '//' ile başlar."""
    s = p.resolve().as_posix()
    if len(s) > 1 and s[1] == ":":  # Windows: C:/... -> //c/...
        s = "/" + s[0].lower() + s[2:]
    return "/" + s if s.startswith("/") else "//" + s


def kaynak_sor() -> Path:
    print("\nFinansal belgelerinizin (tablo, ekstre, not) bulunduğu klasör hangisi?")
    oneriler = drive_onerileri()
    if oneriler:
        print("Bulunan Google Drive konumları:")
        for i, o in enumerate(oneriler, 1):
            print(f"  {i}) {o}")
    print(f"Boş bırakırsanız proje içindeki klasör kullanılır: {VARSAYILAN_KAYNAK}")
    cevap = input("Klasör yolu (veya numara): ").strip().strip('"')
    if not cevap:
        return VARSAYILAN_KAYNAK
    if cevap.isdigit() and 1 <= int(cevap) <= len(oneriler):
        alt = input(f"{oneriler[int(cevap) - 1]} altındaki finans klasörünün adı (örn. Finans): ").strip()
        return oneriler[int(cevap) - 1] / alt if alt else oneriler[int(cevap) - 1]
    return Path(cevap).expanduser()


def kur(kaynak: Path, para_birimi: str):
    kaynak = kaynak.expanduser().resolve()
    if not kaynak.exists():
        sys.exit(f"HATA: Klasör bulunamadı: {kaynak}")

    AYARLAR.write_text(json.dumps({
        "surum": "0.1.0",
        "kaynak_klasor": str(kaynak),
        "kaynak_proje_ici": kaynak == VARSAYILAN_KAYNAK.resolve(),
        "para_birimi": para_birimi,
        "isletim_sistemi": platform.system(),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    yol = izin_yolu(kaynak)
    LOCAL_SETTINGS.write_text(json.dumps({
        "permissions": {
            "allow": [f"Read({yol}/**)"],
            "deny": [f"Edit({yol}/**)", f"Write({yol}/**)"],
        }
    }, indent=2), encoding="utf-8")

    if not PROFIL.exists():
        shutil.copy(PROFIL_ORNEK, PROFIL)
        profil_mesaj = "oluşturuldu (doldurmak için Claude Code içinde /kurulum çalıştırın)"
    else:
        profil_mesaj = "zaten var, dokunulmadı"

    print("\nKurulum tamam.")
    print(f"  Kaynak klasör : {kaynak} (salt okunur)")
    print(f"  Ayarlar       : {AYARLAR.relative_to(KOK)}")
    print(f"  İzinler       : {LOCAL_SETTINGS.relative_to(KOK)}")
    print(f"  Profil        : veri/profil.md {profil_mesaj}")


def kontrol():
    sorunlar = []
    if not AYARLAR.exists():
        sorunlar.append("veri/ayarlar.json yok → python3 kurulum.py çalıştırın")
    else:
        a = json.loads(AYARLAR.read_text(encoding="utf-8"))
        if not Path(a["kaynak_klasor"]).exists():
            sorunlar.append(f"Kaynak klasör erişilemiyor: {a['kaynak_klasor']}")
    if not LOCAL_SETTINGS.exists():
        sorunlar.append(".claude/settings.local.json yok → python3 kurulum.py çalıştırın")
    if not PROFIL.exists():
        sorunlar.append("veri/profil.md yok → python3 kurulum.py çalıştırın")
    elif PROFIL.read_text(encoding="utf-8") == PROFIL_ORNEK.read_text(encoding="utf-8"):
        sorunlar.append("veri/profil.md henüz doldurulmamış → Claude Code içinde /kurulum")
    try:
        import pandas, openpyxl  # noqa: F401
    except ImportError:
        sorunlar.append("Excel okumak için: pip install pandas openpyxl (opsiyonel)")
    if sorunlar:
        print("Eksikler:")
        print("\n".join(f"  - {s}" for s in sorunlar))
        sys.exit(1)
    print("Kurulum eksiksiz.")


def main():
    ap = argparse.ArgumentParser(description="Finansal Asistanım kurulumu")
    ap.add_argument("--kaynak", help="Finansal belgelerin bulunduğu klasör")
    ap.add_argument("--para-birimi", default="TRY")
    ap.add_argument("--kontrol", action="store_true", help="Mevcut kurulumu kontrol et")
    a = ap.parse_args()
    if a.kontrol:
        return kontrol()
    kur(Path(a.kaynak) if a.kaynak else kaynak_sor(), a.para_birimi)


if __name__ == "__main__":
    main()
