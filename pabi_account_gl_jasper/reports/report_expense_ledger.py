# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ReportExpenseLedger(models.TransientModel):
    _name = 'report.expense.ledger'
    _inherit = 'report.account.gl.common'

    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
    )
    operating_unit_ids = fields.Many2one(
        'operating.unit',
        string='Org',
    )
    user_type = fields.Many2one(
        'account.account.type',
        string='Account Type',
    )

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
        dom_str = ''
        
        if self.user_type:
            dom = [('acct.id', '=', self.user_type.id)]
            dom_str += "{'user_type':%s}," % self.user_type.name
        if self.account_ids:
            dom += [('acc.id', 'in', self.account_ids.ids)]
            acc = [x.code for x in self.account_ids]
            dom_str += "{'account_ids':%s}," % ','.join(acc)
        if self.operating_unit_ids:
            dom += [('acc_ou.id', 'in', self.operating_unit_ids.ids)]
            dom += [('de_ou.id', 'in', self.operating_unit_ids.ids)]
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
                dom += [('aml.id', 'in', map(lambda l: l[0], self._cr.fetchall()))]
            chartf = [x.code for x in self.chartfield_ids]
            dom_str += "{'chartfield_ids':%s}," % ','.join(chartf)
        if self.partner_ids:
            dom += [('aml.partner_id', 'in', self.partner_ids.ids)]
            part = [x.search_key for x in self.partner_ids]
            dom_str += "{'partner_ids':%s}," % ','.join(part)
        if self.charge_type:
            dom += [('aml.charge_type', '=', self.charge_type)]
            dom_str += "{'charge_type':%s}," % self.charge_type
        if self.fiscalyear_start_id:
            dom += [('aml.date', '>=', self.fiscalyear_start_id.date_start)]
            dom_str += "{'fiscalyear_start_id':%s}," % self.fiscalyear_start_id.name
        if self.fiscalyear_end_id:
            dom += [('aml.date', '<=', self.fiscalyear_end_id.date_stop)]
            dom_str += "{'fiscalyear_end_id':%s}," % self.fiscalyear_end_id.name
        if self.period_start_id:
            dom += [('aml.date', '>=', self.period_start_id.date_start)]
            dom_str += "{'period_start_id':%s}," % self.period_start_id.name
        if self.period_end_id:
            dom += [('aml.date', '<=', self.period_end_id.date_stop)]
            dom_str += "{'period_end_id':%s}," % self.period_end_id.name
        if self.date_start:
            dom += [('aml.date', '>=', self.date_start)]
            dom_str += "{'date_start':%s}," % self.date_start
        if self.date_end:
            dom += [('aml.date', '<=', self.date_end)]
            dom_str += "{'date_end':%s}," % self.date_end

        return dom, dom_str

    @api.multi
    def start_report(self):
        self.ensure_one()
        dom, dom_str = self._compute_results()
        params = {}
        params['company'] = self.env.user.with_context(lang="en_US").company_id.partner_id.name
        params['dom_str'] = dom_str
        where_dom = ["%s %s %s" % (x[0],
                                   x[1],
                                   isinstance(x[2], basestring)
                                        and "'%s'" % x[2] or x[2])
                    for x in dom]
        params['condition'] = where_dom\
                            and 'and %s' % (' and '.join(where_dom)).replace('[','(').replace(']',')') or ''
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_expense_ledger',
            'datas': params,
        }

