# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_VIEW_LIST, CHART_VIEW_FIELD, ChartField
import openerp.addons.decimal_precision as dp


class BudgetPrepareTemplate(ChartField, models.Model):
    _name = "budget.prepare.template"
    _description = "Budget Prepare Template"

    name = fields.Char(
        string='Name',
        required=True,
    )
    creating_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self._uid,
    )
    validating_user_id = fields.Many2one(
        'res.users',
        copy=False,
        string='Validating User',
    )
    date = fields.Date(
        string='Date',
        copy=False,
        default=fields.Date.today(),
    )
    date_submit = fields.Date(
        string='Submitted Date',
        copy=False,
        readonly=True,
    )
    date_approve = fields.Date(
        string='Approved Date',
        copy=False,
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
    )
    date_from = fields.Date(
        string='Start Date',
        compute='_compute_date',
        readonly=True,
        store=True,
    )
    date_to = fields.Date(
        string='End Date',
        compute='_compute_date',
        readonly=True,
        store=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submitted'),
         ('cancel', 'Cancelled'),
         ('reject', 'Rejected'),
         ('approve', 'Approved')],
        string='Status',
        default='draft',
        index=True,
        required=True,
        readonly=True,
        copy=False,
    )
    amount_budget_request = fields.Float(
        string='Budget Request',
    )
    amount_budget_policy = fields.Float(
        string='Budget Policy',
    )
    amount_budget_release = fields.Float(
        string='Budget Release',
    )

    @api.multi
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        for rec in self:
            rec.date_from = rec.fiscalyear_id.date_start
            rec.date_to = rec.fiscalyear_id.date_stop

    @api.multi
    def button_submit(self):
        self.write({
            'state': 'submit',
            'date_submit': fields.Date.today(),
        })
        return True

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def button_reject(self):
        self.write({'state': 'reject'})
        return True

    @api.multi
    def button_approve(self):
        self.write({
            'state': 'approve',
            'validating_user_id': self._uid,
            'date_approve': fields.Date.today(),
        })
        return True


class BudgetPrepareLineTemplate(ChartField, models.Model):

    _name = "budget.prepare.line.template"
    _description = "Budget Line"

    name = fields.Char(
        string='Description',
    )
    m0 = fields.Float(
        string='0',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m1 = fields.Float(
        string='1',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m2 = fields.Float(
        string='2',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m3 = fields.Float(
        string='3',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m4 = fields.Float(
        string='4',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m5 = fields.Float(
        string='5',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m6 = fields.Float(
        string='6',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m7 = fields.Float(
        string='7',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m8 = fields.Float(
        string='8',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m9 = fields.Float(
        string='9',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m10 = fields.Float(
        string='10',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m11 = fields.Float(
        string='11',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m12 = fields.Float(
        string='12',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        compute='_compute_planned_amount',
        digits_compute=dp.get_precision('Account'),
        store=True,
    )

    @api.multi
    @api.depends('m1', 'm2', 'm3', 'm4', 'm5', 'm6',
                 'm7', 'm8', 'm9', 'm10', 'm11', 'm12',)
    def _compute_planned_amount(self):
        for rec in self:
            planned_amount = sum([rec.m1, rec.m2, rec.m3, rec.m4,
                                  rec.m5, rec.m6, rec.m7, rec.m8,
                                  rec.m9, rec.m10, rec.m11, rec.m12
                                  ])
            rec.planned_amount = planned_amount + rec.m0  # from last year
