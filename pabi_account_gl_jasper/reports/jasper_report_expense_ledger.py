# -*- coding: utf-8 -*-
from openerp import models, fields, api


class JasperReportExpenseLedger(models.TransientModel):
    _name = 'jasper.report.expense.ledger'
    _inherit = 'report.account.common'

    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
    )
    line_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    chartfield_ids = fields.Many2many(
        'chartfield.view',
        string='Budget',
        domain=['|',('active', '=', False),('active', '=', True),('model', '!=', 'res.personnel.costcenter')],
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
    )
    count_chartfield = fields.Integer(
        compute='_compute_count_chartfield',
        string='Budget Count',
    )
    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
    )
    operating_unit_ids = fields.Many2one(
        'operating.unit',
        string='Org',
    )
    user_type = fields.Many2one(
        'account.account.type',
        string='Account Type',
        #default=lambda self: self.env.ref('account.data_account_type_expense'),
    )
    results = fields.Many2many(
        'account.move.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    @api.depends('chartfield_ids')
    def _compute_count_chartfield(self):
        for rec in self:
            rec.count_chartfield = len(rec.chartfield_ids)

    @api.onchange('operating_unit_ids')
    def onchange_org(self):
        domain_acc = []
        domain_partner = []
        if self.operating_unit_ids:
            domain_acc += [('company_id', '=', self.company_id.ids), '|', ('user_type.code', 'in', ('Expense', 'Allocation')), ('code', 'like', '5%')]
            domain_partner += [('company_id', '=', self.company_id.ids), ('supplier', '=', True), ('user_id.default_operating_unit_id', 'in', self.operating_unit_ids.ids)]
            return {'domain': {'account_ids': domain_acc, 'partner_ids': domain_partner}}

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get from account.move.line
        2. Check account type is expense
        """
        self.ensure_one()
        Result = self.env['account.move.line']
        dom = []
        
        if self.user_type:
            dom += [(" aa.user_type = {} ".format(self.account_type_id.id))]
        if self.account_ids:
            dom += [(' aml.account_id in ({}) '.\
                     format(','.join(map(str, (self.account_ids.ids)))))]
        if self.operating_unit_ids:
            dom += [(' aml.org_id in ({}) '.\
                     format(','.join(map(str, (self.operating_unit_ids.ids)))))]
        else :
            accountant_id = 33
            if not(accountant_id in self.env.user.groups_id.ids): #group_user != Accountant                                                  
                if ('Operating Unit Budget' in [g.name for g in self.env.user.groups_id]): 
                    if not('Cooperate Budget' in [g.name for g in self.env.user.groups_id]):       
                        dom += [(' ou.id in ({}) '.\
                                 format(','.join(map(str, (self.env.user.operating_unit_ids.ids)))))]
        if self.chartfield_ids:
            # map beetween chartfield_id with chartfield type
            chartfields = [('section_id', 'sc:'),
                           ('project_id', 'pj:'),
                           ('invest_construction_phase_id', 'cp:'),
                           ('invest_asset_id', 'ia:'),
                           ('personnel_costcenter_id', 'pc:')]
            where_str = ''
            res_ids = []
            for chartfield_id, chartfield_type in chartfields:
                chartfield_ids = self.chartfield_ids.filtered(
                    lambda l: l.type == chartfield_type).mapped('res_id')
                if chartfield_ids:
                    if where_str:
                        where_str += ' or '
                    where_str += chartfield_id + ' in %s'
                    res_ids.append(tuple(chartfield_ids))
            if res_ids:
                sql = "select id from account_move_line where " + where_str
                self._cr.execute(sql, res_ids)
                aml_id = map(lambda l: l[0], self._cr.fetchall())
                dom += [(' aml.id in ({}) '.format(','.join(map(str, (aml_id)))))]
        if self.partner_ids:
            dom += [(' aml.partner_id in ({}) '.\
                     format(','.join(map(str, (self.partner_ids.ids)))))]
        if self.charge_type:
            dom += [(" aml.charge_type = '{}' ".format(self.charge_type))]
        if self.fiscalyear_start_id:
            date_start = self.fiscalyear_start_id.date_start
        if self.fiscalyear_end_id:
            date_end = self.fiscalyear_end_id.date_stop
        if self.period_start_id:
            date_start = self.period_start_id.date_start
        if self.period_end_id:
            date_end = self.period_end_id.date_stop
        if self.date_start:
            date_start = self.date_start
        if self.date_end:
            date_end = self.date_end
        return dom,date_start,date_end

    @api.onchange('line_filter')
    def _onchange_line_filter(self):
        self.chartfield_ids = []
        Chartfield = self.env['chartfield.view']
        dom = []
        if self.line_filter:
            codes = self.line_filter.split('\n')
            codes = [x.strip() for x in codes]
            codes = ','.join(codes)
            dom.append(('code', 'ilike', codes))
            self.chartfield_ids = Chartfield.search(dom, order='id')
            
    @api.multi
    def start_report(self):
        self.ensure_one()
        dom,date_start,date_end = self._compute_results()
        params = {}
        params['date_start'] = date_start
        params['date_end'] = date_end
        params['condition'] = 'and'.join(map(str, dom))
        return { 
            'type': 'ir.actions.report.xml',
            'report_name': 'report_journal_document_entry',
            'datas': params,
        }
