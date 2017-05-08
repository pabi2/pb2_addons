# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning as UserError


class BudgetReleaseWizard(models.TransientModel):
    _name = "budget.release.wizard"

    # release_ids = fields.One2many(
    #     'budget.release.line',
    #     'wizard_id',
    #     string='Release Lines',
    # )
    progress = fields.Float(
        string='Progress',
        readonly=True,
    )
    amount_to_release = fields.Float(
        string="Amount To Release",
    )

    @api.onchange('amount_to_release')
    def _onchange_amount_to_release(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        BudgetLine = self.env['account.budget.line']
        budget_lines = False
        if active_model == 'account.budget.line':
            budget_lines = BudgetLine.search([('id', '=', active_id)])
        elif active_model == 'account.budget':
            budget_lines = BudgetLine.search([('budget_id', '=', active_id)])

        planned_amount = sum([l.planned_amount for l in budget_lines])
        if not planned_amount:
            self.progress = 0.0
        else:
            self.progress = self.amount_to_release / planned_amount * 100

    @api.model
    def default_get(self, fields):
        res = super(BudgetReleaseWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        budget_line = self.env['account.budget.line'].browse(active_id)
        budget_release = budget_line.budget_id.budget_release
        if budget_release == 'auto':
            raise UserError(_('Manual budget released not allowed!'))
        res['amount_to_release'] = budget_line.released_amount
        return res

    @api.multi
    def do_release(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        budget_line = self.env['account.budget.line'].browse(active_id)
        budget_release = budget_line.budget_id.budget_release
        if budget_release == 'auto':
            raise UserError(_('Manual budget released not allowed!'))
        release_result = {}
        release_result.update({budget_line.id: self.amount_to_release})
        budget_line.release_budget_line(release_result)

#
# class BudgetReleaseLine(models.TransientModel):
#     _name = "budget.release.line"
#
#     wizard_id = fields.Many2one(
#         'budget.release.wizard',
#         string='Wizard',
#         readonly=True,
#     )
#     from_period = fields.Integer(
#         string='From Period',
#         readonly=True,
#     )
#     to_period = fields.Integer(
#         string='To Period',
#         readonly=True,
#     )
#     from_date = fields.Date(
#         string='From Date',
#         readonly=True,
#     )
#     to_date = fields.Date(
#         string='To Date',
#         readonly=True,
#     )
#     planned_amount = fields.Float(
#         string='Planned Amount',
#         digits_compute=dp.get_precision('Account'),
#         readonly=True,
#     )
#     released_amount = fields.Float(
#         string='Released Amount',
#         digits_compute=dp.get_precision('Account'),
#         readonly=True,
#     )
#     release = fields.Boolean(
#         string='Release',
#         default=False,
#     )
#     ready = fields.Boolean(
#         string='Ready to release',
#         help="Whether budget should be released according to release interval",
#     )
#     past = fields.Boolean(
#         string='Past release',
#         help="Whether this is past release, and can't be unreleased",
#     )
#
#     @api.onchange('release')
#     def _onchange_release(self):
#         self.released_amount = self.release and self.planned_amount or 0.0
