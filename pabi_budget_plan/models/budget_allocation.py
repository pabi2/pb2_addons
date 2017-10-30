# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class BudgetAllocation(models.Model):
    _name = 'budget.allocation'
    _inherit = ['mail.thread']
    _description = 'Budget Allocation'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscalyear',
        index=True,
        ondelete='cascade',
    )
    revision = fields.Selection(
        lambda self: [(str(x), str(x))for x in range(13)],
        string='Revision',
        readonly=True,
        help="Revision 0 - 12, 0 is on on the fiscalyear open.",
    )
    amount_unit_base = fields.Float(
        string='Unit Based',
    )
    amount_project_base = fields.Float(
        string='Project Based',
    )
    amount_personnel = fields.Float(
        string='Personnel Budget',
    )
    amount_invest_asset = fields.Float(
        string='Invest Asset',
    )
    amount_invest_construction = fields.Float(
        string='Invest Construction',
    )
    amount_total = fields.Float(
        string='Total',
        compute='_compute_amount_total',
        store=True,
    )
    _sql_constraints = [
        ('uniq_revision', 'unique(fiscalyear_id, revision)',
         'Duplicated revision of budget policy is not allowed!'),
    ]

    @api.multi
    @api.depends('amount_unit_base', 'amount_project_base', 'amount_personnel',
                 'amount_invest_asset', 'amount_invest_construction')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum([rec.amount_unit_base,
                                    rec.amount_project_base,
                                    rec.amount_personnel,
                                    rec.amount_invest_asset,
                                    rec.amount_invest_construction])

    @api.model
    def _change_amount_content(self, fiscal, alloc, alloc_vals):
        track_fields = ['amount_unit_base', 'amount_project_base',
                        'amount_personnel', 'amount_invest_asset',
                        'amount_invest_construction']
        if not alloc_vals or set(alloc_vals.keys()).isdisjoint(track_fields):
            return False
        field_labels = dict([(name, field.string)
                             for name, field in alloc._fields.iteritems()])
        title = _('Allocation change(s) for %s revision %s') % (fiscal.name,
                                                                alloc.revision)
        message = '<h3>%s</h3><ul>' % title
        for field in track_fields:
            if alloc_vals.get(field, False):
                message += _(
                    '<li><b>%s</b>: %s → %s</li>'
                ) % (field_labels[field],
                     '{:,.2f}'.format(alloc[field]),
                     '{:,.2f}'.format(alloc_vals[field]), )
        message += '</ul>'
        return message

    @api.multi
    def write(self, vals):
        for alloc in self:
            message = self._change_amount_content(alloc.fiscalyear_id,
                                                  alloc, vals)
            if message:
                alloc.fiscalyear_id.message_post(body=message)
        return super(BudgetAllocation, self).write(vals)
