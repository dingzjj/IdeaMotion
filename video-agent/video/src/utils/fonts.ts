import { loadFont } from "@remotion/google-fonts/Inter";

/**
 * Load Inter from Google Fonts.
 * Imported at the root level so Remotion blocks rendering until the font is ready.
 * Use `fontFamily` as the CSS font-family value in any component.
 */
export const { fontFamily: INTER_FONT_FAMILY, waitUntilDone: waitForInter } =
  loadFont("normal", {
    weights: ["400", "500", "700", "800"],
    subsets: ["latin"],
  });
