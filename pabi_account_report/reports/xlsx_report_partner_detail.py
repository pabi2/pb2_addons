from openerp import models, fields, api, tools


class XLSXReportPartnerDetail(models.TransientModel):
    _name = 'xlsx.report.partner.detail'
    _inherit = 'xlsx.report'

    # Search Criteria
    category_ids = fields.Many2many(
        'res.partner.category',
        string='Category(s)',
    )
    customer = fields.Boolean(
        string='Customer',
        default=True,
    )
    customer_partner_ids = fields.Many2many(
        'res.partner',
        'partner_detail_customer_rel',
        'report_id', 'partner_id',
        string='Partners',
        domain=[('customer', '=', True),
                '|', ('active', '=', True),
                ('active', '=', False)],
    )
    supplier = fields.Boolean(
        string='Supplier',
        default=True,
    )
    supplier_partner_ids = fields.Many2many(
        'res.partner',
        'partner_detail_supplier_rel',
        'report_id', 'partner_id',
        string='Partners',
        domain=[('supplier', '=', True),
                '|', ('active', '=', True),
                ('active', '=', False)],
    )
    active = fields.Selection(
        selection=[('true', 'True'), ('false', 'False')],
        string='Active',
    )
    # Report Result
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

    @api.one
    def _get_domain(self, partner_id):
        domain = ['|', ('active', '=', True), ('active', '=', False)]
        if self.category_ids:
            domain += [('category_id', 'in', self.category_ids.ids)]
        if self.active:
            domain += \
                [('active', '=', self.active == 'true' and True or False)]
        customer_partner_ids = self.customer_partner_ids.ids
        supplier_partner_ids = self.supplier_partner_ids.ids
        if not self.customer and not self.supplier:
            domain += [('customer', '=', False), ('supplier', '=', False)]
        elif self.customer and self.supplier:
            if not customer_partner_ids and not supplier_partner_ids:
                domain += \
                    ['|', ('customer', '=', True), ('supplier', '=', True)]
            elif customer_partner_ids and supplier_partner_ids:
                domain += ['|', (partner_id, 'in', customer_partner_ids),
                           (partner_id, 'in', supplier_partner_ids)]
            elif customer_partner_ids:
                domain += ['|', (partner_id, 'in', customer_partner_ids),
                           ('supplier', '=', True)]
            else:
                domain += ['|', (partner_id, 'in', supplier_partner_ids),
                           ('customer', '=', True)]
        elif self.customer:
            domain += [('customer', '=', True)]
            if customer_partner_ids:
                domain += [(partner_id, 'in', customer_partner_ids)]
        elif self.supplier:
            domain += [('supplier', '=', True)]
            if supplier_partner_ids:
                domain += [(partner_id, 'in', supplier_partner_ids)]
        return domain

    @api.one
    def _compute_results(self):
        self.partner_detail_results = \
            self.env['res.partner'].search(self._get_domain('id'), order="id")
        self.partner_bank_detail_results = \
            self.env['res.partner.view'] \
                .search(self._get_domain('partner_id'), order="id")


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
