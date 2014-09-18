import datetime
import locale
import os
import collections

from reportlab import platypus
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes


import lesson
from lesson import join_filter
import settings

locale.setlocale(locale.LC_ALL, {
    'nt': 'fra_fra',
    'posix': 'fr_FR.utf8'
}[os.name])


def iso_to_gregorian(iso_year, iso_week, iso_day):
    """Gregorian calendar date for the given ISO year, week and day"""
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(weeks=iso_week-1, days=iso_day - fourth_jan.isoweekday())
    return fourth_jan + delta


styles = {
    'left': ParagraphStyle(name='left', alignment=TA_LEFT, fontSize=8, leading=9),
    'center': ParagraphStyle(name='center', alignment=TA_CENTER, fontSize=10, leading=11),
    'right': ParagraphStyle(name='right', alignment=TA_RIGHT, leading=11),
}


def all_cells(key, value):
    return key, (-1, -1), (-1, -1), value


PADDING = [
    all_cells(d + 'PADDING', x)
    for d, x in [('TOP', 0), ('LEFT', 1), ('BOTTOM', 1), ('RIGHT', 1)]
]

styles2 = {
    'top_left': platypus.TableStyle([
        all_cells('ALIGN', 'LEFT'),
        all_cells('VALIGN', 'TOP'),
    ] + PADDING),
    'bottom_right': platypus.TableStyle([
        all_cells('ALIGN', 'RIGHT'),
        all_cells('VALIGN', 'BOTTOM')
    ] + PADDING),
}


def float_time(time):
    return float(time.hour - settings.START_HOUR) + time.minute/60.


