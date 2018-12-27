# -*- coding: UTF-8 -*-
"""
This method change all purchase.order.line dimension
"""
import sys
import os
import csv
try:
    budget_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.dirname(budget_path)
    migration_path = os.path.dirname(script_path)
    controller_path = '%s/controller' % migration_path
    sys.path.insert(0, controller_path)
    from connection import connection
    from connection import xmlrpc_models, xmlrpc_common, xmlrpc_uid, xmlrpc_database, xmlrpc_password, get_data
    from untility import readCSV
    import log
except Exception:
    pass

# ชื่อไฟล์ CSV ต้องชื่อนี้เท่านั้น
List_CSVFile = [
	'data_section.csv',
	'data_project.csv',
	'data_invest_asset.csv', 
	'data_invest_construction_phase.csv',
	'data_personnel_costcenter.csv'
]

# Config
UseCSVFile = True	# True: Use CSV, False: Manual

# Declare variable
Script = False
ModelTarget = False
CSVFile = False
d = {}

if len(sys.argv) == 3:
	Script, ModelTarget, CSVFile = sys.argv
	if CSVFile not in List_CSVFile and CSVFile != '-all':
		print "Wrong file name csv of arguments!"
		print "Usage: required file name \n" + "\n".join(List_CSVFile)
		exit()
else:
	print "Wrong number of arguments!"
	print "Usage: python script.py model_name file_csv"
	exit()

# Model
Budget = connection.get_model('account.budget')
ModelLine = connection.get_model(ModelTarget)

# Updates list for all structure from -> to (by code)
##################### READ FILE CSV OR MANUAL ################################ 
if(UseCSVFile):
	# Use CSV
	d = readCSV(CSVFile)
else:
	# Manual
	d = {
		'section_id': {'XXX': 'YYY'},
		'project_id': {'XXX': 'YYY'},
		'invest_asset_id': {'XXX': 'YYY'},
		'invest_construction_phase_id': {'XXX': 'YYY'},
		'personnel_costcenter_id': {'XXX': 'YYY'},
	}
#############################################################
# Domain - get only relevant lines
dom = ['|', '|', '|', '|',
       ('section_id.code', 'in', d.get('section_id', {}).keys()),
       ('project_id.code', 'in', d.get('project_id', {}).keys()),
       ('invest_asset_id.code', 'in', d.get('invest_asset_id', {}).keys()),
       ('invest_construction_phase_id.code', 'in', d.get('invest_construction_phase_id', {}).keys()),
       ('personnel_costcenter_id.code', 'in', d.get('personnel_costcenter_id', {}).keys()), ]

# hr.expense.line
# [NOT RUN] hr.salary.line
# purchase.order.line
# purchase.request.line
# purchase.requisition.line
# account.asset
# [NOT SURE] account.analytic.line
# account.invoice.line
# stock.move
# [NOT RUN] sale.order.line
# [NOT RUN] account.model.line
# procurement.order
# account.voucher.multiple.reconcile
# account.bank.receipt.multiple.reconcile
# account.asset.adjust.line
# account.asset.adjust.asset_to_expense
# account.asset.adjust.expense_to_asset
# stock.inventory.line
# pabi.import.journal.entries.line

# Custom Domain

if d.get('section_id', {}).keys():
	dom += [('chart_view','=','unit_base')]

if ModelTarget == 'account.invoice.line':
	dom += [('invoice_id.state','not in',['paid','open','cancel'])]
	
elif ModelTarget == 'account.asset.adjust.line':
	dom += [('adjust_id.state','not in',['done','cancel'])]
elif ModelTarget == 'account.asset.adjust.asset_to_expense':
	dom += [('adjust_id.state','not in',['done','cancel'])]
elif ModelTarget == 'account.asset.adjust.expense_to_asset':
	dom += [('adjust_id.state','not in',['done','cancel'])]
	
elif ModelTarget == 'account.bank.receipt.multiple.reconcile':
	dom += [('bank_receipt_id.state','not in',['done'])]

elif ModelTarget == 'account.voucher.multiple.reconcile':
	dom += [('voucher_id.state','not in',['posted','cancel'])]

elif ModelTarget == 'pabi.import.journal.entries.line':
	dom += [('import_id.state','not in',['done','cancel'])]

elif ModelTarget == 'account.analytic.line':
	dom = ['|', '|', '|', '|',
       ('section_id.code', 'in', d.get('section_id', {}).keys()),
       ('project_id.code', 'in', d.get('project_id', {}).keys()),
       ('invest_asset_id.code', 'in', d.get('invest_asset_id', {}).keys()),
       ('invest_construction_phase_id.code', 'in', d.get('invest_construction_phase_id', {}).keys()),
       ('personnel_costcenter_id.code', 'in', d.get('personnel_costcenter_id', {}).keys()),
       ('move_id','=', False)]

# Search Budget
lines = ModelLine.search_read(dom, ['id'])

log_budget_names = [[], []]
logger = log.setup_custom_logger('UpdateDimension_' + ModelTarget)
logger.info('Start process model %s' % ModelTarget)
logger.info('Total budget: %s' % len(lines))
for line in lines:
	#run = 1
	#if ModelTarget == 'account.analytic.line':
	#	line_run = line.xxx_id or line.xxx2_id
	#	if not line_run:
	#		run = 0
    try:
		# Old Data
		section_o, project_o, invest_asset_o, invest_construction_phase_o, personnel_costcenter_o = get_data(xmlrpc_database,xmlrpc_uid,xmlrpc_password,ModelTarget, line['id'])

        #Budget.mock_update_related_dimension(
        #    ModelTarget, [line['id']],
        #    'account_analytic_id', d)

		# New Data
		section_n, project_n, invest_asset_n, invest_construction_phase_n, personnel_costcenter_n = get_data(xmlrpc_database,xmlrpc_uid,xmlrpc_password,ModelTarget, line['id'])

		log_budget_names[0].append(line['id'])
		logger.info('Pass: %s section(%s=>%s), project(%s=>%s), invest_asset(%s=>%s), invest_construction_phase(%s=>%s), personnel_costcenter(%s=>%s)' % (
			line['id'],
			section_o or '',
			section_n or '',
			project_o or '',
			project_n or '',
			invest_asset_o or '',
			invest_asset_n or '',
			invest_construction_phase_o or '',
			invest_construction_phase_n or '',
			personnel_costcenter_o or '',
			personnel_costcenter_n or ''
		))
    except Exception as ex:
        log_budget_names[1].append(line['id'])
        logger.error('Fail: %s (reason: %s)' % (line['id'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_budget_names[0]),
             log_budget_names[0] and ' %s' % str(tuple(log_budget_names[0]))
             or '', len(log_budget_names[1]),
             log_budget_names[1] and ' %s' % str(tuple(log_budget_names[1]))
             or '')
logger.info(summary)
logger.info('End process')
logger.info('---------------------------------------------------------------')
