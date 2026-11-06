import {Audio, Video} from "@remotion/media";
import {TransitionSeries, linearTiming} from "@remotion/transitions";
import {fade} from "@remotion/transitions/fade";
import React from "react";
import {interpolate, staticFile, useCurrentFrame, useVideoConfig} from "remotion";

const fill = {
  width: "100%",
  height: "100%",
} as const;

const Shot: React.FC<{readonly file: string; readonly name: string}> = ({
  file,
  name,
}) => {
  return (
    <Video
      name={name}
      src={staticFile(file)}
      objectFit="cover"
      style={fill}
    />
  );
};

export const SERIES_FPS = 30;
const FADE = 12;
// Кадры 10–17. Один мотив на все тихие кадры, без склеек между ними.
const MUSIC_FROM = 1936;
const MUSIC_FRAMES = 1176;

// Речь целиком плюс короткий хвост, чтобы не срезать последнее слово.
// Немые куски и заставка держатся целиком. Бумажные 2:09 не ужимаются.
export const SERIES_FRAMES =
  217 +
  237 +
  233 +
  226 +
  243 +
  123 +
  243 +
  216 +
  198 +
  150 * 8 +
  229 +
  297 +
  300 +
  278 +
  229 +
  150 -
  FADE * 2;

export const Series3: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const dissolve = linearTiming({durationInFrames: Math.round(0.4 * fps)});
  const musicVolume = interpolate(
    frame,
    [
      MUSIC_FROM,
      MUSIC_FROM + 12,
      MUSIC_FROM + MUSIC_FRAMES - 15,
      MUSIC_FROM + MUSIC_FRAMES,
    ],
    [0, 1, 1, 0],
    {extrapolateLeft: "clamp", extrapolateRight: "clamp"},
  );

  return (
    <>
    <TransitionSeries name="Серия 3">
      <TransitionSeries.Sequence name="Кадр 1" durationInFrames={217}>
        <Shot file="shots/k01.mp4" name="Улица" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 2" durationInFrames={237}>
        <Shot file="shots/k02.mp4" name="Моргол" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 3" durationInFrames={233}>
        <Shot file="shots/k03.mp4" name="Надежда" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 4" durationInFrames={226}>
        <Shot file="shots/k04.mp4" name="Телефон" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 5" durationInFrames={243}>
        <Shot file="shots/k05.mp4" name="Портрет" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 6" durationInFrames={123}>
        <Shot file="shots/k06.mp4" name="Дербент" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 7" durationInFrames={243}>
        <Shot file="shots/k07.mp4" name="Ихил" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 8" durationInFrames={216}>
        <Shot file="shots/k08.mp4" name="Шидух" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 9" durationInFrames={198}>
        <Shot file="shots/k09.mp4" name="Конечно" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 10" durationInFrames={150}>
        <Shot file="shots/k10.mp4" name="Звонок" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={dissolve} />
      <TransitionSeries.Sequence name="Кадр 11" durationInFrames={150}>
        <Shot file="shots/k11.mp4" name="Кафе" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 12" durationInFrames={150}>
        <Shot file="shots/k12.mp4" name="Аллея" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={dissolve} />
      <TransitionSeries.Sequence name="Кадр 13" durationInFrames={150}>
        <Shot file="shots/k13.mp4" name="Зал" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 14" durationInFrames={150}>
        <Shot file="shots/k14.mp4" name="Центр" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 15" durationInFrames={150}>
        <Shot file="shots/k15.mp4" name="Родители" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 16" durationInFrames={150}>
        <Shot file="shots/k16.mp4" name="Танец" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 17" durationInFrames={150}>
        <Shot file="shots/k17.mp4" name="Взгляд" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 18" durationInFrames={229}>
        <Shot file="shots/k18.mp4" name="Раввин" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 19" durationInFrames={297}>
        <Shot file="shots/k19.mp4" name="Один народ" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 20" durationInFrames={300}>
        <Shot file="shots/k20.mp4" name="Крупно" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 21" durationInFrames={278}>
        <Shot file="shots/k21.mp4" name="Ладони" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Кадр 22" durationInFrames={229}>
        <Shot file="shots/k22.mp4" name="Улыбка" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Заставка" durationInFrames={150}>
        <Shot file="shots/endcard.mp4" name="Логотип" />
      </TransitionSeries.Sequence>
    </TransitionSeries>
    <Audio
      name="Праздничный мотив"
      src={staticFile("music/festive.mp3")}
      from={MUSIC_FROM}
      durationInFrames={MUSIC_FRAMES}
      volume={musicVolume}
    />
    </>
  );
};
