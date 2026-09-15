# Серия 1 — промпты motion

Не генерировать 50 секунд одним роликом.  
8 клипов → склейка. Каждый клип: **start frame + end frame + промпт только про движение**.

Инструмент: Kling / Runway Gen-4 / Luma, режим Image-to-Video.  
Кадр 8 не анимировать — это плашка.

## Замок (вставлять в каждый промпт)

```
Keep the exact same illustrated 2D characters, faces, costumes, and room.
Subtle sitcom motion only. No face morph. No style change. No extra people.
No photoreal conversion. No 3D. No camera shake. No text. No subtitles.
```

## Негатив (если поле есть)

```
face morph, identity change, extra fingers, extra arms, costume change,
headscarf pattern change, room redesign, photoreal, 3D, anime, blur,
jitter, warp, text, watermark, logo
```

Настройки по умолчанию: 9:16, 24 fps, motion **low / 3–4 из 10**.  
Если лицо поплыло — клип брак, не чинить морфом.

| Клип | Старт | Конец | Длит. | Куда в таймлайн |
|---|---|---|---|---|
| 01 | `storyboard/sb-01-open-apartment.png` | `motion/ends/sb-01-end.png` | 5 с × 2 | 0:00–0:10 |
| 02 | `storyboard/sb-02-phone-scroll.png` | `motion/ends/sb-02-end.png` | 5 с × 2 | 0:10–0:20 |
| 03 | `storyboard/sb-03-time-jump.png` | `motion/ends/sb-03-end.png` | 5 с + 0:20–0:22 dissolve из 01 | 0:20–0:32 |
| 04 | `storyboard/sb-04-father-scolds.png` | `motion/ends/sb-04-end.png` | 5 с | 0:32–0:37 |
| 05 | `storyboard/sb-05-shushen-defends.png` | `motion/ends/sb-05-end.png` | 5 с + 2 с hold | 0:37–0:44 |
| 06 | `storyboard/sb-06-father-vay.png` | `motion/ends/sb-06-end.png` | 2.5 с | 0:44–0:46 |
| 07 | `storyboard/sb-07-dont-interfere.png` | `motion/ends/sb-07-end.png` | 2 с | 0:46–0:48 |
| 08 | `storyboard/sb-08-endcard.png` | — | 2–3 с статично | 0:48–0:50 |

Клипы 01–02 длиннее 5 с: сгенерировать два дубля и склеить, либо зациклить с кроссфейдом посередине. Не просить модель «10 секунд одного дубля» — чаще плывут лица.

---

## 01. Завязка 0:00–0:10

**Промпт**

```
Slow gentle push-in on a cozy illustrated living room.
Mama on the sofa lifts her phone a little and taps the screen as if dialing.
The young son at the table slowly raises a small tea glass toward his lips and sips.
Soft blinks. Steam stays still. Furniture locked. Faces locked.
```

Камера: медленный наезд, без панорам.  
Звук под картинку: тихий чай, потом гудки. Голоса ещё нет.

## 02. Телефон 0:10–0:20

**Промпт**

```
Close-up. Mama's thumb scrolls a phone. Cartoon photos of young women
flick upward one by one. Her eyebrows jump and her mouth tightens
on each reject. Head stays framed. Headscarf pattern stays identical.
Only hand, brows, and phone screen move.
```

На склейке: каждый «Ой / эта / у этой» = смена фото (hard cut или быстрый flick).  
Если экран телефона плывёт — оставить лицо живым, фото заменить вручную в монтаже оверлеем.

## 03. Скачок времени 0:20–0:32

Сначала в монтаже: **dissolve 1.5–2 с** из конца клипа 01 в старт клипа 03.  
Это и есть «прошло пять лет». Моделью морфить 23→28 не надо.

**Промпт**

```
The father walks two steps and sits into the carved armchair.
He leans forward, raising one hand, about to speak.
The bearded tired son stays seated, barely turns his eyes.
Mama on the sofa holds still with the phone.
Slow, heavy, no comedy bounce. Room locked.
```

Тишина + низкий аккорд. Голос отца входит только в 0:32.

## 04. Отец строго 0:32–0:37

**Промпт**

```
Medium close-up of the father in the armchair.
He leans in and chops the air with one hand in three short beats
matching angry speech. Thick brows lower. Mouth opens on the last beat.
No standing up. No costume change.
```

Три удара руки: «что стало» / «28 лет» / «чем ты занимаешься».

## 05. Шушэн оправдывается 0:37–0:44

**Промпт**

```
Mama on the sofa talks fast and waves both hands.
The phone stays in her right hand and never leaves the frame.
Shoulders bounce a little. Eyes wide. Headscarf locked.
Warm sitcom energy, not slapstick.
```

Руки всё время в кадре. Телефон — якорь, чтобы модель не дорисовала третью руку.

## 06. «Вай!» 0:44–0:46

**Промпт**

```
The father throws both arms wide, palms up, in one surprised burst.
Eyebrows shoot up. Short motion, then a tiny hold.
No standing. Face stays the same man.
```

Один жест на всё «Шушэн, вай!». Не петля.

## 07. «Не вмешивайся» 0:46–0:48

**Промпт**

```
Mama in the foreground points a finger at her husband and lifts her chin,
shutting the argument down. The father in the armchair freezes, slightly recoils.
Two-second beat. No extra motion after the point.
```

После жеста — freeze 4–6 кадров, затем плашка.

## 08. Плашка 0:48–0:50

Движения нет. Fade in 8 кадров + джингл.  
Текст не печатать по буквам и не доверять модели — он уже на кадре.

```
Продолжение во 2-й серии...
Подпишись на One Soul
```

---

## Склейка

1. Клипы встык. Между 02 и 03 — dissolve. Остальное — прямой cut в жест.
2. Голоса поверх, см. `voice/TIMELINE.md`.
3. Субтитры из `voice/series1.srt`.
4. Бытовой фон 01–02 тише голоса на −20 dB. С 03 — почти тишина, потом отец.
5. В конце 0.4 с джингла, без нового голоса.

Если один клип хорош, а лицо в следующем другое — не «усреднять». Перегенерировать плохой, стартуя с того же start frame.
