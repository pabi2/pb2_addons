# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )

    @api.model
    def create(self, vals):
        """ Add posting dimension """
        if vals.get('account_id', False):
            Analytic = self.env['account.analytic.account']
            analytic = Analytic.browse(vals['account_id'])
            if not analytic:
                analytic = Analytic.create_matched_analytic(self)
            if analytic:
                domain = Analytic.get_analytic_search_domain(analytic)
                vals.update(dict((x[0], x[2]) for x in domain))
        return super(AccountAnalyticLine, self).create(vals)


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    type = fields.Selection(
        [('view', 'Analytic View'),
         ('normal', 'Analytic Account'),
         ('product', 'Product'),
         ('activity', 'Activity'),
         ('contract', 'Contract or Project'),
         ('template', 'Template of Contract')]
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        ondelete='restrict',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        ondelete='restrict',
        compute='_compute_activity_group_id',
        store=True,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        ondelete='restrict',
    )

    @api.one
    @api.depends('activity_id')
    def _compute_activity_group_id(self):
        self.activity_group_id = self.activity_id.activity_group_id

    @api.model
    def _analytic_dimensions(self):
        dimensions = [
            'product_id',
            'activity_id',
            'activity_group_id',
        ]
        return dimensions

    @api.model
    def get_analytic_search_domain(self, rec):
        dimensions = self._analytic_dimensions()
        domain = []
        for dimension in dimensions:
            domain.append((dimension, '=', rec[dimension].id))
        return domain

    @api.model
    def get_matched_analytic(self, rec):
        domain = self.get_analytic_search_domain(rec)
        if rec.product_id:
            domain.append(('type', '=', 'product'))
        elif rec.activity_id:
            domain.append(('type', '=', 'activity'))
        analytics = self.env['account.analytic.account'].search(domain)
        if analytics:
            return analytics[0]
        return False

    @api.model
    def create_matched_analytic(self, rec):
        # Not allow product and activity at the same time.
        if ('product_id' in rec._fields) and ('activity_id' in rec._fields):
            if rec.product_id and rec.activity_id:
                raise UserError(_('Select both Product and '
                                  'Activity is prohibited'))
        if not rec.product_id and not rec.activity_id:
            return False
        # Only create analytic if not exists yet
        Analytic = self.env['account.analytic.account']
        domain = self.get_analytic_search_domain(rec)
        if rec.product_id:
            domain.append(('type', '=', 'product'))
        elif rec.activity_id:
            domain.append(('type', '=', 'activity'))
        analytics = Analytic.search(domain)
        if not analytics:
            vals = dict((x[0], x[2]) for x in domain)
            vals['name'] = rec.product_id.name or rec.activity_id.name
            vals['type'] = rec.product_id and 'product' or 'activity'
            return Analytic.create(vals)
        else:
            return analytics[0]
