-- Update period of account_tax_detail to follow account_move_line
update account_tax_detail set report_period_id = 41, period_id = 41 where id in (
-- Find tax_detail with wrong period
select t.id
from account_tax_detail t
join account_move_line aml on aml.move_id = t.ref_move_id
where t.tax_sequence_display is not null
and t.period_id != aml.period_id
and t.voucher_tax_id is null and invoice_tax_id is null -- Not from invoice/payment
and doc_type = 'sale' -- Sales Tax
and t.period_id = 42
order by move_line_id)
