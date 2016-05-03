# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ThaiHoliday(models.Model):

    _name = 'thai.holiday'
    
    @api.model
    def find_next_working_day(self, date):
        new_date = datetime.strptime(date, "%Y-%m-%d")
        # Check Weekend
        if new_date.weekday() in [5,6]: # Sat & Sun
            new_date = new_date.weekday() == 5 and\
                (new_date + relativedelta(days=2)) or\
                (new_date + relativedelta(days=1))
        # Check Public Holiday
        holidays = self.env['calendar.event'].search([
                        ('user_id','=',self.env.ref('base.user_holiday').id),
                        ('start_date','<=',new_date.strftime("%Y-%m-%d")),
                        ('stop_date','>=',new_date.strftime("%Y-%m-%d"))
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
