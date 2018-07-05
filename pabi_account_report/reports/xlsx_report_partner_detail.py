# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


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
            FROM res_partner_bank rpb
            LEFT JOIN res_partner rp ON rpb.partner_id = rp.id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportPartnerDetail(models.TransientModel):
    _name = 'xlsx.report.partner.detail'
    _inherit = 'report.account.common'

    category_ids = fields.Many2many(
        'res.partner.category',
        string='Categories',
    )
    active = fields.Selection(
        selection=[('true', 'True'), ('false', 'False')],
        string='Active',
    )
    partner_type = fields.Selection(
        [('customer', 'Customer'),
         ('supplier', 'Supplier'),
         ('customer_and_supplier', 'Customer and Supplier'),
         ('customer_or_supplier', 'Customer or Supplier')],
        string='Partner\'s',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
    )
    partner_detail_results = fields.Many2many(
        'res.partner',
        string='Partner Detail Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    partner_bank_account_detail_results = fields.Many2many(
        'res.partner.view',
        string='Partner Bank Acccount Detail Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _get_domain(self):
        self.ensure_one()
        domain = ['|', ('active', '=', True), ('active', '=', False)]
        # Check active
        if self.active == 'true':
            domain += [('active', '=', True)]
        elif self.active == 'false':
            domain += [('active', '=', False)]
        # Check partner type
        if self.partner_type == 'customer_or_supplier':
            domain += ['|', ('customer', '=', True), ('supplier', '=', True)]
        elif self.partner_type == 'customer_and_supplier':
            domain += [('customer', '=', True), ('supplier', '=', True)]
        elif self.partner_type == 'customer':
            domain += [('customer', '=', True)]
        elif self.partner_type == 'supplier':
            domain += [('supplier', '=', True)]
        # Check category
        if self.category_ids:
            domain += [('category_id', 'in', self.category_ids.ids)]
        return domain

    @api.onchange('partner_type', 'active', 'category_ids')
    def _onchange_partner_type(self):
        return {'domain': {'partner_ids': self._get_domain()}}

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Partner = self.env['res.partner']
        PartnerView = self.env['res.partner.view']
        partner_domain = self._get_domain()
        partner_view_domain = self._get_domain()
        # Check Partner
        if self.partner_ids:
            partner_domain += [('id', 'in', self.partner_ids.ids)]
            partner_view_domain += [('partner_id', 'in', self.partner_ids.ids)]
        # --
        self.partner_detail_results = Partner.search(partner_domain,
                                                     order="id")
        self.partner_bank_account_detail_results = \
            PartnerView.search(partner_view_domain, order="partner_id")
