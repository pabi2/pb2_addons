# -*- coding: utf-8 -*-
from openerp import models, fields, api

WHT_CERT_INCOME_TYPE = [('1', 'เงินเดือน ค่าจ้าง ฯลฯ 40 (1)'),
                        ('2', 'เบี้ยประชุม ประเมินผล ฯลฯ 40(2)'),
                        ('3', 'ค่าลิขสิทธิ์ ฯลฯ 40(3)'),
                        ('5', 'เงินรางวัล ค่าเช่า ค่าโฆษณา ฯลฯ'),
                        ('6', 'ธุรกิจพาณิชย์ เกษตร อื่นๆ')]


class WhtCertTaxLine(models.Model):
    _inherit = 'wht.cert.tax.line'

    wht_cert_income_type = fields.Selection(
        WHT_CERT_INCOME_TYPE,
        string='Type of Income',
        required=True,
    )

    @api.onchange('wht_cert_income_type')
    def _onchange_wht_cert_income_type(self):
        if self.wht_cert_income_type:
            select_dict = dict(WHT_CERT_INCOME_TYPE)
            self.wht_cert_income_desc = select_dict[self.wht_cert_income_type]
        else:
            self.wht_cert_income_desc = False
