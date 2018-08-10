# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiSlaBalance(models.TransientModel):
    _name = 'xlsx.report.pabi.sla.balance'
    _inherit = 'xlsx.report'

    # Search Criteria
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    select_status = fields.Selection(
        [
            ('done', 'Done'),
            ('cancel', 'Cancel'),
        ],
        string='Status',
    )

    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.sla.balance.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.sla.balance.results']
        dom = []
        print self.select_status
        if self.operating_unit_id:
            dom += [('operating_unit_id', '=', self.operating_unit_id.id)]
        if self.select_status:
            dom += [('select_status', '=', self.select_status)]
        self.results = Result.search(dom)


class XLSXReportPabiSlaBalanceResults(models.Model):
    _name = 'xlsx.report.pabi.sla.balance.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    requester_ou_name = fields.Char(
        string='OU Name',
        readonly=True,
    )
    requester = fields.Char(
        string='Requester',
        readonly=True,
    )
    sr_name = fields.Char(
        string='Requester',
        readonly=True,
    )
    project = fields.Char(
        string='Project',
        readonly=True,
    )
    section = fields.Char(
        string='Section',
        readonly=True,
    )
    select_status = fields.Char(
        string='Status',
        readonly=True,
    )
    date_request = fields.Date(
        string='Date Request',
        readonly=True,
    )
    date_approve = fields.Date(
        string='Date Approve',
        readonly=True,
    )
    date_receive = fields.Date(
        string='Date Receive',
        readonly=True,
    )
    date_transfer = fields.Date(
        string='Date Transfer',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
       SELECT 
        row_number() over (order by sr.id) as id,
        sr.operating_unit_id,
        sr.name as sr_name,
        CONCAT(
        COALESCE((SELECT value FROM ir_translation it
        WHERE it.res_id = (SELECT rpt.id FROM res_users ru
        LEFT JOIN hr_employee he
        ON ru.login = he.employee_code
        LEFT JOIN res_partner_title rpt
        ON rpt.id = he.title_id
        WHERE ru.id = sr.employee_id LIMIT 1) AND
            it.name LIKE 'res.partner.title,name') || ' ', ''),
        (SELECT value FROM ir_translation it
        WHERE it.res_id = (SELECT he.id FROM res_users ru
        LEFT JOIN hr_employee he
        ON ru.login = he.employee_code
        WHERE ru.id = sr.employee_id) AND
            it.name LIKE 'hr.employee,first_name' LIMIT 1),
        ' ',
        (SELECT value FROM ir_translation it
        WHERE it.res_id = (SELECT he.id FROM res_users ru
        LEFT JOIN hr_employee he
        ON ru.login = he.employee_code
        WHERE ru.id = sr.employee_id) AND it.name LIKE 'hr.employee,last_name' LIMIT 1) 
        ) as requester,
        prj.name as project,
        sec.name as section,
        ou.name as requester_ou_name,
        sr.create_date as date_request,
        sp.create_date as date_approve,
        sp.date_done as date_receive,
        sr.state as select_status,
        (CASE WHEN sr.state = 'done'
        THEN
        sr.write_date
        ELSE
        Null
        END) as date_transfer
        FROM stock_picking sp
        LEFT JOIN stock_request sr
        ON sr.transfer_picking_id = sp.id
        LEFT JOIN res_project prj
        ON sr.project_id = prj.id
        LEFT JOIN res_section sec
        ON sr.section_id = sec.id
        LEFT JOIN operating_unit ou
        ON sr.operating_unit_id = ou.id
        LEFT JOIN hr_employee hr
        ON sr.prepare_emp_id = hr.id
        LEFT JOIN res_partner_title rt
        ON rt.id = hr.title_id
        )""" % (self._table, ))