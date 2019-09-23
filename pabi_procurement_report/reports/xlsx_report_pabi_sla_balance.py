# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiSlaBalance(models.TransientModel):
    _name = 'xlsx.report.pabi.sla.balance'
    _inherit = 'xlsx.report'

    # Search Criteria
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    date_start = fields.Date(
        string='Date Start',
        required=True
    )
    date_end = fields.Date(
        string='Date End',
        required=True
    )
    org_name = fields.Char(
        string='Org Name',
    )

    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.sla.balance.results',
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

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.sla.balance.results']
        dom = [
            ('date_transfer', '>=', self.date_start),
            ('date_transfer', '<=', self.date_end),
        ]
        if self.org_ids:
            dom += [('org_id', 'in', self.org_ids._ids)]
        self.results = Result.search(dom)


class XLSXReportPabiSlaBalanceResults(models.Model):
    _name = 'xlsx.report.pabi.sla.balance.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
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
    section_id = fields.Char(
        string='Section ID',
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
    date_confirm = fields.Date(
        string='Date Confirm',
        readonly=True,
    )
    date_to_approve = fields.Date(
        string='Date to Approve',
        readonly=True,
    )
    project_id = fields.Char(
        string='Project ID',
        readonly=True,)
    

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT 
        row_number() over (order by sr.id) as id,
        sr.operating_unit_id,
        org.id as org_id,
        sr.name as sr_name,
        sec.code as section_id,
        CONCAT((SELECT value FROM ir_translation it
        Where it.res_id = hr.title_id AND
            it.name LIKE 'res.partner.title,name' LIMIT 1),
        ' ',
        (SELECT value FROM ir_translation it
        WHERE it.res_id = sr.employee_id AND
            it.name LIKE 'hr.employee,first_name' LIMIT 1),
        ' ',
        (SELECT value FROM ir_translation it
        WHERE it.res_id =  sr.employee_id AND it.name LIKE 'hr.employee,last_name' LIMIT 1) 
        ) as requester,
        prj.code as project_id,
        prj.name as project,
        --(
        --SELECT value FROM ir_translation it
        --WHERE it.res_id = (SELECT he.id FROM res_users ru
        --LEFT JOIN hr_employee he
        --ON ru.login = he.employee_code
        --LEFT JOIN res_section rs
        --ON  rs.id = he.section_id
        --WHERE ru.id = sr.employee_id  LIMIT 1) AND it.name LIKE 'res.section,name' LIMIT 1
        --) as project,
        (SELECT value FROM ir_translation it
        WHERE it.name LIKE 'res.section,name' AND it.res_id=sec.id LIMIT 1) as section,
        ou.name as requester_ou_name,
        sr.create_date as date_request,
        sr.date_approve as date_approve,
        sr.date_prepare as date_receive,
        sr.state as select_status,
        sr.date_transfer as date_transfer,
        sr.date_confirm as date_confirm,
        sr.date_confirm as date_to_approve
        FROM stock_picking sp
        LEFT JOIN stock_request sr
        ON sr.transfer_picking_id = sp.id
        LEFT JOIN res_org org
        ON sr.operating_unit_id = org.operating_unit_id
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