# Finansal Asistanım — Proje Hafızası

Bu klasör, kişisel finansal durumun düzenli aralıklarla değerlendirildiği bir Claude Code projesidir.
Claude bu dosyayı her oturumun başında okur.

## Oturum başında
`veri/ayarlar.json` veya `veri/profil.md` yoksa kullanıcıya önce `/kurulum` çalıştırmasını öner.

## Veri nerede
- Kullanıcı ayarları: `veri/ayarlar.json`. `kaynak_klasor` alanı ham belgelerin yeridir. Bu klasör **salt okunur** kullanılır.
- Kullanıcı profili ve hedefler: `veri/profil.md`.
- Normalize edilmiş anlık durumlar: `veri/snapshots/YYYY-MM-DD.json` (şema: `.claude/skills/finansal-snapshot/schema.json`).
- Piyasa verileri: `veri/snapshots/piyasa-YYYY-MM-DD.json`.
- Raporlar: `raporlar/YYYY-MM-DD-degerlendirme.md`.

## Komutlar
- `/kurulum`: ilk kurulum ve profil görüşmesi.
- `/degerlendir [ek bilgi]`: uçtan uca değerlendirme.

## Akış
1. `veri-toplayici` ajanı kaynak klasörü okur, kullanıcının sohbette verdiği bilgilerle birleştirir, snapshot üretir.
2. `piyasa-arastirmaci` ajanı güncel faiz, enflasyon ve kur verilerini web'den çeker. Bu adım 1. adımla paralel çalışır.
3. Eksik veya çelişkili bilgi varsa kullanıcıya sorulur. Tahmin yapılmaz.
4. `finans-analisti` ajanı metrikleri **script ile** hesaplar, önceki snapshot ile karşılaştırır, raporu yazar.

## Kurallar
- Rakamlar asla tahmin edilmez veya akıldan yazılmaz. Hesaplar `finansal-analiz/scripts/metrics.py` ile yapılır.
- Güncel oranlar her seferinde web'den doğrulanır ve kaynağı yazılır.
- Çıktı bir analizdir, lisanslı yatırım danışmanlığı değildir. Belirli hisse, fon veya kripto alım-satım önerisi verilmez.
  Seçenekler artı/eksileri ve rakamlarıyla sunulur, karar kullanıcıya bırakılır.
- Kaynak klasöre yazılmaz, hiçbir yerde dosya silinmez.
- Rapor dili: Türkçe, kısa cümleler, önce sonuç sonra detay.
