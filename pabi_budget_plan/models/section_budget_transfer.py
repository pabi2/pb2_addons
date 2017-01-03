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
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_prepare = fields.Date(
        string="Prepare Date",
        default=lambda self: fields.Date.context_today(self),
        readonly=True,
        states={'draft': [('readonly', False)]},
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
        readonly=True,
        states={'draft': [('readonly', False)]},
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
         ('transfer', 'Transferred')],
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
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    notes = fields.Text(
        string="Additional Information",
    )
    total_transferred_amt = fields.Float(
        string="Total Transferred Amount",
        compute="_compute_total_transferred_amt",
    )

    @api.depends('section_budget_transfer_line_ids',
                 'section_budget_transfer_line_ids.amount_to_transfer',
                 'state')
    def _compute_total_transferred_amt(self):
        for record in self:
            if record.state == 'transfer':
                lines = record.section_budget_transfer_line_ids
                total_amt = sum([i.amount_to_transfer
                                 for i in lines])
                record.total_transferred_amt = total_amt

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
        for record in self:
            if not record.section_budget_transfer_line_ids:
                raise UserError(
                    _('You can not confirm without transfer lines!'))
            name = self.env['ir.sequence'].\
                next_by_code('section.budget.transfer')
            record.write({'state': 'confirm',
                          'name': name})
        return True

    @api.multi
    def button_approve(self):
        self.write({'state': 'approve',
                    'date_approve': fields.Date.today(),
                    'approver_user_id': self._uid})
        return True

    @api.multi
    def button_transfer(self):
        for record in self:
            for line in record.section_budget_transfer_line_ids:
                if line.amount_to_transfer <= 0.0:
                    raise UserError(
                        _('Amount to transfer must be greater then zero!'))
                from_line = line.from_budget_control_line_id
                from_line_period_str = 'm' + str(line.from_period)
                from_line_amt = from_line.\
                    read([from_line_period_str])[0][from_line_period_str]
                if line.amount_to_transfer > from_line_amt:
                    raise UserError(
                        _('Amount to transfer not be \
                        greater then original amount!'))
                deducted_amt = from_line_amt - line.amount_to_transfer
                from_line.write({from_line_period_str: deducted_amt})

                to_line_period_str = 'm' + str(line.to_period)
                to_line = line.to_budget_control_line_id
                to_line_amt = to_line.\
                    read([to_line_period_str])[0][to_line_period_str]
                new_amt = to_line_amt + line.amount_to_transfer
                to_line.write({to_line_period_str: new_amt})
        self.write({'state': 'transfer',
                    'date_receive': fields.Date.today(),
                    'receiver_user_id': self._uid})
        return True

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You can not delete non-draft records!'))
        return super(SectionTransferUnit, self).unlink()


class SectionTransferUnitLine(models.Model):
    _name = 'section.budget.transfer.line'
    _description = "Section Budget Transfer Lines"

    @api.constrains('from_period',
                    'to_period')
    def check_from_period(self):
        for line in self:
            if line.from_period < 1 or line.from_period > 12:
                raise UserError(_('Period must be between 1 to 12!'))

    budget_transfer_unit_id = fields.Many2one(
        'section.budget.transfer',
        string='Section Budget Transfer',
        required=True,
    )
    from_section_id = fields.Many2one(
        'res.section',
        string='From Section',
        required=True,
    )
    from_org_id = fields.Many2one(
        'res.org',
        string='From Org',
        required=False,
    )
    from_budget_control_id = fields.Many2one(
        'account.budget',
        string="From Budget Control",
        required=True,
    )
    from_budget_control_line_id = fields.Many2one(
        'account.budget.line',
        string="From Budget Control Line",
        required=True,
    )
    from_period_id = fields.Many2one(
        'account.period',
        string="From Period",
        required=False,
    )
    from_period = fields.Integer(
        string="From Period",
        required=True,
    )
    amount_to_transfer = fields.Float(
        string='Amount to Transfer',
        required=True,
    )
    to_section_id = fields.Many2one(
        'res.section',
        string='To Section',
        required=True,
    )
    to_budget_control_id = fields.Many2one(
        'account.budget',
        string="To Budget Control",
        required=True,
    )
    to_budget_control_line_id = fields.Many2one(
        'account.budget.line',
        string="To Budget Control Line",
        required=True,
    )
    to_period_id = fields.Many2one(
        'account.period',
        string="To Period",
        required=False,
    )
    to_period = fields.Integer(
        string="To Period",
        required=True,
    )
    notes = fields.Text(
        string="Notes/Reason",
    )

    @api.onchange('from_budget_control_line_id', 'to_budget_control_line_id')
    def onchage_line_params(self):
        for record in self:
            budget = record.from_budget_control_line_id.budget_id
            if record.from_budget_control_line_id:
                record.from_budget_control_id = budget
                record.from_section_id = budget.section_id
                record.from_org_id = budget.section_id.org_id
            elif record.from_budget_control_id:
                record.from_section_id = budget.section_id

            budget = record.to_budget_control_line_id.budget_id
            if record.to_budget_control_line_id:
                record.to_budget_control_id = budget
                record.to_section_id = budget.section_id
            elif record.from_budget_control_id:
                record.to_section_id = budget.section_id
