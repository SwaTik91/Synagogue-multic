# Голоса через OpenRouter

Ключ **не хранить в репозитории**. В шелле:

```bash
export OPENROUTER_API_KEY='…'
```

## Замок на сезон

| Роль | Модель | Voice |
|---|---|---|
| Шушэн | `google/gemini-3.1-flash-tts-preview` | `Sulafat` |
| Отец | `google/gemini-3.1-flash-tts-preview` | `Charon` |

Gemini на этом эндпоинте отдаёт только `response_format: pcm` (24 kHz, mono, s16le). Потом:

```bash
ffmpeg -f s16le -ar 24000 -ac 1 -i take.pcm -c:a libmp3lame -q:a 3 take.mp3
```

Grok / MiniMax / Fish пробовали: русский есть, но слабее держат возраст и «вай». Не менять замок без новой прослушки.

## Дубли

| Файл | Окно по сценарию | Факт |
|---|---|---|
| `renders/shushen-a.mp3` | 10 с | ~18.5 с |
| `renders/shushen-b.mp3` | 7 с | ~11.3 с |
| `renders/shushen-c.mp3` | 2 с | спокойный ровный тон, без нежности |
| `renders/father-d.mp3` | 5 с | ~9.6 с |
| `renders/father-e.mp3` | 2 с | ~5.3 с |

Слов больше, чем лезет в 50 с, если говорить по-человечески. Слуховой монтаж поэтому ~66 с: `preview/series1-with-vo.mp4`.  
Более медленные дубли: `renders/natural/`.

Имя «Шушэн» у отца TTS иногда сглатывает. Если режет слух — перезаписать только `father-d` тем же Charon.

## Как перегенерировать один дубль

`POST https://openrouter.ai/api/v1/audio/speech`

В `input` сначала режиссёрские ноты, потом ровно такая строка:

```
#### TRANSCRIPT
```

и русский текст. Ноты модель не читает вслух. Теги вроде `[fast]`, `[stern]`, `[proud]` работают.
