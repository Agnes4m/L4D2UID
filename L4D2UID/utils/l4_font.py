from PIL import ImageFont

from gsuid_core.utils.fonts.fonts import core_font as l4_font


def l4_font_main(size: int) -> ImageFont.FreeTypeFont:
    return l4_font(size)


l4_font_20 = l4_font_main(20)
l4_font_22 = l4_font_main(22)
l4_font_23 = l4_font_main(23)
l4_font_24 = l4_font_main(24)
l4_font_25 = l4_font_main(25)
l4_font_26 = l4_font_main(26)
l4_font_28 = l4_font_main(28)
l4_font_30 = l4_font_main(30)
l4_font_32 = l4_font_main(32)
l4_font_34 = l4_font_main(34)
l4_font_36 = l4_font_main(36)
l4_font_38 = l4_font_main(38)
l4_font_40 = l4_font_main(40)
