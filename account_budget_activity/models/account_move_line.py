# -*- coding: utf-8 -*-
from openerp import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    charge_type = fields.Selection(  # Prepare for pabi_internal_charge
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        required=True,
        default='external',
        help="Specify whether the move line is for Internal Charge or "
        "External Charge. Only expense internal charge to be set as internal",
    )
    org_id = fields.Many2one(
            'res.org', string='Org')
            
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )

    @api.model
    def _prepare_analytic_line(self, obj_line):
        vals = super(AccountMoveLine, self)._prepare_analytic_line(obj_line)
        if obj_line.charge_type == 'internal':
            vals['charge_type'] = 'internal'
        return vals

    @api.model
    def _update_analytic_dimension(self, vals):
        """ Add dimension on move line """
        Analytic = self.env['account.analytic.account']
        analytic = False
        if vals.get('analytic_account_id', False):
            analytic = Analytic.browse(vals['analytic_account_id'])
        if analytic:
            domain = Analytic.get_analytic_search_domain(analytic)
            vals.update(dict((x[0], x[2]) for x in domain))
        return vals

    @api.model
    def create(self, vals):
        vals = self._update_analytic_dimension(vals)
        return super(AccountMoveLine, self).create(vals)

    @api.multi
    def create_analytic_lines(self):
        # Before create, always remove analytic line if exists
        move_lines = self._budget_eligible_move_lines()
        (self - move_lines).mapped('analytic_lines').unlink()
        return super(AccountMoveLine, move_lines).create_analytic_lines()

    @api.multi
    def _budget_eligible_move_lines(self):
        """ To be eligible, move line must be,
        * With journal with analytic_journal
        * Have AG
        * Invoice with realtime stockable product, no budget charge
        """
        BG = self.env['account.budget']
        move_lines = self.filtered(  # Too complicated to use SQL
            lambda l:
            BG.budget_eligible_line(l.journal_id.analytic_journal_id, l)
            # Invoice with realtime stockable product, no budget charge.
            and (not l.invoice or l.product_id.type == 'service' or
                 l.product_id.valuation != 'real_time')
        )
        return move_lines

    @api.model
    def _query_get(self, obj='l'):
        query = super(AccountMoveLine, self)._query_get(obj=obj)
        if self.env.context.get('charge_type', False):
            charge_type = self.env.context.get('charge_type')
            query += "AND " + obj + ".charge_type = '%s'" % (charge_type, )
        if self.env.context.get('org_id', False):
            org_id = self.env.context.get('org_id')
            query += "AND " + obj + ".org_id = %d" % (org_id, )
        return query
