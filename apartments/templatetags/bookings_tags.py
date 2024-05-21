from calendar import HTMLCalendar
from django import template
from datetime import date
from itertools import groupby

from django.utils.html import conditional_escape as esc

register = template.Library()


@register.filter()
def to_grid_col_start(value):
    return f'grid-column-start: {value + 1};'

def do_bookings_calendar(parser, token):
    """
    The template tag's syntax is {% bookings_calendar year month bookings_list %}
    """

    try:
        tag_name, year, month, bookings_list = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires three arguments" % token.contents.split()[0])
    return BookingsCalendarNode(year, month, bookings_list)


class BookingsCalendarNode(template.Node):
    """
    Process a particular node in the template. Fail silently.
    """

    def __init__(self, year, month, bookings_list):
        try:
            self.year = template.Variable(year)
            self.month = template.Variable(month)
            self.bookings_list = template.Variable(bookings_list)
        except ValueError:
            raise template.TemplateSyntaxError

    def render(self, context):
        try:
            # Get the variables from the context so the method is thread-safe.
            my_bookings_list = self.bookings_list.resolve(context)
            my_year = self.year.resolve(context)
            my_month = self.month.resolve(context)
            cal = BookingsCalendar(my_bookings_list)
            return cal.formatmonth(int(my_year), int(my_month))
        except ValueError:
            return
        except template.VariableDoesNotExist:
            return


class BookingsCalendar(HTMLCalendar):
    """
    Overload Python's calendar.HTMLCalendar to add the appropriate bookings to
    each day's table cell.
    """

    def __init__(self, bookings):
        super(BookingsCalendar, self).__init__()
        self.bookings = self.group_by_day(bookings)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.bookings:
                cssclass += ' booked'

                return self.day_cell(cssclass, '<span class="dayNumber">%d</span> %s' % (day))
            return self.day_cell(cssclass, '<span class="dayNumberNobookings">%d</span>' % (day))
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(BookingsCalendar, self).formatmonth(year, month)

    def group_by_day(self, bookings):
        field = lambda bookings: bookings.date_and_time.day
        return dict(
            [(day, list(items)) for day, items in groupby(bookings, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)

# Register the template tag so it is available to templates
register.tag("bookings_calendar", do_bookings_calendar)