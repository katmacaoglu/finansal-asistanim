# Katkıda Bulunma Rehberi

İlginiz için teşekkürler! Bu proje herkesin kendi finansını daha iyi anlaması için var. Her türlü katkı değerli.

## Nasıl katkı verebilirim?

| Katkı türü | Nereden başlamalı |
|---|---|
| 🐛 Hata bildirimi | [Hata bildirimi şablonu](https://github.com/katmacaoglu/finansal-asistanim/issues/new?template=hata.md) |
| 💡 Özellik önerisi | [Özellik önerisi şablonu](https://github.com/katmacaoglu/finansal-asistanim/issues/new?template=ozellik.md) |
| 📝 Dokümantasyon | Doğrudan pull request açabilirsiniz |
| 🌍 Yeni ülke kural seti | Önce bir issue açın, kaynakları birlikte belirleyelim |
| 🧮 Hesaplama ve script | Test ile birlikte pull request |

> [!IMPORTANT]
> Issue veya PR'a **gerçek finansal verilerinizi koymayın.** Örnek gerekiyorsa `veri/ornek/` altındaki uydurma verileri kullanın ya da rakamları değiştirin.

## Geliştirme ortamı

```bash
git clone https://github.com/<sizin-kullanici-adiniz>/finansal-asistanim.git
cd finansal-asistanim
python3 -m unittest discover tests
```

Script'ler sadece Python standart kütüphanesini kullanır. Excel okumak için gereken `pandas` ve `openpyxl` dışında bağımlılık eklemeyin. Eklemeniz gerekiyorsa önce issue'da tartışalım.

## Değişiklik türüne göre kurallar

### Python script'leri (`metrics.py`, `validate.py`, `kurulum.py`)
- Her yeni hesaplama için `tests/` altına test ekleyin.
- Çıktı JSON alan adları Türkçe ve `snake_case` kalsın. Mevcut alanların adını değiştirmek geriye dönük uyumluluğu bozar; bunu CHANGELOG'da belirtin.

### Şema (`schema.json`)
- Yeni alan ekliyorsanız opsiyonel yapın, mevcut snapshot'lar bozulmasın.
- `veri/ornek/snapshot-ornek.json` dosyasını da güncelleyin.

### Ajan ve skill dosyaları (`.md`)
- Bunlar prompt'tur. Küçük bir kelime değişikliği bile davranışı değiştirebilir.
- PR açıklamasında değişikliği gerçek bir `/degerlendir` çalıştırmasıyla denediğinizi ve sonucu yazın.
- `description` alanları skill'in ne zaman seçileceğini belirler. Bunları değiştirirken dikkatli olun.
- Ajanların araç yetkilerini (`tools:`) genişletmek güvenlik değişikliğidir. Gerekçesini açıklayın.

### Değerlendirme kuralları
- Eşik değiştiriyorsanız kaynağını yazın.
- Belirli bir ürün, hisse, fon veya kripto öneren kural kabul edilmez.

## Pull request süreci
1. Repoyu fork'layın ve bir dal açın: `git checkout -b ozellik/kisa-aciklama`
2. Değişikliğinizi yapın, testleri çalıştırın.
3. `CHANGELOG.md` dosyasının en üstüne **Yayınlanmadı** başlığı altında bir satır ekleyin.
4. PR açın ve şablonu doldurun.

Commit mesajları Türkçe veya İngilizce olabilir. Kısa, emir kipinde bir başlık yeterli: `Kartopu simülasyonuna asgari ödeme kontrolü ekle`.

## Davranış kuralları
Bu projeye katılan herkes [Davranış Kuralları](CODE_OF_CONDUCT.md)'na uymayı kabul eder.
