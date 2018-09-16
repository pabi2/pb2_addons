# -*- coding: utf-8 -*-
import logging
from openerp import models, api, _
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def test_create_or_update_partner(self):
        """ Example dict, following are availabe fields """
        data_dict = {
            'vat': u'1412920212114',  # 1st matched criteria
            'taxbranch': u'12125',  # 2nd matched criteria
            # Name
            'name': u'Cust 2',  # 3rd matched criteria
            'name_en': u'Cust 2',  # optional
            'name_th': u'ลูกค้า 2',  # Optional
            # --
            'customer': True,
            'supplier': False,
            'title': u'Mr.',
            'category_id': u'supplier-ภาคเอกชน',
            'street': u'14 ซอย 12 ถนน นราธิวาส',
            'street2': u'---',
            'country_id': u'Thailand',
            'province_id': u'จ.สระบุรี',
            'district_id': u'อ.ดอนพุด',
            'township_id': False,
            'zip': u'18210',
            'property_payment_term': u'Immediate Payment',
            'property_supplier_payment_term': u'Immediate Payment',
        }
        return self.create_or_update_partner(data_dict)

    @api.model
    def _find_partner_id(self, data_dict):
        """ Find partner based on vat, taxbranch and name """
        criterias = {'vat': data_dict.get('vat', False),
                     'taxbranch': data_dict.get('taxbranch', False),
                     'name': data_dict.get('taxbranch', False)}
        vat = criterias.get('vat', False)
        taxbranch = criterias.get('taxbranch', False)
        name = criterias.get('name', False)
        domains = []
        if vat and taxbranch:  # More specific to less specific
            domains.append([('vat', '=', vat),
                            ('taxbranch', '=', taxbranch)])
        if vat and not taxbranch:
            domains.append([('vat', '=', vat)])
        if name:
            domains.append([('name', 'ilike', name)])
        for domain in domains:
            res = self.search(domain)
            if len(res) == 1:
                return res
            elif len(res) > 1:
                raise ValidationError(
                    _('Multiple match on same partner criterias: %s') %
                    (criterias, ))
        return False

    @api.model
    def _pre_write_partner_data(self, data_dict):
        m2o_fields = {  # Fields needs changes to database id
            'title': 'res.partner.title',
            'category_id': 'res.partner.category',
            'country_id': 'res.country',
            'province_id': 'res.country.province',
            'district_id': 'res.country.district',
            'township_id': 'res.country.township',
            'property_payment_term': 'account.payment.term',
            'property_supplier_payment_term': 'account.payment.term',
        }
        for key, value in data_dict.iteritems():
            if key in m2o_fields:
                if not value:
                    continue
                res = self.env[m2o_fields[key]].name_search(value)
                if res:
                    data_dict[key] = res[0][0]
                else:
                    raise ValidationError(_('%s = %s is not valid!') %
                                          (key, value))
                data_dict[key] = res and res[0][0] or False
        return data_dict

    @api.model
    def _pre_load_partner_data(self, data_dict):
        if 'name_en' in data_dict:
            data_dict.pop('name_en')
        if 'name_th' in data_dict:
            data_dict.pop('name_th')
        # Boolean field must be str
        if 'customer' in data_dict:
            data_dict['customer'] = str(data_dict['customer'])
        if 'supplier' in data_dict:
            data_dict['supplier'] = str(data_dict['supplier'])
        return data_dict

    @api.model
    def create_or_update_partner(self, data_dict):
        _logger.info('create_or_update_partner(), input: %s' % data_dict)
        res = {}
        try:
            # Temp translation fields
            name_en = data_dict.get('name_en', False)
            name_th = data_dict.get('name_th', False)
            # Find matching first, before create or update
            partner = self._find_partner_id(data_dict)
            if partner:  # Found, do the update
                data_dict = self._pre_write_partner_data(data_dict)
                partner.write(data_dict)
                res = {
                    'is_success': True,
                    'result': {'id': partner.id},
                    'messages': _('Record updated successfully'),
                }
            else:
                data_dict = self._pre_load_partner_data(data_dict)
                res = self.env['pabi.utils.ws'].create_data(self._name,
                                                            data_dict)
                partner = self.browse(res['result']['id'])
            # Update translation, if any
            if name_en:
                partner.with_context(lang='en_US').write({'name': name_en})
            if name_th:
                partner.with_context(lang='th_TH').write({'name': name_th})
        except Exception, e:
            res = {
                'is_success': False,
                'result': False,
                'messages': _(str(e)),
            }
            self._cr.rollback()
        _logger.info('create_or_update_partner(), output: %s' % res)
        return res
