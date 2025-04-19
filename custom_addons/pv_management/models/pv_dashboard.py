# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
import calendar


class PVDashboard(models.Model):
    _name = 'pv.dashboard'
    _description = 'PV Management Dashboard'

    name = fields.Char(string='Name', default="PV Dashboard")

    # Installations counts
    total_installations = fields.Integer(string="Total Installations", compute="_compute_installation_stats")
    active_installations = fields.Integer(string="Active Installations", compute="_compute_installation_stats")
    production_installations = fields.Integer(string="In Production", compute="_compute_installation_stats")
    stopped_installations = fields.Integer(string="Stopped", compute="_compute_installation_stats")

    # Maintenance stats
    open_reclamations = fields.Integer(string="Open Reclamations", compute="_compute_maintenance_stats")
    pending_interventions = fields.Integer(string="Pending Interventions", compute="_compute_maintenance_stats")

    # Alarm stats
    recent_alarms = fields.Integer(string="Recent Alarms", compute="_compute_alarm_stats")

    # Chart data
    installation_states_chart = fields.Text(compute="_compute_chart_data")
    monthly_interventions_chart = fields.Text(compute="_compute_chart_data")
    recent_activity_ids = fields.One2many('mail.activity', 'res_id', string='Recent Activities',
                                          domain=lambda self: [('res_model', 'in', ['pv.installation', 'reclamation',
                                                                                    'fiche.intervention'])])

    def action_new_installation(self):
        return {
            'name': 'New Installation',
            'view_mode': 'form',
            'res_model': 'pv.installation',
            'type': 'ir.actions.act_window',
            'context': {'default_state': 'draft'},
            'target': 'current',
        }

    def action_new_reclamation(self):
        return {
            'name': 'New Reclamation',
            'view_mode': 'form',
            'res_model': 'reclamation',
            'type': 'ir.actions.act_window',
            'context': {'default_state': 'draft'},
            'target': 'current',
        }

    def action_new_intervention(self):
        return {
            'name': 'New Intervention',
            'view_mode': 'form',
            'res_model': 'fiche.intervention',
            'type': 'ir.actions.act_window',
            'context': {'default_state': 'draft'},
            'target': 'current',
        }

    def action_view_alarms(self):
        return {
            'name': 'Alarm Management',
            'view_mode': 'tree,form',
            'res_model': 'alarm.management',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }




    @api.depends('name')
    def _compute_installation_stats(self):
        for record in self:
            # Get total installations
            total = self.env['pv.installation'].search_count([])

            # Get active installations
            active = self.env['pv.installation'].search_count([('active', '=', True)])

            # Get in production installations
            production = self.env['pv.installation'].search_count([('state', '=', 'in_production')])

            # Get stopped installations
            stopped = self.env['pv.installation'].search_count([('state', '=', 'in_stop')])

            record.total_installations = total
            record.active_installations = active
            record.production_installations = production
            record.stopped_installations = stopped

    @api.depends('name')
    def _compute_maintenance_stats(self):
        for record in self:
            # Get open reclamations
            open_recs = self.env['reclamation'].search_count([('state', 'in', ['draft', 'in_progress'])])

            # Get pending interventions
            pending_ints = self.env['fiche.intervention'].search_count([('state', '!=', 'closed')])

            record.open_reclamations = open_recs
            record.pending_interventions = pending_ints

    @api.depends('name')
    def _compute_alarm_stats(self):
        for record in self:
            # Get recent alarms (in the last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            recent = self.env['reclamation'].search_count([
                ('date_heure', '>=', thirty_days_ago),
                ('code_alarm_id', '!=', False)
            ])

            record.recent_alarms = recent

    @api.depends('name')
    def _compute_chart_data(self):
        for record in self:
            # Installation states chart data
            states = {
                'draft': 0,
                'in_progress': 0,
                'pending': 0,
                'in_production': 0,
                'in_stop': 0,
                'canceled': 0,
            }

            for state in states.keys():
                count = self.env['pv.installation'].search_count([('state', '=', state)])
                states[state] = count

            record.installation_states_chart = str(states)

            # Monthly interventions chart data
            now = datetime.now()
            start_of_year = datetime(now.year, 1, 1)

            monthly_data = {}

            for i in range(1, 13):
                month_name = calendar.month_name[i]
                start_date = datetime(now.year, i, 1)

                if i < 12:
                    end_date = datetime(now.year, i + 1, 1)
                else:
                    end_date = datetime(now.year + 1, 1, 1)

                count = self.env['fiche.intervention'].search_count([
                    ('date', '>=', start_date.strftime('%Y-%m-%d')),
                    ('date', '<', end_date.strftime('%Y-%m-%d'))
                ])

                monthly_data[month_name] = count

            record.monthly_interventions_chart = str(monthly_data)