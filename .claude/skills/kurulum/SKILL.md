---
name: kurulum
description: Finansal Asistanım'ı yeni bir kullanıcı için kurar; kaynak klasörü ayarlar, izinleri yazar ve kısa bir görüşmeyle veri/profil.md dosyasını doldurur. Kullanıcı /kurulum yazdığında çalışır.
disable-model-invocation: true
---

# /kurulum — İlk kurulum

## 1. Teknik kurulum
`python3 kurulum.py --kontrol` çalıştır.
- `veri/ayarlar.json` yoksa kullanıcıya finansal belgelerinin bulunduğu klasörü sor.
  Seçenekler: Google Drive for Desktop ile senkron bir klasör ya da proje içindeki `veri/kaynak/`.
  Cevaba göre `python3 kurulum.py --kaynak "<yol>"` çalıştır. Kullanıcı TRY dışında bir ana para birimi
  söylediyse `--para-birimi` ile ver.
- Kurulum `.claude/settings.local.json` dosyasını yeni yazdıysa kullanıcıya şunu söyle:
  izinlerin devreye girmesi için Claude Code oturumunu kapatıp yeniden açması gerekir.

## 2. Profil görüşmesi
`veri/profil.md` dosyasını oku. Boş alanları kısa bir görüşmeyle doldur:
- Her mesajda en fazla 3 soru sor. Sırasıyla: gelir, sabit giderler, hane, hedefler, risk tercihi.
- Kullanıcı bir soruyu atlamak isterse alanı "belirtilmedi" olarak bırak.
- Rakamları kullanıcının söylediği gibi yaz, yuvarlama veya tahmin yapma.
- Bitince dosyayı yaz ve özetini göster, onay iste.

Bu dosyada borç ve varlık bakiyeleri **olmaz**. Onlar her değerlendirmede snapshot'a girer.

## 3. Kaynak klasör rehberi
Kullanıcıya klasörde hangi belgelerin işe yaradığını söyle:
- Banka ve kart hesap ekstreleri (PDF)
- Kredi ödeme planları
- Varlık ve borç listesi tablosu (.xlsx veya .csv). Google Sheets kullanıyorsa .xlsx olarak dışa aktarması gerekir.
- Serbest notlar (.md, .txt)

## 4. Bitiş
`python3 kurulum.py --kontrol` ile tekrar doğrula. Sonra kullanıcıya `/degerlendir` komutuyla ilk değerlendirmeyi başlatabileceğini söyle.
