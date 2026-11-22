---
name: finansal-analiz
description: Kişisel finans snapshot'ından net değer, likidite, acil durum fonu, borç/gelir oranı, faiz maliyeti ve borç kapatma senaryolarını script ile hesaplayıp Türkçe değerlendirme raporu yazar. Borç, nakit, birikim veya genel finansal durum değerlendirmesi istendiğinde kullan.
---

# Finansal Analiz

## 1. Hesapla (LLM hesap yapmaz)
```
python3 .claude/skills/finansal-analiz/scripts/metrics.py veri/snapshots/<tarih>.json \
  --piyasa veri/snapshots/piyasa-<tarih>.json \
  --onceki veri/snapshots/<onceki-tarih>.json \
  --ekstra-oran 0.5
```
- `--onceki`: `veri/snapshots/` altındaki bir önceki tarihli snapshot. Yoksa çıkar.
- `--ekstra-oran`: serbest nakdin borca ayrılacak kısmı. Kullanıcı başka bir oran söylediyse onu kullan.
  Farklı oranları karşılaştırmak için script'i birkaç kez çalıştırabilirsin.

## 2. Yorumla
Eşikler ve Türkiye'ye özgü notlar: `references/degerlendirme-kurallari.md`. Bunu oku.

## 3. Yaz
Şablon: `references/rapor-sablonu.md`. Bölüm sırasını koru.
Rapordaki her rakam script çıktısından veya piyasa dosyasından gelmeli.
