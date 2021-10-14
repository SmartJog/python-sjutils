class TextDecoration:
    """Allows to decorate text in a terminal."""

    # styles
    NOSTYLE = "0"
    BOLDED = "1"
    DARKENED = "2"
    UNDERLINED = "4"
    STRIKED = "9"

    # modes
    NORMAL = "3"
    BACKGROUND = "4"
    LIGHTENED = "9"

    # colors
    WHITE = ""
    GREY = "0"  # BLACK if darkened
    RED = "1"
    GREEN = "2"
    YELLOW = "3"
    BLUE = "4"
    PURPLE = "5"
    CYAN = "6"

    def __init__(self, style=NOSTYLE, mode=NORMAL, color=WHITE, enabled=True):
        self._enabled = enabled
        self.set_text_style(style)
        self.set_text_mode(mode)
        self.set_text_color(color)

    def reset(self):
        """Fakes resetting decorations to default."""
        if not self._enabled:
            return ""
        return "\033[0m"

    def set_text_style(self, style):
        """Set the text style."""
        authorized = [
            TextDecoration.NOSTYLE,
            TextDecoration.BOLDED,
            TextDecoration.DARKENED,
            TextDecoration.UNDERLINED,
            TextDecoration.STRIKED,
        ]
        self._style = style if style in authorized else TextDecoration.NOSTYLE

    def set_text_mode(self, mode):
        """Set the text mode."""
        authorized = [
            TextDecoration.NORMAL,
            TextDecoration.BACKGROUND,
            TextDecoration.LIGHTENED,
        ]
        self._mode = mode if mode in authorized else TextDecoration.NORMAL

    def set_text_color(self, color):
        """Set the text color."""
        authorized = [
            TextDecoration.WHITE,
            TextDecoration.GREY,
            TextDecoration.RED,
            TextDecoration.GREEN,
            TextDecoration.YELLOW,
            TextDecoration.BLUE,
            TextDecoration.PURPLE,
            TextDecoration.CYAN,
        ]
        self._color = color if color in authorized else TextDecoration.WHITE

    def get(self):
        """Return the ansi escape sequence using the style, mode and color set."""
        if not self._enabled:
            return ""
        return "\033[%s;%s%sm" % (self._style, self._mode, self._color)
