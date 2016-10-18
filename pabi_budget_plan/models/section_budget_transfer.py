# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class SectionTransferUnit(models.Model):
    _name = 'section.budget.transfer'
    _inherit = ['mail.thread']
    _description = "Section Budget Transfer"

    name = fields.Char(
        string="Name",
        required=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
    )
    date_prepare = fields.Date(
        string="Prepare Date",
        default=lambda self: fields.Date.context_today(self),
    )
    date_approve = fields.Date(
        string="Approved Date",
        readonly=True,
    )
    date_receive = fields.Date(
        string="Received Date",
        readonly=True,
    )
    preparer_user_id = fields.Many2one(
        'res.users',
        string='Preparer',
        default=lambda self: self._uid,
    )
    approver_user_id = fields.Many2one(
        'res.users',
        string='Approver',
        readonly=True,
    )
    receiver_user_id = fields.Many2one(
        'res.users',
        string='Receiver',
        readonly=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirmed'),
         ('approve', 'Approved'),
         ('cancel', 'Cancelled'),
         ('transfer', 'Transferred'),],
        string='Status',
        default='draft',
        index=True,
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )
    section_budget_transfer_line_ids = fields.One2many(
        'section.budget.transfer.line',
        'budget_transfer_unit_id',
        string='Section Budget Transfer Lines',
    )

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def button_confirm(self):
        self.write({'state': 'confirm'})
        return True

    @api.multi
    def button_approve(self):
        self.write({'state': 'approve',
                    'date_approve': fields.Date.today(),
                    'approver_user_id': self._uid,})
        return True
    
    @api.multi
    def button_transfer(self):
        self.write({'state': 'transfer'})
        return True


class SectionTransferUnitLine(models.Model):
    _name = 'section.budget.transfer.line'
    _description = "Section Budget Transfer Lines"

    budget_transfer_unit_id = fields.Many2one(
        'section.budget.transfer',
        string='Section Budget Transfer',
    )
    from_section_id = fields.Many2one(
        'res.section',
        string='From Section',
    )
    from_budget_control_id = fields.Many2one(
        'account.budget',
        string="From Budget Control",
    )
    from_budget_control_line_id = fields.Many2one(
        'account.budget.line',
        string="From Budget Control Line",
    )
    from_period_id = fields.Many2one(
        'account.period',
        string="From Period",
    )
    to_section_id = fields.Many2one(
        'res.section',
        string='To Section',
    )
    to_budget_control_id = fields.Many2one(
        'account.budget',
        string="To Budget Control",
    )
    to_budget_control_line_id = fields.Many2one(
        'account.budget.line',
        string="To Budget Control Line",
    )
    to_period_id = fields.Many2one(
        'account.period',
        string="To Period",
    )
