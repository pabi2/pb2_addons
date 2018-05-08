from openerp import models, fields, api


class XLSXReporPartnerList(models.TransientModel):
    _name = 'xlsx.report.partner.list'
    _inherit = 'xlsx.report'

    # Search Criteria
    category_ids = fields.Many2many(
        'res.partner.category',
        string='Category',
    )
    customer = fields.Boolean(
        string='Customer',
        default=True,
    )
    customer_partner_ids = fields.Many2many(
        'res.partner',
        'partner_list_customer_rel',
        'report_id', 'partner_id',
        string='Partners',
        domain=[('customer', '=', True)],
    )
    supplier = fields.Boolean(
        string='Supplier',
        default=True,
    )
    supplier_partner_ids = fields.Many2many(
        'res.partner',
        'partner_list_supplier_rel',
        'report_id', 'partner_id',
        string='Partners',
        domain=[('supplier', '=', True)],
    )
    active = fields.Selection(
        selection=[
            ('true', 'True'),
            ('false', 'False'),
        ],
        string='Active',
    )
    # Report Result
    results = fields.Many2many(
        'res.partner',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['res.partner']
        dom = ['|', ('active', '=', True), ('active', '=', False)]
        if self.category_ids:
            dom += [('category_id', 'in', self.category_ids.ids)]
        if self.active:
            dom += [('active', '=', self.active == 'true' and True or False)]
        customer_partner_ids = self.customer_partner_ids.ids
        supplier_partner_ids = self.supplier_partner_ids.ids
        if not self.customer and not self.supplier:
            dom += [('id', '=', 0)]  # Show no result
        elif self.customer and self.supplier:
            if not self.customer_partner_ids and not self.supplier_partner_ids:
                dom += ['|', ('customer', '=', True), ('supplier', '=', True)]
            elif self.customer_partner_ids and self.supplier_partner_ids:
                dom += ['|', ('id', 'in', customer_partner_ids),
                        ('id', 'in', supplier_partner_ids)]
            elif self.customer_partner_ids:
                dom += ['|', ('id', 'in', customer_partner_ids),
                        ('supplier', '=', True)]
            else:
                dom += ['|', ('id', 'in', supplier_partner_ids),
                        ('customer', '=', True)]
        elif self.customer:
            dom += [('customer', '=', True)]
            if self.customer_partner_ids:
                dom += [('id', 'in', customer_partner_ids)]
        elif self.supplier:
            dom += [('supplier', '=', True)]
            if self.supplier_partner_ids:
                dom += [('id', 'in', supplier_partner_ids)]
        self.results = Result.search(dom)
