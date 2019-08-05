# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiComparisonPrPo(models.TransientModel):
    _name = 'xlsx.report.pabi.comparison.pr.po'
    _inherit = 'xlsx.report'

    # Search Criteria
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    date_start = fields.Date(
        string='PR Create Date',
        required=True,
    )
    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.comparison.pr.po.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.comparison.pr.po.results']
        dom = []
        if self.partner_id:
            dom += [('partner_id', '=', self.partner_id.id)]
        if self.org_ids:
            dom += [('org_id', 'in', self.org_ids._ids)]
        self.results = Result.search(dom)


class XLSXReportPabiComparisonPrPoResults(models.Model):
    _name = 'xlsx.report.pabi.comparison.pr.po.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    partner_name = fields.Char(
        string='Partner',
        readonly=True,
    )
    partner_code = fields.Char(
        string='Partner Code',
        readonly=True,
    )
    pr_header = fields.Char(
        string='Header',
        readonly=True,
    )
    pr_name = fields.Char(
        string='PR',
        readonly=True,
    )
    date_start = fields.Date(
        readonly=True,
    )
    po_name = fields.Char(
        string='PO',
        readonly=True,
    )
    pr_total = fields.Float(
        string='PR Total',
        readonly=True,
    )
    po_tax = fields.Float(
        string='PO VAT',
        readonly=True,
    )
    po_no_vat = fields.Float(
        string='PO Amount No Vat',
        readonly=True,
    )
    po_vat = fields.Float(
        string='PO Total',
        readonly=True,
    )
    diff = fields.Float(
        string='Diff',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    org_id = fields.Many2one(
        'res.org',
        string='org',
    )
    ou_name = fields.Char(
        string='OU',
    )
    

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select
            pr.id as id,
            prl.name as pr_header,
            pr.name as pr_name,
            pr.date_start,  
            prl.price_subtotal as pr_total,
            pol.name,
            po.name as po_name,
            po.partner_id as partner_id,
            rp.name as partner_name,
            rp.search_key as partner_code,
            coalesce(
            (pol.price_unit * pol.product_qty),
             0.00
             )  as po_vat,
            coalesce(
            at.amount * (pol.price_unit * pol.product_qty),
            0.00
            ) as po_tax,
            coalesce(
            (pol.price_unit * pol.product_qty) -
            (at.amount * (pol.price_unit * pol.product_qty)),
             coalesce((pol.price_unit * pol.product_qty), 0.00)
             ) as po_no_vat,
            coalesce(
            (pol.price_unit * pol.product_qty) - prl.price_subtotal,
             0.00
             )  as diff,
            ou.name as ou_name,
            org.id as org_id
            from purchase_request_line prl
            left join purchase_request pr on pr.id = prl.request_id
            left join purchase_request_purchase_order_line_rel prpolr
            on prpolr.purchase_request_line_id = prl.id
            left join purchase_order_line pol
            on prpolr.purchase_order_line_id = pol.id
            left join purchase_order_taxe pot
            on pot.ord_id = pol.id
            left join account_tax at
            on pot.tax_id = at.id
            left join purchase_order po
            on pol.order_id = po.id
            left join operating_unit ou
            on ou.id = po.operating_unit_id
            left join res_org org
            on org.operating_unit_id = ou.id
            left join res_partner rp
            on rp.id = po.partner_id
            where po.state in ('purchase_order','done')
            order by pr_name,po_name
        )""" % (self._table, ))
