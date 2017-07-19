# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountBudget(models.Model):
    _inherit = 'account.budget'

    in_unit_transfer_ids = fields.One2many(
        'section.budget.transfer.line',
        'to_budget_id',
        string='Transfer In',
        domain=[('state', '=', 'transfer')],
        readonly=True,
        copy=False,
    )
    out_unit_transfer_ids = fields.One2many(
        'section.budget.transfer.line',
        'from_budget_id',
        string='Transfer In',
        domain=[('state', '=', 'transfer')],
        readonly=True,
        copy=False,
    )

    @api.multi
    def name_get(self):
        if self._context.get('display_as_section', False):
            result = []
            for budget in self:
                section = budget.section_id
                name = section.name
                name_short = ('name_short' in section) and \
                    section['name_short'] or False
                result.append(
                    (budget.id, "%s%s" %
                     (section.code and '[' + section.code + '] ' or '',
                      name_short or name or '')))
        else:
            result = super(AccountBudget, self).name_get()
        return result