class Schedule(canvas.Canvas):
    HOURS = settings.END_HOUR - settings.START_HOUR
    QUARTER = 60 // settings.HOUR_DIVISION_MINUTES

    PAGE_WIDTH, PAGE_HEIGHT = pagesizes.landscape(pagesizes.A4)

    width = PAGE_WIDTH - settings.MARGIN['left'] - settings.MARGIN['right']
    height = PAGE_HEIGHT - settings.MARGIN['bottom'] - settings.MARGIN['top']

    hours = list(range(settings.START_HOUR, settings.END_HOUR))

    table_left = settings.ROW_TITLE_WIDTH
    table_bottom = 0.
    table_right = width
    table_top = height - settings.COLUMN_TITLE_HEIGHT - settings.HEADERS_HEIGHT

    #table_width = width - settings.ROW_TITLE_WIDTH
    #table_height = height - settings.HEADERS_HEIGHT - settings.COLUMN_TITLE_HEIGHT
    table_v_step = (table_top - table_bottom) / settings.DAYS
    table_vv_step = table_v_step / settings.MAX_GROUP
    table_h_step = (table_right - table_left) / HOURS
    table_hh_step = table_h_step / QUARTER

    def __init__(self, filename):
        super().__init__(filename, (self.PAGE_WIDTH, self.PAGE_HEIGHT))

    def drawString(self, x, y, *args, **kwargs):
        super().drawString(x+1., y+2., *args, **kwargs)

    def drawRightString(self, x, y, *args, **kwargs):
        super().drawRightString(x-1., y+2., *args, **kwargs)

    def drawCentredString(self, x, y, *args, **kwargs):
        super().drawCentredString(x, y+2., *args, **kwargs)

    def drawVerticalCentredString(self, x, y, *args, **kwargs):
        self.saveState()
        self.translate(x, y)
        self.rotate(90)
        self.drawCentredString(0., 0., *args, **kwargs)
        self.restoreState()

    def draw_columns(self):
        x = self.table_left
        for hour in self.hours:
            xp = x
            for quarter in range(1, self.QUARTER):
                xp += self.table_hh_step
                self.setStrokeColorRGB(.8, .8, .8)
                self.line(xp, self.table_bottom, xp, self.table_top)
            self.setStrokeColorRGB(.5, .5, .5)
            self.line(x, self.table_bottom, x, self.table_top + settings.COLUMN_TITLE_HEIGHT)
            self.drawString(x, self.table_top, '%dh' % hour)
            x += self.table_h_step
        self.line(x, self.table_bottom, x, self.table_top + settings.COLUMN_TITLE_HEIGHT)
        self.drawRightString(x, self.table_top, '%dh' % settings.END_HOUR)

    def draw_rows(self, days):
        self.setStrokeColorRGB(.5, .5, .5)
        y = self.table_top
        for day in days:
            self.line(self.table_left - settings.ROW_TITLE_WIDTH, y, self.table_right, y)
            self.drawVerticalCentredString(self.table_left, y - self.table_v_step/2., day.strftime('%A %d/%m'))
            y -= self.table_v_step
        self.line(self.table_left - settings.ROW_TITLE_WIDTH, y, self.table_right, y)

    def draw_grid(self, year, week, mtime):
        self.translate(settings.MARGIN['left'], settings.MARGIN['bottom'])
        first_day = iso_to_gregorian(year, week, 1)
        days = [first_day + datetime.timedelta(days=i) for i in range(settings.DAYS)]

        self.draw_columns()
        self.draw_rows(days)
        self.draw_title(year, week, days)
        self.setFontSize(8)
        self.drawRightString(self.width, 0 - self._fontsize - 5, mtime)

    def draw_title(self, year, week, days):
        self.setFontSize(settings.HEADERS_FONT_SIZE)
        title_height = self.height - self._fontsize
        self.drawString(0, title_height, 'Emploi du temps GB1')
        self.drawRightString(self.width, title_height, 'semaine n° {}'.format(week))
        self.drawCentredString(self.width/2., title_height, 'du {0:%d/%m/%y} au {1:%d/%m/%y}'.format(
            days[0],
            days[-1],
        ))

    def draw_rect(self, lesson, group):
        x1 = float_time(lesson.start_time)
        x2 = float_time(lesson.end_time)
        x = self.table_left + x1 * self.table_h_step
        w = (x2 - x1) * self.table_h_step

        y1 = lesson.date.isoweekday() - 1
        yy1 = group[1]
        yy2 = group[0]-1
        y = self.table_top - y1 * self.table_v_step - yy1 * self.table_vv_step
        h = (yy1 - yy2) * self.table_vv_step

        self.roundRect(x, y, w, h, settings.RECT_RADIUS, fill=True)
        return x, y, w, h

    def draw_lesson(self, lesson):
        self.setFillColor(lesson.background_color)
        self.setStrokeColorRGB(0., 0., 0.)
        for group in lesson.groups.lines:
            x, y, width, height = self.draw_rect(lesson, group)
            if group[0] == group[1]:
                sep = ' - '
            else:
                sep = '<br/>\n'
            p = platypus.Paragraph(join_filter(sep, lesson.top_left_caption), style=styles['left'])
            t = platypus.Table([[p]], colWidths=width, rowHeights=height)
            t.setStyle(styles2['top_left'])
            t.wrapOn(self, width, height)
            t.drawOn(self, x, y)
            p = platypus.Paragraph(join_filter(sep, lesson.bottom_right_caption), style=styles['right'])
            t = platypus.Table([[p]], colWidths=width, rowHeights=height)
            t.setStyle(styles2['bottom_right'])
            t.wrapOn(self, width, height)
            t.drawOn(self, x, y)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', default=settings.INPUT_FILE_DEFAULT)
    parser.add_argument('output', nargs='?', default=settings.OUTPUT_DIRECTORY_DEFAULT)
    options = parser.parse_args()

    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(options.file)).strftime('%Y/%m/%d %H:%M')
    s = Schedule(os.path.join(options.output, "2014_2015.pdf"))
    lessons = lesson.parse_file(options.file)
    d = collections.defaultdict
    for (year, week), lesson_list in sorted(lessons.items()):
        ss = Schedule(os.path.join(options.output, "S{}.pdf".format(week)))
        ss.draw_grid(year, week, mtime)
        s.draw_grid(year, week, mtime)
        for lesson in lesson_list:
            s.draw_lesson(lesson)
            ss.draw_lesson(lesson)
        ss.save()
        s.showPage()
    s.save()

