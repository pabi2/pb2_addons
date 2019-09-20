# -*- coding: utf-8 -*-
import time
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare
from openerp.exceptions import RedirectWarning
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import RetryableJobError
import logging

_logger = logging.getLogger(__name__)


@job
def action_done_async_process(session, model_name, res_id):
    try:
        res = session.pool[model_name].action_carry_forward_background(
            session.cr, session.uid, [res_id], session.context)
        return {'result': res}
    except Exception, e:
        raise RetryableJobError(e)


@job
def action_done_save_async_process(session, model_name, res_id):
    try:
        res = session.pool[model_name].action_done_save(
            session.cr, session.uid, [res_id], session.context)
        return {'result': res}
    except Exception, e:
        raise RetryableJobError(e)


class ProjectBalanceCarryForward(models.Model):
    _name = 'project.balance.carry.forward'

    name = fields.Char(
        string='Name',
        readonly=True,
        size=500,
    )
    from_fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='From Fiscal Year',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    to_fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='To Fiscal Year',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    line_ids = fields.One2many(
        'project.balance.carry.forward.line',
        'carry_forward_id',
        string='Carry Forward Lines',
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        string='Status',
        default='draft',
        readonly=True,
    )
    amount_total = fields.Float(
        string='Total Amount',
        compute='_compute_amount_total',
    )
    button_carry_forward_job_id = fields.Many2one(
        'queue.job',
        string='Carry Forward Job',
        compute='_compute_button_carry_forward_job_uuid',
    )
    button_carry_forward_uuid = fields.Char(
        string='Carry Forward Job UUID',
        compute='_compute_button_carry_forward_job_uuid',
    )

    @api.multi
    def _compute_button_carry_forward_job_uuid(self):
        for rec in self:
            task_name = "%s('%s', %s)" % \
                ('action_done_async_process', self._name, rec.id)
            jobs = self.env['queue.job'].search([
                ('func_string', 'like', task_name),
                ('state', '!=', 'done')],
                order='id desc', limit=1)
            rec.button_carry_forward_job_id = jobs and jobs[0] or False
            rec.button_carry_forward_uuid = jobs and jobs[0].uuid or False
        return True

    @api.multi
    def action_done(self):
        for rec in self:
            rec.action_carry_forward()
        return True

    @api.multi
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('balance_amount'))

    @api.model
    def default_get(self, fields):
        res = super(ProjectBalanceCarryForward, self).default_get(fields)
        Fiscal = self.env['account.fiscalyear']
        if not res.get('fiscalyear_id', False):
            fiscals = Fiscal.search([
                ('date_start', '>', time.strftime('%Y-%m-%d'))],
                order='date_start')
            if fiscals:
                res['from_fiscalyear_id'] = Fiscal.find()
                res['to_fiscalyear_id'] = fiscals[0].id
        return res

    @api.multi
    def write(self, vals):
        res = super(ProjectBalanceCarryForward, self).write(vals)
        if 'from_fiscalyear_id' in vals:
            self.compute_projects()
        return res

    @api.model
    def create(self, vals):
        res = super(ProjectBalanceCarryForward, self).create(vals)
        res.name = '{:03d}'.format(res.id)
        res.compute_projects()
        return res

    @api.multi
    def compute_projects(self):
        self.ensure_one()
        self.line_ids.unlink()
        """ This method, list all projects with, budget balance > 0 """
        where_ext = ''
        if self.from_fiscalyear_id.control_ext_charge_only:
            where_ext = "and charge_type = 'external'"
        sql = """
            select a.project_id, a.program_id, a.balance_amount
            from (
                select project_id, program_id,
                sum(released_amount - amount_actual) balance_amount
                from budget_monitor_report
                where budget_method = 'expense'
                and project_id is not null
                and fiscalyear_id = %s
                %s
                and (coalesce(released_amount, 0.0) != 0.0
                     or coalesce(amount_actual, 0.0) != 0.0)
                group by project_id,  program_id
            ) a
                inner join res_project prj
                    on prj.id = a.project_id
                    and prj.state = 'approve'
            where a.balance_amount > 0.0
        """ % (self.from_fiscalyear_id.id, where_ext)
        self._cr.execute(sql)
        projects = [(0, 0, project) for project in self._cr.dictfetchall()]
        self.write({'line_ids': projects})

    @api.multi
    def action_carry_forward(self):
        """ For each project, inject the balance amount to the released amount
        in related account.budget.line """
        BudgetLine = self.env['account.budget.line']
        for rec in self:
            fiscalyear = rec.to_fiscalyear_id
            for line in rec.line_ids:
                budget_lines = BudgetLine.search(
                    [('fiscalyear_id', '=', fiscalyear.id),
                     ('project_id', '=', line.project_id.id),
                     ('charge_type', '=', 'external'),
                     ('budget_method', '=', 'expense')])
                if len(budget_lines) == 1:
                    budget_lines.released_amount = line.balance_amount
                    line.write({'state': 'success'})
                elif not budget_lines:
                    line.write({'reason': '1',
                                'state': 'fail'})
                elif len(budget_lines) > 1:
                    balance_amount = line.balance_amount
                    for budget in budget_lines:
                        released_amount = 0.0
                        if float_compare(balance_amount, budget.planned_amount, 2) == 1:
                            released_amount = budget.planned_amount
                            balance_amount -= released_amount
                            budget.write({'released_amount': released_amount})
                        else:
                            released_amount = balance_amount
                            balance_amount = 0.0
                            budget.write({'released_amount': released_amount})
                            break

                    line.write({'state': 'success'})
        # update project released amount
        fiscalyear = self.to_fiscalyear_id
        for line in self.line_ids:
            if line.state == "success":
                project = line.project_id
                self.update_project_released_amount(project, fiscalyear, line.balance_amount)
        self.write({'state': 'done'})

    @api.multi
    def action_carry_forward_background(self):
        if self._context.get('button_carry_forward_async_process', False):
            self.ensure_one()
            self.name = '{:03d}'.format(self.id)
            if self._context.get('job_uuid', False):  # Called from @job
                return self.action_done()
            if self.button_carry_forward_job_id:
                message = ('Carry Forward')
                action = self.env.ref('pabi_utils.action_my_queue_job')
                raise RedirectWarning(message, action.id, ('Go to My Jobs'))
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = 'From %s to %s - Commitment Carry Forward' % \
                (self.from_fiscalyear_id.name, self.to_fiscalyear_id.name)
            uuid = action_done_async_process.delay(
                session, self._name, self.id, description=description)
            self.env['queue.job'].search([('uuid', '=', uuid)], limit=1)
        else:
            return self.action_done()

    def update_project_released_amount(self, project, fiscalyear, balance_amount):
        budget_plans = project.budget_plan_ids.filtered(lambda l:
                                                        l.fiscalyear_id == fiscalyear
                                                        and l.budget_method=='expense'
                                                        and l.charge_type=='external')
        if not budget_plans:
            raise ValidationError(
                _("Not allow to release budget for %s without plan!" % project.code))

        update_vals = []
        lock = 0
        released_amount = balance_amount
        for budget_plan in budget_plans:
            if budget_plan.planned_amount == 0.0:
                update = {'released_amount': balance_amount}
                balance_amount = 0.0
                update_vals.append((1, budget_plan.id, update))
                break
            else:
                # float_compare: 0:equal, 1:first>second, -1:first<second
                if float_compare(balance_amount, budget_plan.planned_amount, 2) == 1:
                    update = {'released_amount': budget_plan.planned_amount}
                    balance_amount -= budget_plan.planned_amount
                    update_vals.append((1, budget_plan.id, update))
                else:
                    update = {'released_amount': balance_amount}
                    balance_amount = 0.0
                    update_vals.append((1, budget_plan.id, update))
                    break
        project_lock = project.lock_release
        if update_vals:
            if project_lock:
                lock = 1
                project.write({'lock_release': False})
            project.write({'budget_plan_ids': update_vals})
            # Create release history
            project.budget_release_ids.create({
                'fiscalyear_id': fiscalyear.id,
                'project_id': project.id,
                'released_amount': update.get('released_amount')
            })
            if lock:
                project.write({'lock_release': True})

        return True


class ProjectBalanceCarryForwardLine(models.Model):
    _name = 'project.balance.carry.forward.line'
    _order = 'program_id'

    carry_forward_id = fields.Many2one(
        'project.balance.carry.forward',
        string='Carry Over',
        index=True,
        ondelete='cascade',
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program',
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
    )
    balance_amount = fields.Float(
        string='Amount to Carry Forward',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('success', 'Successful'),
         ('fail', 'Failed')],
        string='Status',
        readonly=True,
        default='draft',
        help="Whether the amount has been carried as released amount "
        "in target fiscal year release",
    )
    reason = fields.Selection(
        [('1', 'No project in budget line on target fiscalyear'),
         ('2', '> 1 budget line for the same project on target fiscalyear')],
        string='Reason',
        readonly=True,
        help="Reason for failed carry forward",
    )
