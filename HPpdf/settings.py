"""Settings"""

from reportlab.lib.units import cm

########## LESSON
START_HOUR = 8
END_HOUR = 19

MAX_GROUP = 9

DAYS = 5

######## COLORS
TYPE_LESSON_COLOR = {
    'CM': '#9fc6e7',  # blue
    'TP': '#7bd148',  # green
    'TD': '#fff31e',  # yellow
    'DS': '#f83a22',  # red
}
DEFAULT_TYPE_LESSON_COLOR = "#888888"

########### PAGE
MARGIN = {
    'top': .5*cm,
    'left': .5*cm,
    'bottom': .5*cm,
    'right': .5*cm,
}

RECT_RADIUS = 3.

######### HEADERS
HEADERS_HEIGHT = 30.
HEADERS_FONT_SIZE = 15

########## TABLE
COLUMN_TITLE_HEIGHT = 12.  # 1.*cm
ROW_TITLE_WIDTH = 12  # 1.*cm

HOUR_DIVISION_MINUTES = 15