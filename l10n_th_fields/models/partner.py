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
        string='Employee',
        compute='_compute_employee_id',
        search='_search_employee_id',
        help="Employee represent this partner (if any)",
    )

    @api.model
    def _search_employee_id(self, operator, value):
        users = self.env['res.users'].search(['|', ('name', 'ilike', value),
                                              ('login', 'ilike', value)])
        return [('id', 'in', users.mapped('partner_id')._ids)]

    @api.multi
    def _compute_employee_id(self):
        for partner in self:
            self._cr.execute("""
            select id from hr_employee where resource_id in
            (select id from resource_resource where user_id =
            (select id from res_users where partner_id = %s))
            """, (partner.id,))
            res = self._cr.fetchone()
            partner.employee_id = res and res[0] or False

    @api.multi
    @api.constrains('vat')
    def _check_vat(self):
        for rec in self:
            if rec.vat and len(rec.vat) != 13:
                raise ValidationError(
                    _("Tax ID must be 13 digits!"))

    @api.multi
    @api.constrains('taxbranch')
    def _check_taxbranch(self):
        for rec in self:
            if rec.taxbranch and len(rec.taxbranch) != 5:
                raise ValidationError(
                    _("Tax Branch must be 5 digits"))

    @api.multi
    @api.constrains('name', 'supplier', 'customer')
    def _check_partner_name(self):
        for rec in self:
            count = len(self.search([('name', '=', rec.name)])._ids)
            if count > 1:
                raise ValidationError("Partner Name must be unique!")

    @api.multi
    @api.constrains('vat', 'taxbranch')
    def _check_vat_taxbranch_unique(self):
        for rec in self:
            if rec.vat or rec.taxbranch:
                count = len(self.search(
                    ['|', ('parent_id', '=', False),
                     ('is_company', '=', True),
                     ('vat', '=', self.vat),
                     ('taxbranch', '=', self.taxbranch)])._ids)
                if count > 1:
                    raise ValidationError(
                        _("Tax ID + Tax Branch ID must be unique!"))
