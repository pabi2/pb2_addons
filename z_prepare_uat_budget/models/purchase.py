# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def prepare_data(self, action, datas=False):
        action_list = ['copy_po_with_new_section']
        # Sample for action = copy_po_with_new_section
        # For ศก
        sample_datas = {
            'copy_po_with_new_section': {
                # สก
                'PO18000425': ['105068', '105056', '102002', '102001',
                               '103014', '105064', '104008', '105070'],
                # ศว
                'PO18000427': ['305017', '305013', '302007', '301074',
                               '305007', '302005'],
                # ศอ
                'PO18000428': ['405021', '405006'],
                # ศช
                'PO18000426': ['205006', '201051', '201003'],
                # ศน
                'PO18000429': ['605008', '605016', '601012',
                               '105015', '105017', '105014']}
        }

        if action not in action_list:
            raise ValidationError('%s is not a valid action')

        if not datas:
            datas = sample_datas[action]

        for po in datas.keys():
            purchase = self.search([('name', '=', po)])
            if not purchase:
                raise ValidationError('%s not found' % po)
            for s in datas[po]:
                section = self.env['res.section'].search([('code', '=', s)])
                p = purchase.with_context(new_section_id=section.id).copy()
                p.signal_workflow('purchase_confirm')
                p.signal_workflow('purchase_approve')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def create(self, vals):
        if self._context.get('new_section_id', False):
            vals['section_id'] = self._context.get('new_section_id')
        return super(PurchaseOrderLine, self).create(vals)
