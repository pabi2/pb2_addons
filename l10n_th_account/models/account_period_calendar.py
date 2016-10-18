# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields


class AccountCalendaryear(models.Model):
    _name = 'account.calendaryear'
    _description = 'Show period_id in calendar year name'
    _auto = False

    name = fields.Char(
        string='Name',
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select id, to_char(date_start, 'YYYY') as name,
                id as fiscalyear_id
            from account_fiscalyear
        )""" % (self._table, ))


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
        select id,
            case when month = '01' then 'Jan-' when month = '02' then 'Feb-'
            when month = '03' then 'Mar-' when month = '04' then 'Apr-'
            when month = '05' then 'May-' when month = '06' then 'Jun-'
            when month = '07' then 'Jul-' when month = '08' then 'Jul-'
            when month = '09' then 'Sep-' when month = '10' then 'Oct-'
            when month = '11' then 'Nov-' when month = '12' then 'Dec-'
            end || year as name,
            period_id
        from
            (select id, LPAD(date_part('month', date_start)::text, 2, '0')
                as month,
            date_part('year', date_start)::text as year,
            id as period_id
            from account_period where special = false) a
        )""" % (self._table, ))
