# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.addons.account_budget_activity.models.account_activity import \
    ActivityCommon
from openerp.addons.pabi_chartfield.models.chartfield import ChartField


class AccountInterface(models.Model):
    _name = 'account.interface'

    system_origin_id = fields.Many2one(
        'system.origin',
        string='System Origin',
        ondelete='restrict',
        requried=True,
        help="System Origin where this interface transaction is being called",
    )
    name = fields.Char(
        string='Model Name',
        required=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        help="Journal to be used in creating Journal Entry",
    )
    line_ids = fields.One2many(
        'account.interface.line',
        'interface_id',
        string='Lines',
        copy=True,
    )
    legend = fields.Text(
        string='Legend',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        related='journal_id.company_id',
        string='Company',
        store=True,
        readonly=True
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
    )

    # Constraints
    @api.multi
    def _validate_data(self):
        for rec in self:
            # Must have lines
            if len(rec.line_ids) == 0:
                raise ValidationError(_('No lines!'))
            # Must same posting date
            move_dates = list(set(rec.line_ids.mapped('date')))
            if len(move_dates) > 1:
                raise ValidationError(
                    _('Inteferce lines can not have different posting date!'))
            # For account.type receivable and payble, must have date maturity
            lines = rec.line_ids.filtered(
                lambda l: l.account_id.type in ('payable', 'receivable'))
            dates = lines.mapped('date_maturity')
            if False in dates:
                raise ValidationError(
                    _('Payable/Receivabe lines must have payment due date!'))
            # For non THB, must have amount_currency
            lines = rec.line_ids.filtered(
                lambda l: l.currency_id and
                l.currency_id.id != rec.company_id.currency_id)
            for l in lines:
                if (l.debit or l.credit) and not l.amount_currency:
                    raise ValidationError(
                        _('Amount Currency must not be False '))

    @api.multi
    def create_entry(self):
        self._validate_data()
        move_ids = []
        AccountMove = self.env['account.move']
        AccountMoveLine = self.env['account.move.line']
        Period = self.env['account.period']
        for interface in self:
            move_date = interface.line_ids[0].date
            ctx = self._context.copy()
            ctx.update({'company_id': interface.company_id.id})
            periods = Period.find(dt=move_date)
            period_id = periods and periods[0].id or False
            ctx.update({
                'journal_id': interface.journal_id.id,
                'period_id': period_id,
            })
            move = AccountMove.create({
                'ref': interface.name,
                'period_id': period_id,
                'journal_id': interface.journal_id.id,
                'date': move_date,
            })
            move_ids.append(move.id)
            for line in interface.line_ids:
                val = {
                    'move_id': move.id,
                    'journal_id': interface.journal_id.id,
                    'period_id': period_id,
                    # Line Info
                    'name': line.name,
                    'quantity': line.quantity,
                    'debit': line.debit,
                    'credit': line.credit,
                    'account_id': line.account_id.id,
                    'partner_id': line.partner_id.id,
                    'date': line.date,
                    'date_maturity': line.date_maturity,   # Payment Due Date
                }
                AccountMoveLine.with_context(ctx).create(val)
            interface.move_id = move.id
        # Post all at once
        AccountMove.browse(move_ids).post()
        return move_ids


class AccountInterfaceLine(ChartField, ActivityCommon, models.Model):
    _name = 'account.interface.line'
    _order = 'sequence'

    interface_id = fields.Many2one(
        'account.interface',
        string='Interface Model',
        index=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Sequence',
        default=0,
    )
    name = fields.Char(
        string='Name',
        required=True,
    )
    quantity = fields.Float(
        string='Quantity',
    )
    debit = fields.Float(
        string='Debit',
    )
    credit = fields.Float(
        string='Credit',
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True,
        ondelete='cascade',
        digits_compute=dp.get_precision('Account')
    )
    amount_currency = fields.Float(
        string='Amount Currency',
        help="The amount expressed in an optional other currency.",
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    date = fields.Date(
        string='Posting Date',
        required=True,
        help="Account Posting Date. "
        "As such, all lines in the same document should have same date."
    )
    date_maturity = fields.Date(
        string='Maturity Date',
        help="Date "
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
    )
