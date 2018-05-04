# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models


class PabiContractDetailReport(models.Model):
    _name = 'pabi.contract.detail.report'
    _description = 'Pabi Contract Detail Report'
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
            select
            po.id as po_id,
            pcon.name as contract_no,
            pcon.postdating as post_contract_date,
            rp.name as supplier,
            pol.name as product_desc,
            po.amount_total as amount_total,
            rc.name as currency,
            swh.name as destination,
            pm.name as purchase_method,
            pm.id as purchase_method_id,
            pcht.id as purchase_type_id,
            pcon.start_date as date_start,
            pcon.end_date as date_end,
            max(pip.installment) as plan_count
            from purchase_order po
            left join res_partner rp on rp.id = po.partner_id
            left join res_currency rc on rc.id = po.currency_id
            left join purchase_invoice_plan pip on pip.order_id = po.id
            left join purchase_requisition cfb on cfb.id = po.requisition_id
            left join purchase_type pcht on pcht.id = cfb.purchase_type_id
            left join purchase_method pm on pm.id = cfb.purchase_method_id
            left join purchase_contract pcon on pcon.poc_code = po.name
            left join stock_picking_type spt on spt.id = po.picking_type_id
            left join stock_warehouse swh on swh.id = spt.warehouse_id
            left join purchase_order_line pol on pol.order_id = po.id
            left join product_template pt on pt.id = pol.product_id
            where
            po.order_type = 'purchase_order'
            and po.use_invoice_plan = true
            and po.state in ('approved','done')
            group by
            po.id,
            pcon.postdating,
            rp.name,
            pol.name,
            po.amount_total,
            rc.name,
            swh.name,
            pm.name,
            pm.id,
            pcht.id,
            pcon.name,
            pcon.start_date,
            pcon.end_date
        )""" % (self._table, ))
