# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models


class PabiPurchaseSummarizeReport(models.Model):
    _name = 'pabi.purchase.summarize.report'
    _description = 'Pabi Purchase Summarize Report'
    _auto = False

    # purchase_type_id = fields.Many2one(
    #     'purchase.type',
    #     string='Purchase Type',
    # )
    # purchase_method_id = fields.Many2one(
    #     'purchase.method',
    #     string='Purchase Type',
    # )
    # date_from = fields.Date(string='Contract Start Date')
    # date_to = fields.Date(string='Contract End Date')

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT string_agg(po.id::varchar,',') po_id,
        pd.name as pd_number,
        CONCAT((SELECT pt.name FROM purchase_type pt WHERE
            pt.id = pd.purchase_type_id),' ',pd.objective) objective,
        (SELECT COUNT(*) FROM purchase_requisition_line pdl
        WHERE pdl.requisition_id = pd.id) qty,
        pd.amount_total,
        pm.name as method,
        (SELECT CONCAT(COALESCE(rpt.name || ' ',''),rp.name)
            FROM res_partner rp
        LEFT JOIN res_partner_title rpt
        ON rpt.id = rp.title
        WHERE rp.id = selected_po.partner_id) as rfq_supplier,
        selected_po.amount_total as rfq_amount_total,
        (SELECT psr.name FROM purchase_order rfq
        LEFT JOIN purchase_select_reason psr ON psr.id = rfq.select_reason
        WHERE rfq.order_type = 'quotation' AND
            rfq.order_id = selected_po.id) reason,
        pd.create_date::date

        FROM purchase_requisition pd
        LEFT JOIN operating_unit ou
        ON ou.id = pd.operating_unit_id
        LEFT JOIN purchase_method pm
        ON pm.id = pd.purchase_method_id
        LEFT JOIN purchase_price_range ppr
        ON ppr.id = pd.purchase_price_range_id
        LEFT JOIN purchase_order po
        ON po.requisition_id = pd.id AND po.order_type = 'quotation'
        LEFT join purchase_order selected_po
        ON selected_po.requisition_id = pd.id AND
            selected_po.order_type LIKE 'purchase_order' AND
            selected_po.state NOT LIKE 'cancel'
        WHERE pd.state = 'done'
        GROUP BY pd.id, pd.name, pd.objective, pd.amount_total, pm.name,
            selected_po.partner_id, selected_po.amount_total,
        selected_po.id
        )""" % (self._table, ))
