-- Find taxbranch of move_line does not match with taxbranch of tax_detail
select aml.id move_line_id, aml.taxbranch_id aml_taxbranch,
	t.id tax_detail_id, t.taxbranch_id td_taxbranch
from account_tax_detail t
join account_move_line aml on aml.move_id = t.ref_move_id
where t.tax_sequence_display is not null
and t.taxbranch_id != aml.taxbranch_id
and t.voucher_tax_id is null and invoice_tax_id is null -- Not from invoice/payment
and doc_type = 'sale' -- Sales Tax
and section_id = '12' -- PTEC
order by move_line_id

-- Update from all moveline in same move_id to 9
update account_move_line set taxbranch_id = 9 where id in (
	select aml.id
	from account_tax_detail t
	join account_move_line aml on aml.move_id = t.ref_move_id
	where t.tax_sequence_display is not null
	and t.taxbranch_id != aml.taxbranch_id
	and t.voucher_tax_id is null and invoice_tax_id is null -- Not from invoice/payment
	and doc_type = 'sale' -- Sales Tax
	and section_id = '12' -- PTEC
)
