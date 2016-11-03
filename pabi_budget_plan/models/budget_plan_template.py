# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.addons.pabi_chartfield.models.chartfield \
    import ChartField, CHART_VIEW_FIELD
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError


class BudgetPlanTemplate(ChartField, models.Model):
    _name = "budget.plan.template"
    _inherit = 'mail.thread'
    _description = "Budget Plan Template"

    @api.one
    @api.constrains('fiscalyear_id', 'section_id')
    def _check_fiscalyear_section_unique(self):
        if self.fiscalyear_id and self.section_id:
            budget_plans = self.search(
                [('fiscalyear_id', '=', self.fiscalyear_id.id),
                 ('section_id', '=', self.section_id.id),
                 ('state', 'not in', ('cancel', 'reject')),
                 ])
            if len(budget_plans) > 1:
                raise ValidationError(
                    _('You can not have duplicate budget plan for '
                      'same fiscalyear and section.'))

    @api.model
    def _default_fy(self):
        current_fiscalyear = self.env['account.period'].find().fiscalyear_id
        #next_fiscalyear = self.env['account.fiscalyear'].search(
        #    [('date_start', '>', current_fiscalyear.date_stop)],
        #    limit=1)
        return current_fiscalyear or False

    name = fields.Char(
        string='Number',
        required=True,
        default="/",
        copy=False,
    )
    creating_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self._uid,
    )
    submiting_user_id = fields.Many2one(
        'res.users',
        copy=False,
        string='Submitting User',
    )
    validating_user_id = fields.Many2one(
        'res.users',
        copy=False,
        string='Validating User',
    )
    accepting_user_id = fields.Many2one(
        'res.users',
        copy=False,
        string='Accepting User',
    )
    validating_user_id = fields.Many2one(
        'res.users',
        copy=False,
        string='Verifying User',
    )
    rejecting_user_id = fields.Many2one(
        'res.users',
        copy=False,
        string='Rejecting User',
    )
    date = fields.Date(
        string='Date',
        copy=False,
        default=lambda self: fields.Date.context_today(self),
    )
    date_submit = fields.Date(
        string='Submitted Date',
        copy=False,
        readonly=True,
    )
    date_approve = fields.Date(
        string='Verified Date',
        copy=False,
        readonly=True,
    )
    date_accept = fields.Date(
        string='Accepted Date',
        copy=False,
        readonly=True,
    )
    date_reject = fields.Date(
        string='Rejected Date',
        copy=False,
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
        default=_default_fy,
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
        related="section_id.division_id",
        required=True,
        readonly=True,
    )
    date_from = fields.Date(
        string='Start Date',
        compute='_compute_date',
        store=True,
    )
    date_to = fields.Date(
        string='End Date',
        compute='_compute_date',
        store=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submitted'),
         ('accept', 'Approved'),
         ('cancel', 'Cancelled'),
         ('reject', 'Rejected'),
         ('approve', 'Verified'),
         ('accept_corp', 'Accepted'),
         ],
        string='Status',
        default='draft',
        index=True,
        required=True,
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )
    
    org_id = fields.Many2one(related='section_id.org_id')

    @api.onchange('fiscalyear_id')
    def onchange_fiscalyear_id(self):
        self.date_from = self.fiscalyear_id.date_start
        self.date_to = self.fiscalyear_id.date_stop

    @api.one
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        self.date_from = self.fiscalyear_id.date_start
        self.date_to = self.fiscalyear_id.date_stop


class BudgetPlanLineTemplate(ChartField, models.Model):

    _name = "budget.plan.line.template"
    _description = "Budget Line"

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=False,
    )
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
    # Set default for Fund
    fund_id = fields.Many2one(
        'res.fund',
        string='Fund',
        default=lambda self: self.env.ref('base.fund_nstda'),
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


class BudgetPlanCommon(object):

    @api.multi
    @api.depends('plan_line_ids')
    def _compute_planned_overall(self):
        for rec in self:
            planned_amounts = rec.plan_line_ids.mapped('planned_amount')
            rec.planned_overall = sum(planned_amounts)

    @api.model
    def _prepare_copy_fields(self, source_model, target_model):
        src_fields = [f for f, _x in source_model._fields.iteritems()]
        no_fields = [
            'id', 'state', 'display_name', '__last_update', 'state'
            'write_date', 'create_date', 'create_uid', 'write_uid',
            'date', 'date_approve', 'date_submit', 'date_from', 'date_to',
            'template_id', 'validating_user_id', 'creating_user_id',
        ]
        trg_fields = [f for f, _x in target_model._fields.iteritems()]
        return list((set(src_fields) & set(trg_fields)) - set(no_fields))

    @api.model
    def _convert_plan_to_budget_control(self, active_id,
                                        head_src_model,
                                        line_src_model):
        head_trg_model = self.env['account.budget']
        line_trg_model = self.env['account.budget.line']
        header_fields = self._prepare_copy_fields(head_src_model,
                                                  head_trg_model)
        line_fields = self._prepare_copy_fields(line_src_model,
                                                line_trg_model)
        plan = self.browse(active_id)
        vals = {}
        for key in header_fields:
            vals.update({key: (hasattr(plan[key], '__iter__') and
                               plan[key].id or plan[key])})
        budget = head_trg_model.create(vals)
        for line in plan.plan_line_ids:
            for key in line_fields:
                vals.update({key: (hasattr(line[key], '__iter__') and
                                   line[key].id or line[key])})
            vals.update({'budget_id': budget.id})
            line_trg_model.create(vals)
        return budget

    @api.multi
    def button_submit(self):
        for rec in self:
            res = rec.template_id.\
                _get_chained_dimension(CHART_VIEW_FIELD[rec.chart_view])
            rec.write(res)
            name = self.env['ir.sequence'].next_by_code('budget.plan')
            rec.write({'name': name})
            for line in rec.plan_line_ids:
                res = line.mapped('template_id').\
                    _get_chained_dimension(CHART_VIEW_FIELD[line.chart_view])
                line.write(res)
        self.write({
            'state': 'submit',
            'date_submit': fields.Date.context_today(self),
            'submiting_user_id': self._uid,
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
        self.write({
            'state': 'reject',
            'date_reject': fields.Date.context_today(self),
            'rejecting_user_id': self._uid,
        })
        return True

    @api.multi
    def button_accept(self):
        self.write({
            'state': 'accept',
            'date_accept': fields.Date.context_today(self),
            'accepting_user_id': self._uid,
        })
        return True

    @api.multi
    def button_approve(self):
        self.write({
            'state': 'approve',
            'validating_user_id': self._uid,
            'date_approve': fields.Date.context_today(self),
        })
        return True

    @api.multi
    def button_accept_corp(self):
        self.write({
            'state': 'accept_corp',
        })
        return True

    @api.multi
    def button_back_approve(self):
        self.write({
            'state': 'accept',
        })
        return True

    @api.multi
    def button_back_verify(self):
        self.write({
            'state': 'approve',
        })
        return True
