import {Composition} from "remotion";
import {SERIES_FRAMES, SERIES_FPS, Series3} from "./Series3";

export const MyComposition = () => {
  return (
    <Composition
      id="Series3"
      component={Series3}
      durationInFrames={SERIES_FRAMES}
      fps={SERIES_FPS}
      width={1080}
      height={1920}
    />
  );
};
