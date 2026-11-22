---
name: degerlendir
description: Kişisel finansal durumun uçtan uca değerlendirmesini başlatır; veri toplama, piyasa araştırması ve analiz ajanlarını sırayla çalıştırır. Kullanıcı /degerlendir yazdığında çalışır.
disable-model-invocation: true
---

# /degerlendir — Orkestrasyon

Bugünün tarihi = TARİH. Ek bilgi: $ARGUMENTS

## 0. Ön kontrol
`python3 kurulum.py --kontrol` çalıştır. Hata dönerse kullanıcıyı `/kurulum` komutuna yönlendir ve dur.
Excel kütüphanesi eksik uyarısı tek başına durma sebebi değildir.

## 1. Kullanıcıdan güncel bilgileri al
Kaynak klasörde olmayan ya da her seferinde değişen bilgileri tek mesajda sor:
- Elinizdeki nakit ve hesap bakiyeleri
- Drive'a girmemiş yeni borç, ödeme veya büyük harcama
- Bu dönemdeki özel durum (ikramiye, iş değişikliği, beklenen büyük gider)
- Bu değerlendirmeden özel bir soru var mı?

Kullanıcı `$ARGUMENTS` ile bunları zaten verdiyse tekrar sorma.

## 2. Paralel çalıştır
Aynı anda iki ajan başlat:
- `veri-toplayici`: kaynak klasör + 1. adımdaki bilgiler → `veri/snapshots/TARİH.json`
- `piyasa-arastirmaci`: → `veri/snapshots/piyasa-TARİH.json`

## 3. Eksikleri kapat
`veri-toplayici` soru döndürdüyse kullanıcıya sor, cevaba göre snapshot'ı güncellet.

## 4. Analiz
`finans-analisti` ajanını başlat. Ona snapshot, piyasa dosyası ve (varsa) bir önceki snapshot yolunu ver.

## 5. Sonuç
Kullanıcıya şunları göster:
- Raporun 3 maddelik özeti
- Rapor dosyasının yolu
- Varsa kullanıcının özel sorusunun cevabı
