# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vat = fields.Char(
        string='Tax ID',
        size=13,
        copy=False,
    )
    taxbranch = fields.Char(
        string='Tax Branch ID',
        size=5,
        copy=False,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        sring='Employee',
        compute='_compute_employee_id',
        help="Employee represent this partner (if any)",
    )

    @api.multi
    @api.depends()
    def _compute_employee_id(self):
        for partner in self:
            self._cr.execute("""
            select id from hr_employee where resource_id in
            (select id from resource_resource where user_id =
            (select id from res_users where partner_id = %s))
            """, (partner.id,))
            res = self._cr.fetchone()
            partner.employee_id = res and res[0] or False

    @api.one
    @api.constrains('vat')
    def _check_vat(self):
        if self.vat and len(self.vat) != 13:
            raise ValidationError(
                _("Tax ID must be 13 digits!"))

    @api.one
    @api.constrains('taxbranch')
    def _check_taxbranch(self):
        if self.taxbranch and len(self.taxbranch) != 5:
            raise ValidationError(
                _("Tax Branch must be 5 digits"))

    @api.one
    @api.constrains('name', 'supplier', 'customer')
    def _check_partner_name(self):
        count = self.search_count([('name', '=', self.name)])
        if count > 1:
            raise ValidationError("Partner Name must be unique!")

    @api.one
    @api.constrains('vat', 'taxbranch')
    def _check_vat_taxbranch_unique(self):
        if self.vat or self.taxbranch:
            count = self.search_count(
                ['|', ('parent_id', '=', False),
                 ('is_company', '=', True),
                 ('vat', '=', self.vat),
                 ('taxbranch', '=', self.taxbranch)])
            if count > 1:
                raise ValidationError(
                    _("Tax ID + Tax Branch ID must be unique!"))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
