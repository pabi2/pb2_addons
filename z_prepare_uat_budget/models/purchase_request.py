# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import ValidationError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    line_ids = fields.One2many(
        'purchase.request.line',
        copy=True,
    )

    @api.model
    def prepare_data(self, action, datas=False):
        action_list = ['copy_pr_with_new_section']
        # Sample for action = copy_po_with_new_section
        # For ศก
        sample_datas = {
            'copy_pr_with_new_section': {
                # สก
                'PR18000053': ['105068', '105056', '102002', '102001',
                               '103014', '105064', '104008', '105070'],
                # ศว
                'PR18000054': ['305017', '305013', '302007', '301074',
                               '305007', '302005'],
                # ศอ
                'PR18000055': ['405021', '405006'],
                # ศช
                'PR18000056': ['205006', '201051', '201003'],
                # ศน
                'PR18000057': ['605008', '605016', '601012',
                               '105015', '105017', '105014']}
        }

        if action not in action_list:
            raise ValidationError('%s is not a valid action')

        if not datas:
            datas = sample_datas[action]

        for pr in datas.keys():
            purchase_request = self.search([('name', '=', pr)])
            if not purchase_request:
                raise ValidationError('%s not found' % pr)
            for s in datas[pr]:
                section = self.env['res.section'].search([('code', '=', s)])
                p = purchase_request.\
                    with_context(new_section_id=section.id).copy()
                p.button_to_approve()


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    @api.model
    def create(self, vals):
        if self._context.get('new_section_id', False):
            vals['section_id'] = self._context.get('new_section_id')
        return super(PurchaseRequestLine, self).create(vals)
