# GeoIP-базы (MaxMind GeoLite2)

Сюда кладутся offline-базы для детерминированного определения страны хостинга
по IP (`pdn_parser/geoip.py`):

- `GeoLite2-Country.mmdb` — **обязательная**, страна по IP (ISO-2).
- `GeoLite2-ASN.mmdb` — *опциональная*, ASN и провайдер; улучшает пометку CDN
  и заполняет `hosting_provider`/`server_asn`.

Сами `.mmdb` **не коммитятся** (см. `.gitignore`): они большие и лицензионные.
Без них парсер не падает — `meta.server_country` будет `null`
(страну не выдумываем). Каталог можно переопределить переменной `GEOIP_DB_DIR`.

## Как получить базы

GeoLite2 бесплатна, но требует учётной записи MaxMind и license key.

1. Зарегистрируйтесь на https://www.maxmind.com/en/geolite2/signup и создайте
   license key (Account → Manage License Keys).
2. Скачайте базы:

   ```bash
   MAXMIND_LICENSE_KEY=xxxxx python ../../scripts/download_geoip.py \
       --out . --editions GeoLite2-Country GeoLite2-ASN
   ```

   Скрипт скачивает официальные tar.gz с download.maxmind.com и распаковывает
   `*.mmdb` в этот каталог.

## Обновление

MaxMind обновляет GeoLite2 еженедельно (вторник). Базу стоит освежать
регулярно (cron / пересборка образа). Альтернатива скрипту — официальный
`geoipupdate`. В Docker базы скачиваются при сборке, если задан build-arg
`MAXMIND_LICENSE_KEY` (см. `crowler/Dockerfile`).

## Лицензия и атрибуция

> This product includes GeoLite2 data created by MaxMind, available from
> <https://www.maxmind.com>.

Использование GeoLite2 регулируется
[MaxMind GeoLite2 EULA](https://www.maxmind.com/en/geolite2/eula). Атрибуцию
MaxMind необходимо сохранять. Альтернатива со схожей лицензией —
IP2Location LITE (CC BY 4.0).
