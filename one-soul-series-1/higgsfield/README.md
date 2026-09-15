# Higgsfield — только рот, голоса наши

OpenRouter / Sulafat / Charon **не меняем**.  
Higgsfield нужен, чтобы посадить рот на уже снятый вариант В.

MCP подключён: модель `sync_so` (Sync Lipsync 3). Cost-preflight у этой модели ломается (пустой `prompt`), генерация без `get_cost` проходит. ~3 кредита/с.

## Что уже врезано в вариант В

1. **Финал** (~1:06) — `back/01-end.mp4`  
   Нежный дубль «ты ничего не понимаешь…» на живой двухплан `07`. В склейке берём первые 4.40 с, хвост Sync с оплавленными руками отрезаем.
2. **Около 50 с** — `back/02-around-50s-cu.mp4`  
   Реплика Шушэн на замке `style/c-defend-cu-closed.png`. Sync по живому I2V `05w`/`05c` переписывал мизансцену (трубка, чужой человек) — этот дубль в монтаж не берём.

Склейка: `preview/mux-c-lipsync.py` (картинка поверх живого В, дорожка звука не трогается).

## Проба целого куска (не lipsync на застывший кадр)

Финал «Ты не понимаешь, так что не вмешивайся» сгенерирован целиком из `style/c-07-dont.png`:

| Файл | Что это |
|---|---|
| `preview/piece-end-wan27.mp4` | Wan 2.7, 6 с. Картинка + **наш** Sulafat. Рука живая. |
| `preview/piece-end-kling30.mp4` | Kling 3.0, 8 с. Своя речь модели. Рука живая. |

https://github.com/SwaTik91/Synagogue-multic/raw/cursor/one-soul-series1-bible-28ef/one-soul-series-1/preview/piece-end-wan27.mp4  
https://github.com/SwaTik91/Synagogue-multic/raw/cursor/one-soul-series1-bible-28ef/one-soul-series-1/preview/piece-end-kling30.mp4

Полный живой пилот: `preview/series1-wan.mp4` (~74 с).  
Завязка отдельно: `preview/series1-wan-open.mp4`. Хвост: плашка Pillow → дом 28 → отец / защита / вай → финал `piece-end-wan27.mp4`.

## Листы героев на будущее

3D character sheets лежат в `style/hf-sheets/`. В Higgsfield они сохранены как Elements: **Shushen**, **Father**, **Ikhil-23**, **Ikhil-28**.

Wan 2.7 Elements может не подхватить — для него лист класть стартовым кадром. Kling / Seedance / картинки зовут героя по имени. Soul не тренировать.

## Пакеты для следующих реплик

В `01-end/` и `02-around-50s/`: `picture.mp4` + `voice.mp3`.  
Дальше тем же способом: отец (`04m`+`04c` + `father-d`) и завязка (`01w`+`01c` + `shushen-judge`). На жестикуляцию Sync лучше не кормить — сначала locked-off still, как CU.

## Чего не делать

- Не генерировать голос заново в Higgsfield Audio.
- Не отдавать весь 76-секундный ролик одним куском.
- Не подменять живой монтаж статичным RMS-флапом целиком.
- Не Soul-ID «с нуля» вместо наших `style/c-*.png`, пока не решим менять замок лиц.
