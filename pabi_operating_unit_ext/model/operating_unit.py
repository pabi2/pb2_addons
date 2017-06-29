# -*- coding: utf-8 -*-
from openerp import api, models, fields, _
from openerp.exceptions import ValidationError


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    access_all_operating_unit = fields.Boolean(
        string="Access All Operating Unit",
        copy=False,
        help="With this checkbox checked, users in this Operating Unit "
        "will have access to all other Operating Unit too")
    user_ids = fields.Many2many(
        'res.users',
        'operating_unit_users_rel',
        'poid', 'user_id',
        string='Users',
    )
    org_ids = fields.One2many(
        'res.org',
        'operating_unit_id',
        string='Orgs',
        readonly=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        compute='_compute_org_id',
        store=True,
        readonly=True,
    )

    @api.multi
    @api.depends('org_ids.operating_unit_id')
    def _compute_org_id(self):
        for rec in self:
            if rec.org_ids:
                if len(rec.org_ids) > 1:
                    raise ValidationError(_('Org and OU must be 1-to-1'))
                rec.org_id = rec.org_ids[0]
            else:
                rec.org_id = False

    @api.multi
    def write(self, vals):
        res = super(OperatingUnit, self).write(vals)
        if 'access_all_operating_unit' in vals:
            for ou in self:
                ou.user_ids.write({})  # Write to clear cache
        return res
