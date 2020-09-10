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
    org_name = fields.Char(
        string='Org',
    )
    partner_name = fields.Char(
        string='Supplier',
    )
    partner_category_name = fields.Char(
        string='Partner',
    )
    method_name = fields.Char(
        string='Method',
    )
    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.purchase.summarize.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.onchange('org_ids')
    def onchange_orgs(self):
        res = ''
        for prg in self.org_ids:
            if res != '':
                res += ', '
            res += prg.operating_unit_id.code
        self.org_name = res

    @api.onchange('partner_ids')
    def onchange_partners(self):
        res = ''
        for partner in self.partner_ids:
            if res != '':
                res += ', '
            res += partner.name
        self.partner_name = res

    @api.onchange('partner_tag_ids')
    def onchange_tags(self):
        res = ''
        for tag in self.partner_tag_ids:
            if res != '':
                res += ', '
            res += tag.name
        self.partner_category_name = res

    @api.onchange('method_ids')
    def onchange_methods(self):
        res = ''
        for method in self.method_ids:
            if res != '':
                res += ', '
            res += method.name
        self.method_name = res

    @api.model
    def _domain_to_where_str(self, domain):
        """ Helper Function for better performance """
        where_dom = [" %s %s %s " % (x[0], x[1], isinstance(x[2], basestring)
                     and "'%s'" % x[2] or x[2]) for x in domain]

        where_str = 'and'.join(where_dom)
        where_str = where_str.replace(',)', ')')
        return where_str

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.purchase.summarize.results']
        where_str = ''
        dom = [
            ('selected_po.date_order', '>=', self.date_from),
            ('selected_po.date_order', '<=', self.date_to),
        ]
        if self.partner_ids:
            dom += [('po.partner_id', 'in', self.partner_ids._ids)]
        if self.method_ids:
            dom += [('pd.purchase_method_id', 'in', self.method_ids._ids)]
        if self.org_ids:
            dom += [('ou.org_id', 'in', self.org_ids._ids)]
        if self.partner_tag_ids:
            dom += [('rfq_rpc.id', 'in', self.partner_tag_ids._ids)]
        if self.doc_state:
            dom += [('selected_po.state', '=', self.doc_state)]
        
        where_str = self._domain_to_where_str(dom)
        
        self._cr.execute("""
            select
                ou.org_id
                , po.partner_id
                , pd.id as pd_id
                , pd.name as pd_number
                , po.id as po_id
                , po.name as po_number
                , selected_po.id as selected_po_id
                , CONCAT(pt.name,' ',pd.objective) as objective
                , CONCAT(COALESCE(rfq_rpt.name || ' ',''),rfq_rp.name) as rfq_supplier
                , (CASE 
                       WHEN 
                            (
                            SELECT prl.price_subtotal
                            FROM purchase_request_line prl
                                LEFT JOIN purchase_request_purchase_requisition_line_rel linerel
                                    ON linerel.purchase_request_line_id = prl.id
                                LEFT JOIN purchase_requisition_line rql
                                    ON linerel.purchase_requisition_line_id =rql.id
                            WHERE rql.requisition_id = pd.id
                            LIMIT 1
                            ) > 500000
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
                    ELSE 0.00
                END) as amount_standard
                , po.amount_total
                , pm.name as method
                , selected_po.amount_total as rfq_amount_total
                , psr.name as reason
                , po.date_order as po_date
                , pd.purchase_method_id as method_id
                , rfq_rpc.id as partner_category_id
                , selected_po.state as doc_state
                , ou.name as ou_name
                , SUM(
                    case when atax.amount > 0.0 and atax.price_include = False
                        then ROUND((requestline.price_subtotal +
                            (atax.amount * requestline.price_subtotal))::DECIMAL, 2)
                    else
                        ROUND(requestline.price_subtotal::DECIMAL, 2)
                end) as pr_amount
                , rfq_rpc.name as partner_category_name
                , CONCAT(
                    COALESCE(tr_title.value || ' ', ''),
                    tr_fname.value,' ',tr_lname.value
                ) as responsible_name
            FROM purchase_requisition pd
                LEFT JOIN purchase_requisition_line reql ON reql.requisition_id = pd.id
                LEFT JOIN purchase_request_purchase_requisition_line_rel linerel ON reql.id = linerel.purchase_requisition_line_id
                LEFT JOIN purchase_request_line requestline ON linerel.purchase_request_line_id = requestline.id
                LEFT JOIN purchase_request_taxes_rel reqtaxes ON reqtaxes.request_line_id = requestline.id
                LEFT JOIN account_tax atax ON atax.id = reqtaxes.tax_id
                LEFT JOIN operating_unit ou ON ou.id = pd.operating_unit_id
                LEFT JOIN purchase_method pm ON pm.id = pd.purchase_method_id
                LEFT JOIN purchase_order po ON po.requisition_id = pd.id
                LEFT JOIN res_partner rp_po ON rp_po.id = po.partner_id
                LEFT JOIN purchase_type pt ON pt.id = pd.purchase_type_id
                LEFT JOIN res_users responsible_user ON responsible_user.id = po.create_uid
                LEFT JOIN hr_employee he ON he.employee_code = responsible_user.login
                LEFT JOIN ir_translation tr_title ON tr_title.res_id = he.title_id AND tr_title.name LIKE 'res.partner.title,name'
                LEFT JOIN ir_translation tr_fname ON tr_fname.res_id = he.id AND tr_fname.name LIKE 'hr.employee,first_name'
                LEFT JOIN ir_translation tr_lname ON tr_lname.res_id = he.id AND tr_lname.name LIKE 'hr.employee,last_name'
                LEFT join purchase_order selected_po ON 
                    selected_po.requisition_id = pd.id AND
                    selected_po.order_type LIKE 'purchase_order' AND
                    selected_po.state NOT LIKE 'cancel'
                LEFT JOIN res_partner rfq_rp ON rfq_rp.id = selected_po.partner_id
                LEFT JOIN res_partner_title rfq_rpt ON rfq_rpt.id = rfq_rp.title
                LEFT JOIN res_partner_category rfq_rpc on rfq_rpc. id = rfq_rp.category_id
                LEFT JOIN purchase_order rfq ON rfq.order_id = selected_po.id AND rfq.order_type = 'quotation'
                LEFT JOIN purchase_select_reason psr ON psr.id = rfq.select_reason
            WHERE po.order_id is null and %s
            GROUP BY ou.org_id, ou.name, pd.id, pd.name, po.id, po.name, pt.name, pd.objective, pm.name, po.partner_id, rp_po.vat, rp_po.taxbranch, rp_po.name, 
                po.amount_total, selected_po.partner_id, selected_po.amount_total, selected_po.id, po.date_order, he.title_id, 
                he.id, po.state, psr.name, tr_title.value, tr_fname.value, tr_lname.value, rfq_rpt.name, rfq_rp.name, rfq_rpc.id
            ORDER BY ou.name, pd.name, po.name
        """ % (where_str))
        
        summarizes = self._cr.dictfetchall()
        self.results = [Result.new(line).id for line in summarizes]


class XLSXReportPabiPurchaseSummarizeResults(models.AbstractModel):
    _name = 'xlsx.report.pabi.purchase.summarize.results'
    _description = 'Purchase Summarize Results'

    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
    )
    pd_id = fields.Many2one(
        'purchase.requisition',
        string='PD ID',
    )
    pd_number = fields.Char(
        string='PD No.',
        readonly=True,
    )
    po_id = fields.Many2one(
        'purchase.order',
        string='PO ID',
    )
    po_number = fields.Char(
        string='PO No.',
        readonly=True,
    )
    selected_po_id = fields.Many2one(
        'purchase.order',
        string='Selected PO ID',
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
    partner_category_name = fields.Char(
        string='Supplier Cat',
    )
    responsible_name = fields.Char(
        string='Responsible Name',
    )
