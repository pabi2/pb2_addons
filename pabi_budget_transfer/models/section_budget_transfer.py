# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class SectionBudgetTransfer(models.Model):
    _name = 'section.budget.transfer'
    _inherit = ['mail.thread']
    _description = "Section Budget Transfer"

    name = fields.Char(
        string='Name',
        required=True,
        readonly=True,
        default='/',
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
        readonly=True,
        default=lambda self: self.env['account.fiscalyear'].find(),
        help="Fiscalyear will be as of current date only, no backdate allowed"
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=lambda self: self.env.user.company_id.currency_id,
        readonly=True,
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
    date_transfer = fields.Date(
        string="Transfer Date",
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
    transfer_user_id = fields.Many2one(
        'res.users',
        string='Transferer',
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
    transfer_line_ids = fields.One2many(
        'section.budget.transfer.line',
        'transfer_id',
        string='Budget Transfer Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    notes = fields.Text(
        string="Additional Information",
    )
    total_transfer_amt = fields.Float(
        string="Transferred Amount",
        compute="_compute_total_transfer_amt",
    )

    @api.depends('transfer_line_ids',
                 'transfer_line_ids.amount_transfer',
                 'state')
    def _compute_total_transfer_amt(self):
        for record in self:
            if record.state == 'transfer':
                lines = record.transfer_line_ids
                total_amt = sum([i.amount_transfer
                                 for i in lines])
                record.total_transfer_amt = total_amt

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
        fiscalyear_id = self.env['account.fiscalyear'].find()
        for record in self:
            if not record.transfer_line_ids:
                raise UserError(
                    _('You can not confirm without transfer lines!'))
            name = self.env['ir.sequence'].\
                with_context(fiscalyear_id=fiscalyear_id).\
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
        for transfer in self:
            transfer.transfer_line_ids.action_transfer()
        self.write({'state': 'transfer',
                    'date_transfer': fields.Date.today(),
                    'transfer_user_id': self._uid})
        return True

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You can not delete non-draft records!'))
        return super(SectionBudgetTransfer, self).unlink()


class SectionBudgetTransferLine(models.Model):
    _name = 'section.budget.transfer.line'
    _description = "Section Budget Transfer Lines"

    transfer_id = fields.Many2one(
        'section.budget.transfer',
        string='Section Budget Transfer',
        ondelete='cascade',
        index=True,
    )
    from_section_id = fields.Many2one(
        'res.section',
        string='From Section',
        required=True,
    )
    from_org_id = fields.Many2one(
        'res.org',
        string='From Org',
        related='from_section_id.org_id',
        readonly=True,
    )
    from_budget_id = fields.Many2one(
        'account.budget',
        string='From Budget',
        readonly=True,
    )
    amount_transfer = fields.Float(
        string='Transfer Amount',
        required=True,
    )
    to_section_id = fields.Many2one(
        'res.section',
        string='To Section',
        required=True,
    )
    to_org_id = fields.Many2one(
        'res.org',
        string='To Org',
        related='to_section_id.org_id',
    )
    to_budget_id = fields.Many2one(
        'account.budget',
        string='To Budget',
        readonly=True,
    )
    notes = fields.Text(
        string="Notes/Reason",
    )

    @api.model
    def _get_section_budget(self, fiscalyear, section):
        AccountBudget = self.env['account.budget']
        budget = AccountBudget.search([
            ('active', '=', True),
            ('fiscalyear_id', '=', fiscalyear.id),
            ('section_id', '=', section.id),
            ('state', 'not in', ('draft', 'cancel'))])
        if not budget:
            raise UserError(
                _("No active budget control for section %s") %
                (section.name_get()[0][1], ))
        if len(budget) == 1:
            return budget
        else:
            raise UserError(
                _("Strange!, there are > 1 active budget control "
                  "for section %s") % (section.name_get(), ))

    @api.multi
    def action_transfer(self):
        for line in self:
            fiscalyear = line.transfer_id.fiscalyear_id
            from_budget = self._get_section_budget(fiscalyear,
                                                   line.from_section_id)
            to_budget = self._get_section_budget(fiscalyear,
                                                 line.to_section_id)
            from_budget.to_release_amount -= line.amount_transfer
            from_budget._validate_plan_vs_release()
            to_budget.to_release_amount += line.amount_transfer
            to_budget._validate_plan_vs_release()
            line.write({'from_budget_id': from_budget.id,
                        'to_budget_id': to_budget.id, })
        return True
