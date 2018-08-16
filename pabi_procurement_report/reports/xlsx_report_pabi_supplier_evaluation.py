# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiSupplierEvaluation(models.TransientModel):
    _name = 'xlsx.report.pabi.supplier.evaluation'
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

    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.supplier.evaluation.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.supplier.evaluation.results']
        dom = []
        if self.partner_id:
            dom += [('partner_id', '=', self.partner_id.id)]
        self.results = Result.search(dom)


class XLSXReportPabiSupplierEvaluationResults(models.Model):
    _name = 'xlsx.report.pabi.supplier.evaluation.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    partner_code = fields.Char(
        string='Partner Code',
        readonly=True,
    )
    partner_name = fields.Char(
        string='Partner',
        readonly=True,
    )
    wa_no = fields.Char(
        string='Material Doc',
        readonly=True,
    )
    po_no = fields.Char(
        string='Purchase Order',
        readonly=True,
    )
    date_contract_end = fields.Date(
        string='Contract End Date',
        readonly=True,
    )
    date_receive = fields.Date(
        string='Receive Date',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    eval_service = fields.Char(
        string='Service',
        readonly=True,
    )
    eval_quality = fields.Char(
        string='Quality',
        readonly=True,
    )
    eval_receiving = fields.Char(
        string='Receiving',
        readonly=True,
    )
    delay_day = fields.Integer(
        string='Delay Day',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT 
        row_number() over (order by wa.id) as id,
        rp.search_key as partner_code,
        concat(rpt.name,' ',rp.name) as partner_name,
        rp.id as partner_id,
        po.name as po_no,
        wa.name as wa_no,
        wa.date_contract_end,
        wa.date_receive,
        (
        SELECT pwas.score
        FROM
        purchase_work_acceptance_evaluation_line wael
        left join purchase_work_acceptance_score pwas
        ON pwas.id = wael.score_id
        left join purchase_work_acceptance_case pwac
        ON pwac.id = wael.case_id
        WHERE wael.case_id = 1
        AND wael.acceptance_id = wa.id
        LIMIT 1
        ) as eval_receiving,
        (
        SELECT pwas.score
        FROM
        purchase_work_acceptance_evaluation_line wael
        left join purchase_work_acceptance_score pwas
        ON pwas.id = wael.score_id
        left join purchase_work_acceptance_case pwac
        ON pwac.id = wael.case_id
        WHERE wael.case_id = 3
        AND wael.acceptance_id = wa.id
        LIMIT 1
        ) as eval_service,
        (
        SELECT pwas.score
        FROM
        purchase_work_acceptance_evaluation_line wael
        left join purchase_work_acceptance_score pwas
        ON pwas.id = wael.score_id
        left join purchase_work_acceptance_case pwac
        ON pwac.id = wael.case_id
        WHERE wael.case_id = 2
        AND wael.acceptance_id = wa.id
        LIMIT 1
        ) as eval_quality,
        case
        when (-1 * DATE_PART('day', wa.date_contract_end ::timestamp -
            wa.date_receive::timestamp)) > 0
        then
        -1 * DATE_PART('day', wa.date_contract_end ::timestamp -
            wa.date_receive::timestamp)
        else
        0
        end
        as delay_day,
        org_id as org_id
        from purchase_work_acceptance wa
        left join purchase_order po on po.id = wa.order_id
        left join operating_unit ou on ou.id = po.operating_unit_id
        left join res_org org on org.operating_unit_id = ou.id
        left join res_partner rp on rp.id = po. partner_id
        left join res_partner_title rpt on rpt.id = rp.title
        )""" % (self._table, ))
