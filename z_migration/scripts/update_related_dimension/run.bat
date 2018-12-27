@echo off
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" hr.expense.line data_section.csv
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" purchase.order.line data_section.csv
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" purchase.request.line data_section.csv
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" purchase.requisition.line data_section.csv
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" account.asset data_section.csv
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" account.invoice.line data_section.csv
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" stock.move data_section.csv
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" procurement.order data_section.csv
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" account.voucher.multiple.reconcile data_section.csv
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" account.bank.receipt.multiple.reconcile data_section.csv
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" account.asset.adjust.line data_section.csv
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" account.asset.adjust.asset_to_expense data_section.csv
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" account.asset.adjust.expense_to_asset data_section.csv
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" stock.inventory.line data_section.csv
python "D:\share\z_migration\scripts\update_related_dimension\update_dimension.py" pabi.import.journal.entries.line data_section.csv
pause
