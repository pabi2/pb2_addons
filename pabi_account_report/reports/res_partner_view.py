# -*- coding: utf-8 -*
from openerp import models, fields
from openerp import tools


class ResPartnerView(models.Model):
    _name = 'res.partner.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
    )
    bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank',
        readonly=True,
    )
    category_id = fields.Many2one(
        'res.partner.category',
        string='Category',
        readonly=True,
    )
    active = fields.Boolean(
        string='Active',
        readonly=True,
    )
    customer = fields.Boolean(
        string='Customer',
        readonly=True,
    )
    supplier = fields.Boolean(
        string='Supplier',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY rpb.id) AS id,
                   rp.id AS partner_id, rpb.id AS bank_id, rp.category_id,
                   rp.active, rp.customer, rp.supplier
            FROM res_partner rp
            LEFT JOIN res_partner_bank rpb ON rp.id = rpb.partner_id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
