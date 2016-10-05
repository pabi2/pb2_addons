# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields


class AccountPeriodCalendar(models.Model):
    _name = 'account.period.calendar'
    _description = 'Show period_id in calendar year name'
    _auto = False

    name = fields.Char(
        string='Name',
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select id, LPAD(date_part('month', date_start)::text, 2, '0') ||
                '/' || date_part('year', date_start)::text as name,
                id as period_id
            from account_period where special = false
        )""" % (self._table, ))
