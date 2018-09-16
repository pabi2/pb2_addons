# -*- coding: utf-8 -*-
from openerp import models, fields


class AssetPurchaseMethod(models.Model):
    _name = 'asset.purchase.method'

    """ One/Many purhase methods from CFB, can mapped to AssetPurchaseMethod,
    Asset Purchase Method ==> Purchase Method
    -----------------------------------------
    วิธีตกลงราคา    -> วิธีตกลงราคา
    วิธีสอบราคา     -> วิธีสอบราคา
    วิธีประกวดราคา	-> วิธีประกวดราคา, วิธีตกลง,
                     วิธีคัดเลือกแบบจำกัดข้อกำหนด, วิธีคัดเลือก
    วิธีพิเศษ	     -> วิธีพิเศษ
    วิธีกรณีพิเศษ	 ->  วิธีกรณีพิเศษ
    วิธีe-Auction	->  วิธีประกวดราคาด้วยวิธีการอิเล็กทรอนิกส์
    วิธีฉุกเฉิน (select in IN)
    รับบริจาค (select in IN)
    ของแถม (select in IN)
    รับโอน (select in IN)
    อื่น ๆ (case AITs with mixed method, merged to new Asset)

    """
    name = fields.Char(
        string='Name',
        required=True,
        size=500,
    )
    code = fields.Char(
        string='Code',
        required=True,
        size=100,
    )
    direct = fields.Boolean(
        string='Direct Receive',
        default=False,
    )


class PurchaseMethod(models.Model):
    _inherit = 'purchase.method'

    asset_purchase_method_id = fields.Many2one(
        'asset.purchase.method',
        string='Asset Purchase Method',
        readonly=False,
        help="When asset is created, purchase method here, will be mapped to "
        "the Asset Purchase Method of asset."
    )
