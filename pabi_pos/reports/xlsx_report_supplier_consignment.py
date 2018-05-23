from openerp import models, fields, api


class XLSXReportSupplierConsignment(models.TransientModel):
    _name = 'xlsx.report.supplier.consignment'
    _inherit = 'xlsx.report'

    # Search Criteria
    consign_partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        domain=lambda self: self._domain_consign_partner(),
    )
    workflow_process_ids = fields.Many2many(
        'sale.workflow.process',
        'supplier_consign_rpt_workflow_process_rel',
        'report_id', 'workflow_process_id',
        string='Sales Location',
    )
    date_from = fields.Date(
        string='From Date',
        required=True,
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
    )
    # Report Result
    results = fields.Many2many(
        'sale.order.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.model
    def _domain_consign_partner(self):
        products = self.env['product.template'].search([('consign_partner_id',
                                                         '!=', False)])
        domain = [('id', 'in', products.mapped('consign_partner_id').ids)]
        return domain

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        domain = [
            ('order_id.date_order', '>=', self.date_from),
            ('order_id.date_order', '<=', self.date_to),
            ('product_id.consign_partner_id', '=', self.consign_partner_id.id),
        ]
        if self.workflow_process_ids:
            domain += [('order_id.workflow_process_id', 'in',
                        self.workflow_process_ids.ids)]
        self.results = self.env['sale.order.line'].\
            search(domain, order='order_id')
