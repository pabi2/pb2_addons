-- This query find PO -> INV/IN that do not return budget properly

select number, amount_untaxed, (inv_actual + stock_actual + po_commit) consumed from (
select purchase_id, number, amount_untaxed, coalesce(po_commit, 0.0) po_commit,
	coalesce(inv_actual, 0.0) inv_actual, coalesce(stock_actual, 0.0) stock_actual
from (select id purchase_id, name number, amount_untaxed,
	-- po commit
	(select sum(-amount)
	 from account_analytic_line aal
	 where aal.purchase_id = po.id) po_commit,
	-- invoice actual
	(select sum(-amount) from account_analytic_line aal where aal.move_id in
	  (select aml.id from account_move_line aml join account_move am on am.id = aml.move_id
	   join account_invoice av on (av.move_id = am.id or av.cancel_move_id = am.id)
		join purchase_order po2 on po2.name = av.source_document
		where po2.id = po.id)) inv_actual,
	-- stock actual
	(select sum(-amount) from account_analytic_line aal where aal.move_id in
	  (select aml.id from account_move_line aml join account_move am on am.id = aml.move_id
		join stock_picking pick on pick.name = am.document
		join purchase_order po2 on po2.name = pick.origin
		where po2.id = po.id)) stock_actual

from purchase_order po where order_type = 'purchase_order'
-- Not COD case where its invoice is paid without number
and po.id not in (select purchase_id from purchase_invoice_rel
		  where invoice_id in (
			select id from account_invoice
			where state != 'draft' and number is null))
and state not in ('draft', 'cancel') and currency_id = 140
) a ) b
where (inv_actual + po_commit + stock_actual) != amount_untaxed
