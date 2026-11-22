# Güvenlik ve Gizlilik

## Güvenlik açığı bildirme
Bir güvenlik açığı bulduysanız **herkese açık bir issue açmayın.**
Repodaki **Security → Report a vulnerability** bağlantısıyla gizli olarak bildirin.
En geç 7 gün içinde dönüş yapılır.

Kapsamdaki örnekler:
- Kişisel verinin git'e sızmasına yol açan `.gitignore` veya kurulum hataları
- Kaynak klasörün salt okunur korumasını aşan izin ayarları
- Ajanların yetkisi dışındaki araçlara erişebilmesi
- Belge içeriğine gömülü talimatlarla (prompt injection) ajanın kural dışı davranması

## Veri akışı
| Veri | Nerede durur | Nereye gider |
|---|---|---|
| Belgeleriniz | Sizin klasörünüz | Analiz sırasında içerik Claude'a (Anthropic) gönderilir |
| Profil, snapshot'lar, raporlar | `veri/` ve `raporlar/` | Hiçbir yere; `.gitignore`'dadır |
| Piyasa verisi | `veri/snapshots/piyasa-*.json` | Web aramasıyla alınır |

Anthropic'in veri kullanım politikası için: <https://www.anthropic.com/legal/privacy>

## Kullanıcı için öneriler
- Forkladığınız repoyu **private** tutmayı düşünün. `.gitignore` korur, ama `git add -f` ile yanlışlıkla eklenen dosyayı korumaz.
- Push etmeden önce `git status` ile neyin gideceğini kontrol edin.
- Belge klasörünüze şifre, PIN, kart CVV'si veya kimlik fotoğrafı koymayın. Analiz için gerekmezler.
- Ekstrelerdeki tam kart numaraları gerekli değil. Mümkünse maskelenmiş ekstreleri kullanın.

## Desteklenen sürümler
Yalnızca en son sürüm güvenlik güncellemesi alır.
