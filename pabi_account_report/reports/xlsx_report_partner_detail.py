# -*- coding: utf-8 -*
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
        string='Category(s)',
    )
    active = fields.Selection(
        selection=[('true', 'True'), ('false', 'False')],
        string='Active',
        default='true',
    )
    partner_type = fields.Selection(
        [('customer_type', 'Customer'),
         ('supplier_type', 'Supplier'),
         ('all', 'Customer and Supplier')],
        string='Partner\'s',
        default='all',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partner(s)',
    )
    partner_detail_results = fields.Many2many(
        'res.partner',
        string='Partner Detail Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    partner_bank_detail_results = fields.Many2many(
        'res.partner.view',
        string='Partner Bank Detail Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _get_domain(self, partner_id):
        self.ensure_one()
        domain = ['|', ('active', '=', True), ('active', '=', False)]
        if self.category_ids:
            domain += [('category_id', 'in', self.category_ids.ids)]
        if self.active:
            domain += \
                [('active', '=', self.active == 'true' and True or False)]
        if self.partner_ids:
            domain += [(partner_id, 'in', self.partner_ids.ids)]
        return domain

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        self.partner_detail_results = \
            self.env['res.partner'].search(self._get_domain('id'), order="id")
        self.partner_bank_detail_results = \
            self.env['res.partner.view'] \
                .search(self._get_domain('partner_id'), order="partner_id")

    @api.onchange('partner_type', 'active')
    def _onchange_partner_type(self):
        res = {'partner_ids': []}
        domain = []
        if self.active == 'false':
            if self.partner_type == 'customer_type':
                domain = [('customer', '=', True), ('active', '=', False)]
            if self.partner_type == 'supplier_type':
                domain = [('supplier', '=', True), ('active', '=', False)]
            if self.partner_type == 'all':
                domain = [('customer', '=', True), ('supplier', '=', True),
                          ('active', '=', False)]
        elif self.active == 'true':
            if self.partner_type == 'customer_type':
                domain = [('customer', '=', True), ('active', '=', True)]
            if self.partner_type == 'supplier_type':
                domain = [('supplier', '=', True), ('active', '=', True)]
            if self.partner_type == 'all':
                domain = [('customer', '=', True), ('supplier', '=', True),
                          ('active', '=', True)]
        else:
            if self.partner_type == 'customer_type':
                domain = [('customer', '=', True), '|',
                          ('active', '=', True), ('active', '=', False)]
            if self.partner_type == 'supplier_type':
                domain = [('supplier', '=', True), '|',
                          ('active', '=', True), ('active', '=', False)]
            if self.partner_type == 'all':
                domain = [('customer', '=', True), ('supplier', '=', True),
                          '|', ('active', '=', True), ('active', '=', False)]
        res['partner_ids'] = domain
        return {'domain': res}
