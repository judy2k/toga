from android.graphics import Color
from android.widget import LinearLayout, TextView
from travertino.size import at_least

from .label import TextViewWidget


class Divider(TextViewWidget):
    def create(self):
        self.native = TextView(self._native_activity)
        self.cache_textview_defaults()

        # Background color needs to be set or else divider will not be visible.
        self.native.setBackgroundColor(Color.LTGRAY)

        self._direction = self.interface.HORIZONTAL

    def get_direction(self):
        return self._direction

    def set_direction(self, value):
        self._direction = value

        if value == self.interface.VERTICAL:
            # Set the height for a vertical divider
            params = LinearLayout.LayoutParams(1, self.interface._MIN_HEIGHT)
        else:
            # Set the width for a horizontal divider
            params = LinearLayout.LayoutParams(self.interface._MIN_WIDTH, 1)

        self.native.setLayoutParams(params)

    def rehint(self):
        if self.get_direction() == self.interface.VERTICAL:
            self.interface.intrinsic.width = 1
            self.interface.intrinsic.height = at_least(self.native.getHeight())
        else:
            self.interface.intrinsic.width = at_least(self.native.getWidth())
            self.interface.intrinsic.height = 1
