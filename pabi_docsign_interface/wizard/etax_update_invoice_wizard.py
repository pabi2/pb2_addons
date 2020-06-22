# -*- coding: utf-8 -*-
# © 2020 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import xmlrpclib
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class eTaxUpdateInvoiceWizard(models.TransientModel):
    _name = 'etax.update.invoice'
    _inherit = 'etax.invoice'

    reason_update = fields.Selection([
        ('DBNG01', 'มีการเพิ่มราคาค่าสินค้า (สินค้าเกินกว่าจำนวนที่ตกลงกัน)'),
        ('DBNG02', 'คำนวณราคาสินค้า ผิดพลาดต่ำกว่าที่เป็นจริง'),
        ('DBNG99', 'เหตุอื่น (ระบุสาเหตุ)'),
        ('DBNS01', 'การเพิ่มราคาค่าบริการ (บริการเกินกว่าข้อกำหนดทตกลงกัน)'),
        ('DBNS02', 'คำนวณราคาค่าบริการ ผิดพลาดต่ำกว่าที่เป็นจริง'),
        ('DBNS99', 'เหตุอื่น (ระบุสาเหตุ)'),
        ('CDNG01', 'ลดราคาสินค้าที่ขาย (สินค้าผิดข้อกำหนดที่ตกลงกัน)'),
        ('CDNG02', 'สินค้าชำรุดเสียหาย'),
        ('CDNG03', 'สินค้าขาดจำนวนตามที่ตกลงซื้อขาย'),
        ('CDNG04', 'คำนวณราคาสินค้าผิดพลาดสูงกว่าที่เป็นจริง'),
        ('CDNG05', 'รับคืนสินค้า (ไม่ตรงตามคำพรรณนา)'),
        ('CDNG99', 'เหตุอื่น (ระบุสาเหตุ)'),
        ('CDNS01', 'ลดราคาค่าบริการ (บริการผิดข้อกำหนดที่ตกลงกัน)'),
        ('CDNS02', 'ค่าบริการขาดจำนวน'),
        ('CDNS03', 'คำนวณราคาค่าบริการผิดพลาดสูงกว่าที่เป็นจริง'),
        ('CDNS04', 'บอกเลิกสัญญาบริการ'),
        ('CDNS99', 'เหตุอื่น (ระบุสาเหตุ)'),
        ('TIVC01', 'ชื่อผิด'),
        ('TIVC02', 'ที่อยู่ผิด'),
        ('TIVC99', 'เหตุอื่น (ระบุสาเหตุ)'),
        ('RCTC01', 'ชื่อผิด'),
        ('RCTC02', 'ที่อยู่ผิด'),
        ('RCTC03', 'รับคืนสินค้า / ยกเลิกบริการ ทั้งจำนวน (ระบุจำนวนเงิน) บาท'),
        ('RCTC04', 'รับคืนสินค้า / ยกเลิกบริการ บางส่วนจำนวน (ระบุจำนวนเงิน) บาท'),
        ('RCTC99', 'เหตุอื่น (ระบุสาเหตุ)'),
    ])

    # @api.onchange('form_name')
    # def _onchange_form_name(self):
    #     # debit note
    #     if self.form_name == '80':
    #         self.reason_update
