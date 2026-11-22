---
name: finansal-snapshot
description: Drive'daki finans tablolarını, banka/kart ekstrelerini (PDF), notları ve kullanıcı beyanlarını tek bir normalize JSON snapshot'a dönüştürür. Kişisel finans verisi toplanırken veya güncellenirken kullan.
---

# Finansal Snapshot Üretimi

Amaç: Her değerlendirme aynı yapıda veriyle başlasın. Şema: `schema.json` (aynı klasörde).

## Kaynak türlerine göre okuma
| Kaynak | Nasıl okunur | Dikkat |
|---|---|---|
| `.xlsx` / `.csv` | Bash ile `python3 -c "import pandas as pd; print(pd.read_excel(...).to_string())"` | Birden fazla sayfa olabilir, hepsini listele |
| Google Sheets (`.gsheet`) | Drive for Desktop bunları kısayol olarak tutar, içerik yoktur | Kullanıcıdan .xlsx olarak dışa aktarmasını iste |
| PDF ekstre | Read aracıyla oku | Kart ekstresinde **dönem borcu**, **asgari ödeme**, **son ödeme tarihi** ve **akdi faiz oranı**nı al |
| `.md` / `.txt` / `.docx` notlar | Read | Tarihsiz bilgiyi `uyarilar`a ekle |
| Kullanıcı beyanı (sohbet) | Ana ajan iletir | `kaynak: "kullanıcı beyanı"` |

## Normalizasyon kuralları
- Tutarlar sayı olarak yazılır: `125000.50`. Binlik ayıracı yoktur.
- Türkiye'de kredi faizleri **aylık** verilir. `aylik_faiz_orani` alanına yüzde olarak yaz (örn. `4.25`).
- Döviz ve altın varlıkları kendi para biriminde kalır, TRY'ye çevrilmez. Çeviriyi analiz script'i yapar.
  Altın için `para_birimi: "XAU_GRAM"` ve `tutar` = gram.
- `likit: true` sadece 1 hafta içinde zararsız nakde dönebilen varlıklar içindir: nakit, vadesiz, PPF, vadesi gelen mevduat.
- Aynı kalem iki kaynakta varsa daha yeni tarihliyi al, diğerini `uyarilar`a yaz.
- Bilinmeyen alanı `null` bırak ve `eksikler` listesine ekle. Uydurma.

## Doğrulama
Yazdıktan sonra çalıştır:
```
python3 .claude/skills/finansal-snapshot/scripts/validate.py veri/snapshots/YYYY-MM-DD.json
```
Örnek dosya: `veri/ornek/snapshot-ornek.json`.
