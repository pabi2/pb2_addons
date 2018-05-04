# -*- coding: utf-8 -*-
from openerp import models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ThaiHoliday(models.Model):

    _name = 'thai.holiday'

    @api.model
    def find_next_working_day(self, date):
        new_date = datetime.strptime(date, "%Y-%m-%d")
        # Check Weekend
        if new_date.weekday() in [5, 6]:  # Sat & Sun
            new_date = new_date.weekday() == 5 and\
                (new_date + relativedelta(days=2)) or\
                (new_date + relativedelta(days=1))
        # Check Public Holiday
        holidays = self.env['calendar.event'].search([
            ('user_id', '=', self.env.ref('base.user_holiday').id),
            ('start_date', '<=', new_date.strftime("%Y-%m-%d")),
            ('stop_date', '>=', new_date.strftime("%Y-%m-%d")),
        ])
        if holidays:
            stop_dates = []
            for holiday in holidays:
                stop_dates.append(datetime.strptime(
                    holiday.stop_date,
                    "%Y-%m-%d")
                )
            stop_date = max(stop_dates)
            new_date = stop_date + relativedelta(days=1)
        return new_date.strftime("%Y-%m-%d")

    @api.model
    def find_previous_working_day(self, date):
        new_date = datetime.strptime(date, "%Y-%m-%d")
        # Check Weekend
        if new_date.weekday() in [5, 6]:  # Sat & Sun
            new_date = new_date.weekday() == 5 and\
                (new_date - relativedelta(days=1)) or\
                (new_date - relativedelta(days=2))
        # Check Public Holiday
        holidays = self.env['calendar.event'].search([
            ('user_id', '=', self.env.ref('base.user_holiday').id),
            ('start_date', '<=', new_date.strftime("%Y-%m-%d")),
            ('stop_date', '>=', new_date.strftime("%Y-%m-%d")),
        ])
        if holidays:
            stop_dates = []
            for holiday in holidays:
                stop_dates.append(datetime.strptime(
                    holiday.stop_date,
                    "%Y-%m-%d")
                )
            stop_date = max(stop_dates)
            new_date = stop_date + relativedelta(days=1)
        return new_date.strftime("%Y-%m-%d")
