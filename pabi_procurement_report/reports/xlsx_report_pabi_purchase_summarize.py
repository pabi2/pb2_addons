# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiPurchaseSummarize(models.TransientModel):
    _name = 'xlsx.report.pabi.purchase.summarize'
    _inherit = 'xlsx.report'

    # Search Criteria
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Supplier',
    )
    partner_tag_ids = fields.Many2many(
        'res.partner.category',
        string='Supplier Type',
    )
    method_ids = fields.Many2many(
        'purchase.method',
        string='Method',
    )
    date_from = fields.Date(
        string='Date From',
        required=True,
    )
    date_to = fields.Date(
        string='Date To',
        required=True,
    )
    doc_state = fields.Selection(
        [
            ('confirmed', 'Confirmed'),
            ('draft', 'Draft'),
            ('approved', 'Released'),
            ('done', 'Done'),
        ],
        string='PO Status',
        select=True,
    )
    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.purchase.summarize.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.purchase.summarize.results']
        dom = [
            ('po_date', '>=', self.date_from),
            ('po_date', '<=', self.date_to),
        ]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids._ids)]
        if self.method_ids:
            dom += [('method_id', 'in', self.method_ids._ids)]
        if self.org_ids:
            dom += [('org_id', 'in', self.org_ids._ids)]
        if self.partner_tag_ids:
            dom += [('partner_category_id', 'in', self.partner_tag_ids._ids)]
        if self.doc_state:
            dom += [('doc_state', '=', self.doc_state)]
        self.results = Result.search(dom)


class XLSXReportPabiPurchaseSummarizeResults(models.Model):
    _name = 'xlsx.report.pabi.purchase.summarize.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
    )
    pd_number = fields.Char(
        string='PD No.',
        readonly=True,
    )
    objective = fields.Char(
        string='Objective',
        readonly=True,
    )
    rfq_supplier = fields.Char(
        string='Supplier RFQ',
        readonly=True,
    )
    po_supplier = fields.Char(
        string='Supplier PO',
        readonly=True,
    )
    amount_standard = fields.Float(
        string='Amount Standard',
        readonly=True,
    )
    amount_total = fields.Float(
        string='Amount Total',
        readonly=True,
    )
    method = fields.Char(
        string='Method',
        readonly=True,
    )
    rfq_amount_total = fields.Float(
        string='RFQ Amount Total',
        readonly=True,
    )
    reason = fields.Char(
        string='Reason',
        readonly=True,
    )
    po_date = fields.Date(
        string='Date',
        readonly=True,
    )
    method_id = fields.Many2one(
        'purchase.method',
        string='Method',
    )
    partner_category_id = fields.Many2one(
        'res.partner.category',
        string='Supplier Type',
    )
    doc_state = fields.Char(
        string='Status',
    )
    ou_name = fields.Char(
        string='OU Name',
    )
    pr_amount = fields.Float(
        string='PR Amount',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT row_number() over (order by pd.id) as id,
        po.name as pd_number,
        po.partner_id,
        pd.purchase_method_id as method_id,
        (
        SELECT id from res_org WHERE operating_unit_id = ou.id
        LIMIT 1
        ) as org_id,
        CONCAT((SELECT pt.name FROM purchase_type pt WHERE
            pt.id = pd.purchase_type_id  LIMIT 1),' ',pd.objective) objective,
        (SELECT COUNT(id) FROM purchase_requisition_line pdl
        WHERE pdl.requisition_id = pd.id LIMIT 1) qty,
        (
        CASE WHEN 
        (
        SELECT prl.price_subtotal
        FROM purchase_request_line prl
        LEFT JOIN purchase_request_purchase_requisition_line_rel linerel
        ON linerel.purchase_request_line_id = prl.id
        LEFT JOIN purchase_requisition_line rql
        ON linerel.purchase_requisition_line_id =rql.id
        WHERE rql.requisition_id = pd.id
        LIMIT 1
        ) > 100000
        THEN 
        (
        SELECT prl.price_subtotal
        FROM purchase_request_line prl
        LEFT JOIN purchase_request_purchase_requisition_line_rel linerel
        ON linerel.purchase_request_line_id = prl.id
        LEFT JOIN purchase_requisition_line rql
        ON linerel.purchase_requisition_line_id =rql.id
        WHERE rql.requisition_id = pd.id
        LIMIT 1
        )
        ELSE
        0.00
        END
        ) as amount_standard,
        selected_po.amount_total,
        pm.name as method,
        (SELECT CONCAT(COALESCE(rpt.name || ' ',''),rp.name)
            FROM res_partner rp
        LEFT JOIN res_partner_title rpt
        ON rpt.id = rp.title
        WHERE rp.id = selected_po.partner_id  LIMIT 1) as rfq_supplier,
        selected_po.amount_total as rfq_amount_total,
        (SELECT psr.name FROM purchase_order rfq
        LEFT JOIN purchase_select_reason psr ON psr.id = rfq.select_reason
        WHERE rfq.order_type = 'quotation' AND
            rfq.order_id = selected_po.id) reason,
        selected_po.date_order as po_date,
        (SELECT rpc.id 
        from res_partner_category rpc
	    LEFT JOIN res_partner rp on rp.category_id = rpc.id
	    WHERE rp.id = selected_po.partner_id
        ) as partner_category_id,
        selected_po.state as doc_state,
        ou.name as ou_name,
        (
        SELECT prl.price_subtotal
        FROM purchase_request_line prl
        LEFT JOIN purchase_request_purchase_requisition_line_rel linerel
        ON linerel.purchase_request_line_id = prl.id
        LEFT JOIN purchase_requisition_line rql
        ON linerel.purchase_requisition_line_id =rql.id
        WHERE rql.requisition_id = pd.id
        LIMIT 1
        ) as pr_amount,
        (SELECT CONCAT(COALESCE(rpt.name || ' ',''),rp.name)
            FROM res_partner rp
        LEFT JOIN res_partner_title rpt
        ON rpt.id = rp.title
        WHERE rp.id = selected_po.partner_id  LIMIT 1) as po_supplier
        FROM purchase_requisition pd
        LEFT JOIN operating_unit ou
        ON ou.id = pd.operating_unit_id
        LEFT JOIN purchase_method pm
        ON pm.id = pd.purchase_method_id
        LEFT JOIN purchase_price_range ppr
        ON ppr.id = pd.purchase_price_range_id
        LEFT JOIN purchase_order po
        ON po.requisition_id = pd.id
        LEFT join purchase_order selected_po
        ON selected_po.requisition_id = pd.id AND
            selected_po.order_type LIKE 'purchase_order' AND
            selected_po.state NOT LIKE 'cancel'
        WHERE po.order_type = 'purchase_order'
        GROUP BY pd.id, ou.id, po.name,pd.name, pd.objective, pd.amount_total, pm.name,
            selected_po.partner_id, selected_po.amount_total, po.partner_id,selected_po.date_order,
        selected_po.id
        )""" % (self._table, ))
