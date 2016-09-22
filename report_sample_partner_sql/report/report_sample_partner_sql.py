# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields


class ReportSamplePartnerSQL(models.Model):
    _name = 'report.sample.partner.sql'
    _description = 'Sample Partner List Report in SQL (pdf/xls)'
    _auto = False
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Name')
    customer = fields.Boolean('Is Customer?')
    supplier = fields.Boolean('IS Suupplier?')
    user_id = fields.Many2one('res.users', string='Salesperson')

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select rp.name, rp.customer, rp.supplier, ru.login salesperson
            from res_partner rp
            left outer join res_users ru on ru.id = rp.user_id
        )""" % (self._table, ))
