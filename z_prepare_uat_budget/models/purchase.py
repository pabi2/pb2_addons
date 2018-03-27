# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def prepare_data(self, action, datas=False):
        action_list = ['copy_po_with_new_section',
                       'copy_po_with_new_project']

        if action not in action_list:
            raise ValidationError('%s is not a valid action')

        if not datas:
            datas = self._get_sample_datas(action)

        for po in datas.keys():
            purchase = self.search([('name', '=', po)])
            if not purchase:
                raise ValidationError('%s not found' % po)
            for s in datas[po]:
                if action == 'copy_po_with_new_section':
                    section = \
                        self.env['res.section'].search([('code', '=', s)])
                    p = purchase.with_context(new_section_id=section.id).copy()
                    p.signal_workflow('purchase_confirm')
                    p.signal_workflow('purchase_approve')
                if action == 'copy_po_with_new_project':
                    project = \
                        self.env['res.project'].search([('code', '=', s)])
                    p = purchase.with_context(new_project_id=project.id).copy()
                    p.signal_workflow('purchase_confirm')
                    p.signal_workflow('purchase_approve')

    def _get_sample_datas(self, action):
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
                               '105015', '105017', '105014']},
            'copy_po_with_new_project': {
                'PO18000484': [  # project = P1450891
                    'P1650064',
                    'P1550663',
                    'P1650748',
                    'P1650749',
                    'P1650700',
                    'P1650475',
                    'P1650785',
                    'P1350441',
                    'P1650666',
                    'P1551680',
                    'P1350420',
                    'P1451356',
                    'P1350438',
                    'P1450383',
                    'P1630004',
                    'P1350429',
                    'P1551380',
                    'P1550583',
                    'P1650669',
                    'P1650596',
                    'P1650395',
                    'P1450015',
                    'P1550967',
                    'P1550571',
                    'P1300882',
                    'P1450883',
                    'P1450962',
                    'P1551326',
                    'P1450907',
                    'P1450804',
                    'P1551548',
                    'P1551585',
                    'P1450650',
                    'P1551647',
                    'P1551493',
                    'P1551728',
                    'P1551729',
                    'P1650049',
                    'P1650297',
                    'P1550633',
                    'P1301089',
                    'P1550450',
                    'P1551400',
                    'P1451231',
                    'P1550617',
                    'P1550684',
                    'P1201973',
                    'P1201970',
                    'P1300360',
                    'P1450766',
                    'P1201968',
                    'P1201967',
                    'P1550665',
                    'P1551170',
                    'P1301090',
                    'P1300750',
                    'P1450055',
                    'P0040209',
                    'P1650746',
                    'P1551295',
                    'P1551537',
                    'P1451152',
                    'P1451124',
                    'P1451121',
                    'P1451138',
                    'P1202251',
                    'P1101128',
                    'P1101144',
                    'P1300066',
                    'P1551372',
                    'P1551342',
                    'P1551301',
                    'P1551047',
                    'P1450824',
                    'P1350040',
                    'P1350045',
                    'P1551428',
                    'P1650571',
                    'P1551638',
                    'P1650063',
                    'P1650650',
                    'P1451097',
                    'P1550605',
                    'P1650732',
                    'P1551171',
                    'P1551177',
                    'P1650410',
                    'M15014',
                    'M15015',
                    'M16007',
                    'M15013',
                    'P1551526',
                    'P1550309',
                    'P1551717',
                    'P1010661',
                    'P1650774',
                    'P1300697',
                    'P1650425',
                    'P1551107',
                    'P1450604',
                    'P1451313',
                    'P1650142',
                    'P1650742',
                    'P1650767',
                    'P1350137',
                    'P1450592',
                    'P1551062',
                    'P1651210',
                    'P1450891-PH2',
                    'P1650064-PH2',
                    'P1550663-PH2',
                    'P1650748-PH2',
                    'P1650749-PH2',
                    'P1650700-PH2',
                    'P1650475-PH2',
                    'P1650785-PH2',
                    'P1350441-PH2',
                    'P1650666-PH2',
                    'P1551680-PH2',
                    'P1350420-PH2',
                    'P1451356-PH2',
                    'P1350438-PH2',
                    'P1450383-PH2',
                    'P1630004-PH2',
                    'P1350429-PH2',
                    'P1551380-PH2',
                    'P1550583-PH2',
                    'P1650669-PH2',
                    'P1650596-PH2',
                    'P1650395-PH2',
                    'P1450015-PH2',
                    'P1550967-PH2',
                    'P1550571-PH2',
                    'P1300882-PH2',
                    'P1450883-PH2',
                    'P1450962-PH2',
                    'P1551326-PH2',
                    'P1450907-PH2',
                    'P1450804-PH2',
                    'P1551548-PH2',
                    'P1551585-PH2',
                    'P1450650-PH2',
                    'P1551647-PH2',
                    'P1551493-PH2',
                    'P1551728-PH2',
                    'P1551729-PH2',
                    'P1650049-PH2',
                    'P1650297-PH2',
                    'P1550633-PH2',
                    'P1301089-PH2',
                    'P1550450-PH2',
                    'P1551400-PH2',
                    'P1451231-PH2',
                    'P1550617-PH2',
                    'P1550684-PH2',
                    'P1201973-PH2',
                    'P1201970-PH2',
                    'P1300360-PH2',
                    'P1450766-PH2',
                    'P1201968-PH2',
                    'P1201967-PH2',
                    'P1550665-PH2',
                    'P1551170-PH2',
                    'P1301090-PH2',
                    'P1300750-PH2',
                    'P1450055-PH2',
                    'P0040209-PH2',
                    'P1650746-PH2',
                    'P1551295-PH2',
                    'P1551537-PH2',
                    'P1451152-PH2',
                    'P1451124-PH2',
                    'P1451121-PH2',
                    'P1451138-PH2',
                    'P1202251-PH2',
                    'P1101128-PH2',
                    'P1101144-PH2',
                    'P1300066-PH2',
                    'P1551372-PH2',
                    'P1551342-PH2',
                    'P1551301-PH2',
                    'P1551047-PH2',
                    'P1450824-PH2',
                    'P1350040-PH2',
                    'P1350045-PH2',
                    'P1551428-PH2',
                    'P1650571-PH2',
                    'P1551638-PH2',
                    'P1650063-PH2',
                    'P1650650-PH2',
                    'P1451097-PH2',
                    'P1550605-PH2',
                    'P1650732-PH2',
                    'P1551171-PH2',
                    'P1551177-PH2',
                    'P1650410-PH2',
                    'M15014-PH2',
                    'M15015-PH2',
                    'M16007-PH2',
                    'M15013-PH2',
                    'P1551526-PH2',
                    'P1550309-PH2',
                    'P1551717-PH2',
                    'P1010661-PH2',
                    'P1650774-PH2',
                    'P1300697-PH2',
                    'P1650425-PH2',
                    'P1551107-PH2',
                    'P1450604-PH2',
                    'P1451313-PH2',
                    'P1650142-PH2',
                    'P1650742-PH2',
                    'P1650767-PH2',
                    'P1350137-PH2',
                    'P1450592-PH2',
                    'P1551062-PH2',
                    'P1651210-PH2',
                ]
            }
        }
        return sample_datas[action]


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def create(self, vals):
        if self._context.get('new_section_id', False):
            vals['section_id'] = self._context.get('new_section_id')
        if self._context.get('new_project_id', False):
            vals['project_id'] = self._context.get('new_project_id')
        return super(PurchaseOrderLine, self).create(vals)
