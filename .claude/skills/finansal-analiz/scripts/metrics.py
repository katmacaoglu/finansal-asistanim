#!/usr/bin/env python3
"""Kişisel finans metriklerini deterministik olarak hesaplar.

Kullanım:
  metrics.py <snapshot.json> --piyasa <piyasa.json> [--onceki <onceki.json>] [--ekstra-oran 0.5]

Çıktı: stdout'a JSON. LLM bu çıktıyı yorumlar, rakamları kendisi hesaplamaz.
"""
import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def yukle(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def piyasa_degeri(piyasa, anahtar):
    v = (piyasa or {}).get("degerler", {}).get(anahtar)
    return v.get("deger") if isinstance(v, dict) else v


def kur_tablosu(piyasa):
    kurlar = {"TRY": 1.0,
              "USD": piyasa_degeri(piyasa, "usd_try"),
              "EUR": piyasa_degeri(piyasa, "eur_try"),
              "XAU_GRAM": piyasa_degeri(piyasa, "gram_altin_try")}
    return kurlar


def try_karsiligi(tutar, pb, kurlar, eksik_kurlar):
    kur = kurlar.get(pb)
    if kur is None:
        eksik_kurlar.add(pb)
        return 0.0
    return tutar * kur


def ozet(snap, kurlar):
    eksik = set()
    varliklar = [(v, try_karsiligi(v["tutar"], v["para_birimi"], kurlar, eksik)) for v in snap["varliklar"]]
    borclar = [(b, try_karsiligi(b["kalan_anapara"], b["para_birimi"], kurlar, eksik)) for b in snap["borclar"]]

    toplam_varlik = sum(t for _, t in varliklar)
    likit = sum(t for v, t in varliklar if v["likit"])
    toplam_borc = sum(t for _, t in borclar)
    gelir = sum(g["tutar"] for g in snap["aylik_nakit_akisi"]["gelirler"])
    gider = sum(g["tutar"] for g in snap["aylik_nakit_akisi"]["giderler"])
    borc_odemeleri = sum(try_karsiligi(b["aylik_odeme"], b["para_birimi"], kurlar, eksik) for b in snap["borclar"])
    serbest = gelir - gider - borc_odemeleri
    aylik_cikis = gider + borc_odemeleri

    dagilim = {}
    for v, t in varliklar:
        dagilim[v["tur"]] = dagilim.get(v["tur"], 0) + t

    return {
        "toplam_varlik_try": round(toplam_varlik, 2),
        "likit_varlik_try": round(likit, 2),
        "toplam_borc_try": round(toplam_borc, 2),
        "net_deger_try": round(toplam_varlik - toplam_borc, 2),
        "aylik_gelir": round(gelir, 2),
        "aylik_gider_borc_haric": round(gider, 2),
        "aylik_borc_odemeleri": round(borc_odemeleri, 2),
        "aylik_serbest_nakit": round(serbest, 2),
        "acil_durum_fonu_ay": round(likit / aylik_cikis, 1) if aylik_cikis else None,
        "borc_odeme_gelir_orani_%": round(100 * borc_odemeleri / gelir, 1) if gelir else None,
        "borc_varlik_orani_%": round(100 * toplam_borc / toplam_varlik, 1) if toplam_varlik else None,
        "varlik_dagilimi_%": {k: round(100 * t / toplam_varlik, 1) for k, t in sorted(dagilim.items(), key=lambda x: -x[1])} if toplam_varlik else {},
        "eksik_kurlar": sorted(eksik),
    }


def borc_detay(snap, kurlar, tufe_yillik):
    sonuc = []
    for b in snap["borclar"]:
        m = b.get("aylik_faiz_orani")
        kalan = try_karsiligi(b["kalan_anapara"], b["para_birimi"], kurlar, set())
        satir = {"ad": b["ad"], "tur": b["tur"], "kalan_try": round(kalan, 2), "aylik_faiz_%": m}
        if m is not None:
            yillik_bilesik = ((1 + m / 100) ** 12 - 1) * 100
            satir["yillik_bilesik_faiz_%"] = round(yillik_bilesik, 1)
            satir["bu_ayki_faiz_maliyeti_try"] = round(kalan * m / 100, 2)
            if tufe_yillik is not None:
                satir["reel_faiz_%"] = round(((1 + yillik_bilesik / 100) / (1 + tufe_yillik / 100) - 1) * 100, 1)
        sonuc.append(satir)
    return sorted(sonuc, key=lambda x: -(x["aylik_faiz_%"] or 0))


def simule(borclar, ekstra, siralama, max_ay=600):
    """Her ay: faiz eklenir, asgari ödemeler yapılır, ekstra + serbest kalan ödemeler hedef borca gider."""
    bakiyeler = [dict(ad=b["ad"], bakiye=b["kalan"], r=(b["faiz"] or 0) / 100, asgari=b["odeme"]) for b in borclar]
    if siralama == "cig_topu":
        sira = sorted(range(len(bakiyeler)), key=lambda i: bakiyeler[i]["bakiye"])
    else:  # cig = en yüksek faiz önce
        sira = sorted(range(len(bakiyeler)), key=lambda i: -bakiyeler[i]["r"])
    butce = sum(b["asgari"] for b in bakiyeler) + ekstra
    toplam_faiz, kapanis = 0.0, {}
    for ay in range(1, max_ay + 1):
        for b in bakiyeler:
            if b["bakiye"] > 0:
                f = b["bakiye"] * b["r"]
                b["bakiye"] += f
                toplam_faiz += f
        kalan_butce = butce
        for b in bakiyeler:
            if b["bakiye"] > 0:
                p = min(b["asgari"], b["bakiye"], kalan_butce)
                b["bakiye"] -= p
                kalan_butce -= p
        for i in sira:
            b = bakiyeler[i]
            if b["bakiye"] > 0 and kalan_butce > 0:
                p = min(b["bakiye"], kalan_butce)
                b["bakiye"] -= p
                kalan_butce -= p
        for b in bakiyeler:
            if b["bakiye"] <= 0.01 and b["ad"] not in kapanis:
                kapanis[b["ad"]] = ay
        if len(kapanis) == len(bakiyeler):
            return {"toplam_ay": ay, "toplam_faiz_try": round(toplam_faiz, 2), "kapanis_ayi": kapanis}
    return {"toplam_ay": None, "toplam_faiz_try": round(toplam_faiz, 2), "kapanis_ayi": kapanis,
            "not": f"{max_ay} ayda kapanmıyor; ödemeler faizi karşılamıyor olabilir"}


def borc_plani(snap, kurlar, serbest, ekstra_oran):
    borclar = [dict(ad=b["ad"],
                    kalan=try_karsiligi(b["kalan_anapara"], b["para_birimi"], kurlar, set()),
                    faiz=b.get("aylik_faiz_orani"),
                    odeme=try_karsiligi(b["aylik_odeme"], b["para_birimi"], kurlar, set()))
               for b in snap["borclar"] if b["kalan_anapara"] > 0]
    if not borclar:
        return None
    ekstra = max(0.0, serbest) * ekstra_oran
    return {
        "ekstra_aylik_odeme_try": round(ekstra, 2),
        "varsayim": (f"Serbest nakdin %{int(ekstra_oran * 100)}'i borca ayrılıyor; faiz oranları sabit; "
                     "toplam aylık borç bütçesi sabit kalır, kapanan borcun ödemesi sıradaki borca aktarılır"),
        "sadece_mevcut_odemeler": simule(borclar, 0, "cig"),
        "cig_yontemi_yuksek_faiz_once": simule(borclar, ekstra, "cig"),
        "kartopu_yontemi_kucuk_bakiye_once": simule(borclar, ekstra, "cig_topu"),
    }


def karsilastir(simdi, onceki_ozet):
    alanlar = ["net_deger_try", "toplam_borc_try", "likit_varlik_try", "aylik_serbest_nakit", "acil_durum_fonu_ay"]
    return {a: {"onceki": onceki_ozet.get(a), "simdi": simdi.get(a),
                "degisim": round(simdi[a] - onceki_ozet[a], 2) if simdi.get(a) is not None and onceki_ozet.get(a) is not None else None}
            for a in alanlar}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("snapshot")
    ap.add_argument("--piyasa")
    ap.add_argument("--onceki")
    ap.add_argument("--ekstra-oran", type=float, default=0.5)
    a = ap.parse_args()

    snap = yukle(a.snapshot)
    piyasa = yukle(a.piyasa) if a.piyasa else None
    kurlar = kur_tablosu(piyasa)
    tufe = piyasa_degeri(piyasa, "tufe_yillik")

    oz = ozet(snap, kurlar)
    cikti = {
        "tarih": snap["tarih"],
        "ozet": oz,
        "borclar_faize_gore": borc_detay(snap, kurlar, tufe),
        "borc_kapatma_senaryolari": borc_plani(snap, kurlar, oz["aylik_serbest_nakit"], a.ekstra_oran),
        "piyasa_referans": {k: piyasa_degeri(piyasa, k) for k in
                            ["tcmb_politika_faizi", "tufe_yillik", "ortalama_mevduat_faizi_32_gun",
                             "kredi_karti_azami_akdi_faiz"]} if piyasa else None,
        "uyarilar": snap.get("uyarilar", []),
        "eksikler": snap.get("eksikler", []),
    }
    if a.onceki:
        onceki = yukle(a.onceki)
        cikti["onceki_doneme_gore"] = karsilastir(oz, ozet(onceki, kurlar))
        cikti["onceki_doneme_gore"]["not"] = f"Önceki: {onceki['tarih']}; her iki dönem güncel kurla çevrildi"
    print(json.dumps(cikti, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
