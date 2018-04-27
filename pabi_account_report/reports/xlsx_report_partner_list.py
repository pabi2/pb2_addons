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
        dom = []
        if self.category_ids:
            dom += [('category_id', 'in',
                    self.category_ids.ids)]
        partner_ids = []
        partner_ids += self.customer_partner_ids.ids
        partner_ids += self.supplier_partner_ids.ids
        if partner_ids:
            dom += [('id', 'in', partner_ids)]
        if not self.customer and not self.supplier:
            dom += [('id', '=', 0)]  # show no result
        elif self.customer and self.supplier:  # show both
            dom += ['|', ('customer', '=', True), ('supplier', '=', True)]
        elif self.customer:
            dom += [('customer', '=', True)]
        elif self.supplier:
            dom += [('supplier', '=', True)]
        self.results = Result.search(dom)
