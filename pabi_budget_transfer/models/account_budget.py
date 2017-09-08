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

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        # case transfer, only list budget with diff amount to transfer
        if self._context.get('show_release_diff_rolling_gt_zero', False):
            budgets = self.search(args)
            _ids = []
            for budget in budgets:
                if budget.release_diff_rolling >= 0.0:
                    _ids.append(budget.id)
            args += [('id', 'in', _ids)]
        return super(AccountBudget, self).name_search(name=name,
                                                      args=args,
                                                      operator=operator,
                                                      limit=limit)
