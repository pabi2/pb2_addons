# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiSupplierEvaluationScore(models.TransientModel):
    _name = 'xlsx.report.pabi.supplier.evaluation.score'
    _inherit = 'xlsx.report'

    # Search Criteria
    partner_ids = fields.Many2many(
        'res.partner',
        string='Supplier',
    )

    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.supplier.evaluation.score.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.supplier.evaluation.score.results']
        dom = []
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids._ids)]
        self.results = Result.search(dom)


class XLSXReportPabiSupplierEvaluationScoreResults(models.Model):
    _name = 'xlsx.report.pabi.supplier.evaluation.score.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        readonly=True,
    )
    partner_code = fields.Char(
        string='Partner Code',
        readonly=True,
    )
    partner_name = fields.Char(
        string='Partner',
        readonly=True,
    )
    po_count = fields.Integer(
        string='Count Order',
        readonly=True,
    )
    sum_service = fields.Integer(
        string='Sum Service',
        readonly=True,
    )
    sum_delivery = fields.Integer(
        string='Sum Delivery',
        readonly=True,
    )
    sum_quality = fields.Integer(
        string='Sum Quality',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT
	    row_number() over (order by rp.search_key) as id,
        rp.id as partner_id,
        rp.search_key as partner_code,
        concat(rpt.name,' ',rp.name) as partner_name,
        (
        SELECT COALESCE(count(wa.id), 0)
        FROM
        purchase_work_acceptance_evaluation_line wael
        left join purchase_work_acceptance_score pwas ON pwas.id = wael.score_id
        left join purchase_work_acceptance wa on wa.id = wael.acceptance_id
        left join purchase_order po on wa.order_id = po.id
        WHERE po.partner_id = rp.id
        ) as po_count,
        (
        SELECT COALESCE(sum(pwas.score), 0)
        FROM
        purchase_work_acceptance_evaluation_line wael
        left join purchase_work_acceptance_score pwas ON pwas.id = wael.score_id
        left join purchase_work_acceptance wa on wa.id = wael.acceptance_id
        left join purchase_order po on wa.order_id = po.id
        WHERE wael.case_id = 1
        AND po.partner_id = rp.id
        ) as sum_delivery,
        (
        SELECT COALESCE(sum(pwas.score), 0)
        FROM
        purchase_work_acceptance_evaluation_line wael
        left join purchase_work_acceptance_score pwas ON pwas.id = wael.score_id
        left join purchase_work_acceptance wa on wa.id = wael.acceptance_id
        left join purchase_order po on wa.order_id = po.id
        WHERE wael.case_id = 2
        AND po.partner_id = rp.id
        ) as sum_quality,
        (
        SELECT COALESCE(sum(pwas.score), 0)
        FROM
        purchase_work_acceptance_evaluation_line wael
        left join purchase_work_acceptance_score pwas ON pwas.id = wael.score_id
        left join purchase_work_acceptance wa on wa.id = wael.acceptance_id
        left join purchase_order po on wa.order_id = po.id
        WHERE wael.case_id = 3
        AND po.partner_id = rp.id
        ) as sum_service
        from res_partner rp
        left join res_partner_title rpt on rpt.id = rp.title
        where rp.employee = False
        group by rp.search_key,rpt.name,rp.name,rp.id
        )""" % (self._table, ))
