# -*- coding: utf-8 -*-
from openerp import api, models, fields, _
from openerp.exceptions import ValidationError
from .chartfield import CHART_FIELDS, ChartFieldAction
from datetime import datetime


class AccountAnalyticLine(ChartFieldAction, models.Model):
    _inherit = 'account.analytic.line'

    # ChartfieldAction changed account_id = account.account, must change back
    account_id = fields.Many2one('account.analytic.account')
    # Following fields is not mature yet, so we need it to be store=False
    docline_seq = fields.Integer(
        string='Docline Seq',
        compute='_compute_docline_seq',
    )
    document_date = fields.Date(
        string='Document Date',
        compute='_compute_document_date',
    )
    request_emp_id = fields.Many2one(
        'hr.employee',
        string='Requester',
        compute='_compute_document_employee_partner',
    )
    prepare_emp_id = fields.Many2one(
        'hr.employee',
        string='Requester',
        compute='_compute_document_employee_partner',
    )
    approve_emp_id = fields.Many2one(
        'hr.employee',
        string='Requester',
        compute='_compute_document_employee_partner',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        compute='_compute_document_employee_partner',
    )
    chartfield_id = fields.Reference(
        [('res.section', 'Section'),
         ('res.project', 'Project'),
         ('res.invest.asset', 'Invest Asset'),
         ('res.invest.construction.phase', 'Construction Phase'),
         ('res.personnel.costcenter', 'Personnel'), ],
        string='Budget',
        compute='_compute_chartfield',
    )

    @api.multi
    def _compute_docline_seq(self):
        """ Only for PR/PO/SO/EX that we can do at this moment """
        for rec in self:
            if rec.doctype not in ('sale_order', 'purchase_order',
                                   'purchase_request', 'employee_expense'):
                continue
            rec.docline_seq = \
                rec.purchase_line_id.docline_seq or \
                rec.sale_line_id.docline_seq or \
                rec.expense_line_id.docline_seq or \
                rec.purchase_request_line_id.docline_seq
        return True

    @api.multi
    def _compute_document_date(self):
        for rec in self:
            res_model = rec.document_id and rec.document_id._name or False
            if res_model in ['hr.expense.expense']:
                rec.document_date = rec.document_id.create_date
            if res_model in ['sale.order', 'purchase.order']:
                rec.document_date = rec.document_id.date_order
            if res_model in ['purchase.request']:
                create_date = datetime.strptime(
                    rec.document_id.create_date, '%Y-%m-%d %H:%M:%S')
                rec.document_date = create_date.strftime('%Y-%m-%d')
            if res_model in ['account.invoice']:
                rec.document_date = rec.document_id.date_document
            if res_model in ['stock.picking']:
                rec.document_date = rec.document_id.date
        return True

    @api.multi
    def _compute_document_employee_partner(self):
        """ Only for PR/EX that will have request/prepare/approver user """
        for rec in self:
            # Employee
            if rec.doctype == 'employee_expense':
                rec.request_emp_id = rec.document_id.employee_id
                rec.prepare_emp_id = \
                    rec.document_id.user_id.partner_id.employee_id
                rec.approve_emp_id = \
                    rec.document_id.approver_id.partner_id.employee_id
            if rec.doctype == 'purchase_request':
                rec.request_emp_id = \
                    rec.document_id.requested_by.partner_id.employee_id
                rec.prepare_emp_id = \
                    rec.document_id.responsible_uid.partner_id.employee_id
                rec.approve_emp_id = \
                    rec.document_id.assigned_to.partner_id.employee_id
            # Partner
            res_model = rec.document_id and rec.document_id._name or False
            if res_model in ['hr.expense.expense', 'sale.order',
                             'purchase.order', 'account.invoice',
                             'stock.picking']:
                rec.partner_id = rec.document_id.partner_id
        return True

    @api.multi
    def _compute_chartfield(self):
        for rec in self:
            model, res_id = False, False
            if rec.section_id:
                model, res_id = ('res.section', rec.section_id.id)
            if rec.project_id:
                model, res_id = ('res.project', rec.project_id.id)
            if rec.invest_asset_id:
                model, res_id = ('res.invest.asset', rec.invest_asset_id.id)
            if rec.invest_construction_phase_id:
                model, res_id = ('res.invest.construction.phase',
                                 rec.invest_construction_phase_id.id)
            if rec.personnel_costcenter_id:
                model, res_id = ('res.personnel.costcenter',
                                 rec.personnel_costcenter_id.id)
            rec.chartfield_id = '%s,%s' % (model, res_id)
        return True


class AccountAnalyticAccount(ChartFieldAction, models.Model):
    _inherit = 'account.analytic.account'

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        required=True,  # Some error on adjust asset -> expense, temp remove
    )

    @api.model
    def _analytic_dimensions(self):
        dimensions = super(AccountAnalyticAccount, self)._analytic_dimensions()
        dimensions += dict(CHART_FIELDS).keys()
        return dimensions

    @api.model
    def test_chartfield_active(self, chartfield_dict):
        """ Test with following chartfield is inactive
            :param chartfield_dict: i.e., {'section_id': 1234, ...}
            :return: (active, err_message)
        """
        test_model = {
            'res.costcenter': 'costcenter_id',
            'res.section': 'section_id',
            'res.project': 'project_id',
            'res.invest.construction.phase': 'invest_construction_phase_id',
            'res.invest.asset': 'invest_asset_id',
            'res.personnel.costcenter': 'personnel_costcenter_id',
        }
        for model, field in test_model.iteritems():
            if chartfield_dict.get(field, False):
                obj = self.env[model].search(
                    [('id', '=', chartfield_dict[field]),
                     ('active', '=', False)])
                if obj:
                    return (False, _('Inactive: %s') % obj.display_name_2)
        return (True, False)

    @api.model
    def get_analytic_search_domain(self, rec):
        domain = \
            super(AccountAnalyticAccount, self).get_analytic_search_domain(rec)
        chartfield_dict = dict([(x[0], x[2]) for x in domain])
        active, err_message = self.test_chartfield_active(chartfield_dict)
        if not active:
            raise ValidationError(err_message)
        return domain
