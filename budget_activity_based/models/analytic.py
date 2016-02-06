# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from lxml import etree
from openerp import api, fields, models
from openerp.osv.orm import setup_modifiers


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
            domain = Analytic.get_analytic_search_domain(analytic)
            vals.update(dict((x[0], x[2]) for x in domain))
        return super(AccountAnalyticLine, self).create(vals)


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    type = fields.Selection(
        [('view', 'Analytic View'),
         ('normal', 'Analytic Account'),
         ('activity', 'Activity'),
         ('contract', 'Contract or Project'),
         ('template', 'Template of Contract')]
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
        domain.append(('type', '=', 'activity'))
        analytics = self.env['account.analytic.account'].search(domain)
        if analytics:
            #analytics.ensure_one()
            return analytics[0]
        return False

    @api.model
    def create_matched_analytic(self, rec):
        # Only create analytic if not exists yet
        Analytic = self.env['account.analytic.account']
        domain = self.get_analytic_search_domain(rec)
        domain.append(('type', '=', 'activity'))
        analytics = Analytic.search(domain)
        if not analytics:
            vals = dict((x[0], x[2]) for x in domain)
            vals['name'] = rec.activity_id.name
            vals['type'] = 'activity'
            return Analytic.create(vals)
        else:
            #analytics.ensure_one()
            return analytics[0]


