"""Hesap motoru ve şema doğrulayıcı için temel testler.

Çalıştırma: python3 -m unittest discover tests
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / ".claude" / "skills" / "finansal-analiz" / "scripts"))
import metrics  # noqa: E402

SNAP = KOK / "veri" / "ornek" / "snapshot-ornek.json"
PIYASA = KOK / "veri" / "ornek" / "piyasa-ornek.json"
VALIDATE = KOK / ".claude" / "skills" / "finansal-snapshot" / "scripts" / "validate.py"


class MetrikTestleri(unittest.TestCase):
    def setUp(self):
        self.snap = metrics.yukle(SNAP)
        self.kurlar = metrics.kur_tablosu(metrics.yukle(PIYASA))

    def test_ozet_rakamlari(self):
        oz = metrics.ozet(self.snap, self.kurlar)
        # 45.000 + 150.000 + 2.000*42 + 50*5.500
        self.assertEqual(oz["toplam_varlik_try"], 554000.0)
        self.assertEqual(oz["toplam_borc_try"], 287000.0)
        self.assertEqual(oz["net_deger_try"], 267000.0)
        self.assertEqual(oz["aylik_serbest_nakit"], 23100.0)
        self.assertEqual(oz["eksik_kurlar"], [])

    def test_eksik_kur_raporlanir(self):
        oz = metrics.ozet(self.snap, {"TRY": 1.0, "USD": None, "EUR": None, "XAU_GRAM": None})
        self.assertIn("USD", oz["eksik_kurlar"])
        self.assertIn("XAU_GRAM", oz["eksik_kurlar"])

    def test_yillik_bilesik_faiz(self):
        borclar = metrics.borc_detay(self.snap, self.kurlar, 30.0)
        kart = borclar[0]
        self.assertEqual(kart["aylik_faiz_%"], 3.75)
        self.assertAlmostEqual(kart["yillik_bilesik_faiz_%"], 55.5, places=1)

    def test_ekstra_odeme_faizi_azaltir(self):
        plan = metrics.borc_plani(self.snap, self.kurlar, 23100.0, 0.5)
        temel = plan["sadece_mevcut_odemeler"]["toplam_faiz_try"]
        cig = plan["cig_yontemi_yuksek_faiz_once"]["toplam_faiz_try"]
        self.assertLess(cig, temel)

    def test_cig_kartopundan_pahali_olamaz(self):
        plan = metrics.borc_plani(self.snap, self.kurlar, 23100.0, 0.5)
        self.assertLessEqual(plan["cig_yontemi_yuksek_faiz_once"]["toplam_faiz_try"],
                             plan["kartopu_yontemi_kucuk_bakiye_once"]["toplam_faiz_try"] + 0.01)

    def test_kapanmayan_borc_tespit_edilir(self):
        borc = [dict(ad="X", kalan=100000, faiz=5.0, odeme=1000)]  # faiz 5.000 > ödeme
        sonuc = metrics.simule(borc, 0, "cig", max_ay=24)
        self.assertIsNone(sonuc["toplam_ay"])


class DogrulamaTestleri(unittest.TestCase):
    def calistir(self, veri, tmp_ad):
        yol = KOK / "tests" / tmp_ad
        yol.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
        try:
            return subprocess.run([sys.executable, str(VALIDATE), str(yol)], capture_output=True, text=True, encoding="utf-8")
        finally:
            yol.unlink()

    def test_ornek_gecerli(self):
        r = subprocess.run([sys.executable, str(VALIDATE), str(SNAP)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_yillik_faiz_aylik_alana_girilirse_yakalanir(self):
        veri = json.loads(SNAP.read_text(encoding="utf-8"))
        veri["borclar"][0]["aylik_faiz_orani"] = 55.0
        r = self.calistir(veri, "_gecici1.json")
        self.assertEqual(r.returncode, 1)
        self.assertIn("yıllık mı", r.stdout)

    def test_gecersiz_tur_yakalanir(self):
        veri = json.loads(SNAP.read_text(encoding="utf-8"))
        veri["varliklar"][0]["tur"] = "bitcoin"
        r = self.calistir(veri, "_gecici2.json")
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
