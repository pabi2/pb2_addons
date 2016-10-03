# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields


class ReportSamplePartnerORM(models.Model):
    _name = 'report.sample.partner.orm'
    _description = 'Sample Partner List Report in ORM (pdf/xls)'
    _auto = False
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Name')
    customer = fields.Boolean('Is Customer?')
    supplier = fields.Boolean('IS Suupplier?')
    user_id = fields.Many2one('res.users', string='Salesperson')

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select id, id as partner_id, customer, supplier, user_id
            from res_partner
        )""" % (self._table, ))
