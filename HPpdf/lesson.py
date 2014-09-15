import configparser
import csv
import datetime
import collections
import functools
import logging
import operator
import re

from reportlab.lib import colors

import settings
import group_config


logger = logging.getLogger()


class ParseError(Exception):
    def __init__(self, field, arg):
        self.field = field
        self.arg = arg


def parse_date(date):
    """date format is 'DD/MM/YYYY'"""
    try:
        day = int(date[0:2])
        month = int(date[3:5])
        year = int(date[6:10])
        return datetime.date(year, month, day)
    except Exception:
        raise ParseError('date', date)


def parse_time(time):
    """time format is 'HHhMM'"""
    try:
        hour = int(time[0:2])
        minute = int(time[3:5])
        return datetime.time(hour, minute)
    except Exception:
        raise ParseError('time', time)


teacher_pattern = re.compile(r'(?P<last_name>(?:(?:M\.)|(?:Mme)) [A-Z \-]+) (?P<first_name>(?:[A-Z]?[a-z \-]*)+)')


def parse_teacher(teacher):
    """teacher format is "M./Mme LASTNAME Firstname"""
    match = teacher_pattern.match(teacher)
    if not match:
        raise ParseError('teacher', teacher)
    return match.groupdict()


def parse_teachers(teachers):
    if not teachers:
        logger.warning('No teacher')
        return []
    return [parse_teacher(teacher) for teacher in teachers.split(', ')]


def lines_add(lines1, lines2):
    l1 = list(lines1)
    l2 = list(lines2)
    lines = []
    while l1 and l2:
        x1, y1 = l1.pop()
        x2, y2 = l2.pop()
        if y1+1 < x2:
            lines.append((x2, y2))
            l1.append((x1, y1))
        elif y2+1 < x1:
            lines.append((x1, y1))
            l2.append((x2, y2))
        else:
            y = max(y1, y2)
            x = min(x1, x2)
            if x1 < x2:
                l1.append((x, y))
            elif x2 < x1:
                l2.append((x, y))
            else:
                lines.append((x, y))
    return l1 + l2 + list(reversed(lines))


def lines_union(groups):
    return functools.reduce(lines_add, groups)


def parse_groups(groups):
    names = []
    lines = []
    for group in groups.split(', '):
        try:
            g = group_config.CONFIG[group]
        except KeyError:
            raise ParseError('group', group)
        else:
            names.append(g.name)
            lines.append(g.lines)
    return group_config.Group('-'.join(names), lines_union(lines))


def join_filter(sep, args):
    return sep.join(filter(None, args))


class Lesson:
    TYPE_COLOR = {k: colors.HexColor(v) for k, v in settings.TYPE_LESSON_COLOR.items()}
    DEFAULT_TYPE_COLOR = colors.HexColor(settings.DEFAULT_TYPE_LESSON_COLOR)

    def __init__(self, t, group_config):
        self.title = t[0]
        self.date = parse_date(t[1])
        self.start_time = parse_time(t[2])
        self.end_time = parse_time(t[3])
        self.type = t[4]
        self.orig_groups = t[5]
        self.groups = parse_groups(t[5])
        self.room = t[6]
        self.memo = t[7]
        self.teachers = parse_teachers(t[8])
        self.number = 0

    @property
    def iso_year_week(self):
        return self.date.isocalendar()[:2]

    @property
    def background_color(self):
        return self.TYPE_COLOR.get(self.type, self.DEFAULT_TYPE_COLOR)

    @property
    def top_left_caption(self):
        yield self.room
        yield self.groups.name
        if self.type == 'CM':
            yield ', '.join(t['last_name'] for t in self.teachers)


    @property
    def bottom_right_caption(self):
        if self.type == 'CM':
            yield 'n°{}'.format(self.number)
        yield self.title
        yield self.memo

    @property
    def sort_key(self):
        return self.groups.lines[0][0] - self.groups.lines[-1][1]


def in_date(min_date, max_date, lesson):
    return (min_date is None or min_date <= lesson.date) and \
           (max_date is None or lesson.date <= max_date)


def parse_file(filename):
    d = collections.defaultdict(lambda: [])
    cms = collections.defaultdict(lambda: [])
    with open(filename, 'r') as fd:
        rd = csv.reader(fd, delimiter=';')
        for i, line in enumerate(rd):
            try:
                lesson = Lesson(line, group_config)
            except ParseError as e:
                logger.error('Parse error line {} - {} "{}" - {}'.format(i, e.field, e.arg, ';'.join(line)))
            else:
                d[lesson.iso_year_week].append(lesson)
                if lesson.type == 'CM':
                    cms[lesson.title].append(lesson)
    for lessons in cms.values():
        for i, lesson in enumerate(sorted(lessons, key=operator.attrgetter('date')), start=1):
            lesson.number = i
    for val in d.values():
        val.sort(key=lambda x: x.sort_key)
    return d


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    options = parser.parse_args()
    parse_file(options.file)
