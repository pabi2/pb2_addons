# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare

_TRANSFER_STATE = [('draft', 'Draft'),
                   ('confirm', 'Confirmed'),
                   ('approve', 'Approved'),
                   ('cancel', 'Cancelled'),
                   ('transfer', 'Transferred')]


class SectionBudgetTransfer(models.Model):
    _name = 'section.budget.transfer'
    _inherit = ['mail.thread']
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Section Budget Transfer"
    _order = 'id desc'
    #
    # _track = {
    #     'state': {
    #         'pabi_budget_transfer.mt_transferd_draft_to_confirmed':
    #             lambda self, cr, uid, obj, ctx=None: obj.state == 'confirm',
    #     },
    # }

    # @api.model
    # def _needaction_domain_get(self):
    #     """ Show as unread to everyone as it is transfered """
    #     return [('state', '=', 'draft')]

    name = fields.Char(
        string='Name',
        required=True,
        readonly=True,
        default='/',
        size=100,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
        readonly=True,
        # states={'draft': [('readonly', False)]},
        default=lambda self: self.env['account.fiscalyear'].find(),
        help="Fiscalyear will be as of current date only, no backdate allowed"
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
        required=True,
        readonly=True,
        default=lambda self:
        self.env.user.partner_id.employee_id.section_id.division_id,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=True,
        readonly=True,
        default=lambda self:
        self.env.user.partner_id.employee_id.section_id.org_id,
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
        default=lambda self: self.env.user,
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
        _TRANSFER_STATE,
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
        string='Additional Information',
        size=1000,
    )
    total_transfer_amt = fields.Float(
        string='Transferred Amount',
        compute='_compute_total_transfer_amt',
    )

    @api.multi
    @api.constrains('fiscalyear_id', 'org_id', 'transfer_line_ids')
    def _check_transfer_line(self):
        """ Check that, all budget selected must be
        * chart_view = 'unit_base'
        * Same fiscal as the header
        * Belong to the same Org
        * Must be in state draft
        """
        for trans in self:
            for l in trans.transfer_line_ids:
                # State
                if l.from_budget_id.state != 'draft' or \
                        l.to_budget_id.state != 'draft':
                    raise ValidationError(_('Please verify that all budgets '
                                            'are in draft state!'))
                # Unit based
                if l.from_budget_id.chart_view != 'unit_base' or \
                        l.to_budget_id.chart_view != 'unit_base':
                    raise ValidationError(
                        _('Please verify that all budgets are unit based'))
                # Fiscal year
                this_fy_id = self.env['account.fiscalyear'].find()
                this_fy = self.env['account.fiscalyear'].browse(this_fy_id)
                if this_fy.id != trans.fiscalyear_id.id:
                    raise ValidationError(
                        _('Current FY is %s, you are not allow to transfer '
                          'budget out of this fiscalyear.') % (this_fy.name))
                if l.from_budget_id.fiscalyear_id != trans.fiscalyear_id or \
                        l.to_budget_id.fiscalyear_id != trans.fiscalyear_id:
                    raise ValidationError(
                        _('Please verify that all budgets are on fiscal '
                          'year %s') % (trans.fiscalyear_id.name))
                # Org
                # kittiu: this result in error during save
                # if l.from_budget_id.org_id != trans.org_id or \
                #         l.to_budget_id.org_id != trans.org_id:
                #     raise ValidationError(
                #        _('Please verify that all budgets belong to Org %s') %
                #         (trans.org_id.name_short))
                # Not same budget
                if l.from_budget_id == l.to_budget_id:
                    raise ValidationError(_('Please verify that source and '
                                            'target budget are not same!'))

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
            # 1) Lines
            if sum(record.transfer_line_ids.mapped('amount_transfer')) == 0.0:
                raise ValidationError(
                    _('You can not confirm without transfer line amount!'))
            # 2) Can't transfer > room
            for line in record.transfer_line_ids:
                if float_compare(
                        line.amount_transfer,
                        line.from_budget_id.release_diff_rolling, 2) == 1:
                    raise ValidationError(
                        _('Your amount is bigger than '
                          'available amount to transfer!'))
            name = self.env['ir.sequence'].\
                with_context(fiscalyear_id=fiscalyear_id).\
                next_by_code('section.budget.transfer')
            record.write({'state': 'confirm',
                          'name': name})
        return True

    @api.multi
    def button_approve(self):
        self.write({'state': 'approve',
                    'date_approve': fields.Date.context_today(self),
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
                raise ValidationError(
                    _('You can not delete non-draft records!'))
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
    state = fields.Selection(
        _TRANSFER_STATE,
        string='Status',
        related='transfer_id.state',
        readonly=True,
        store=True,
    )
    from_budget_id = fields.Many2one(
        'account.budget',
        string='From Section',
        required=True,
        domain=[('chart_view', '=', 'unit_base')],
    )
    from_budget = fields.Char(
        string='From Budget',
        related='from_budget_id.name',
        readonly=True,
    )
    from_section_id = fields.Many2one(
        'res.section',
        string='From Secton',
        related='from_budget_id.section_id',
        readonly=True,
    )
    amount_transfer = fields.Float(
        string='Transfer Amount',
        required=True,
    )
    to_budget_id = fields.Many2one(
        'account.budget',
        string='To Section',
        required=True,
        domain=[('chart_view', '=', 'unit_base')],
    )
    to_budget = fields.Char(
        string='To Budget',
        related='to_budget_id.name',
        readonly=True,
    )
    to_section_id = fields.Many2one(
        'res.section',
        string='To Secton',
        related='to_budget_id.section_id',
        readonly=True,
    )
    notes = fields.Text(
        string='Notes/Reason',
        size=1000,
    )
    _sql_constraints = [
        ('no_negative_transfer_amount', 'CHECK(amount_transfer >= 0)',
         'Transfer amount must be positive'),
    ]

    @api.multi
    def action_transfer(self):
        # Only available setup to use section budget transfer it,
        for line in self:
            from_budget = line.from_budget_id
            to_budget = line.to_budget_id
            # Check budget level
            from_budget_release = from_budget.budget_level_id.budget_release
            to_budget_release = to_budget.budget_level_id.budget_release
            if from_budget_release != 'manual_header' or \
                    to_budget_release != 'manual_header':
                raise ValidationError(
                    _('Budget level for unit base is not valid for transfer.\n'
                      'Please make sure Release Type = "Budget Header".'))
            from_budget.write({
                'to_release_amount': (from_budget.released_amount -
                                      line.amount_transfer)})
            from_budget._validate_plan_vs_release()
            to_budget.write({
                'to_release_amount': (to_budget.released_amount +
                                      line.amount_transfer)})
            to_budget._validate_plan_vs_release()
        return True

    @api.onchange('from_budget_id')
    def _onchange_from_budget_id(self):
        if self.from_budget_id and \
                self.from_budget_id.release_diff_rolling <= 0.0:
            raise ValidationError(
                _("%s don't have enough budget to transfer.\n"
                  "Make sure its rolling amount is less than its released") %
                self.from_budget_id.name)
        self.amount_transfer = self.from_budget_id.release_diff_rolling

    @api.onchange('amount_transfer')
    def _onchange_amount_transfer(self):
        if float_compare(self.amount_transfer,
                         self.from_budget_id.release_diff_rolling, 2) == 1:
            raise ValidationError(
                _('Your amount is bigger than available amount to transfer!'))
