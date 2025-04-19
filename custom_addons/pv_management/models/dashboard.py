# File: models/dashboard.py
from odoo import api, fields, models
from datetime import datetime, timedelta
import json


class PVDashboard(models.Model):
    _name = 'pv.dashboard'
    _description = 'PV Management Dashboard'

    name = fields.Char('Name', default='Dashboard')

    # Dashboard data computed fields
    total_installations = fields.Integer('Total Installations', compute='_compute_dashboard_data')
    active_installations = fields.Integer('Active Installations', compute='_compute_dashboard_data')
    total_reclamations = fields.Integer('Total Reclamations', compute='_compute_dashboard_data')
    open_reclamations = fields.Integer('Open Reclamations', compute='_compute_dashboard_data')
    total_interventions = fields.Integer('Total Interventions', compute='_compute_dashboard_data')
    pending_interventions = fields.Integer('Pending Interventions', compute='_compute_dashboard_data')

    # Charts data (stored as JSON)
    installation_states_chart = fields.Text('Installation States Chart', compute='_compute_dashboard_data')
    reclamation_monthly_chart = fields.Text('Reclamation Monthly Chart', compute='_compute_dashboard_data')
    intervention_states_chart = fields.Text('Intervention States Chart', compute='_compute_dashboard_data')
    alarms_by_type_chart = fields.Text('Alarms by Type Chart', compute='_compute_dashboard_data')

    @api.depends('name')
    def _compute_dashboard_data(self):
        """Compute all dashboard data"""
        for record in self:
            # Basic counts
            record.total_installations = self.env['pv.installation'].search_count([])
            record.active_installations = self.env['pv.installation'].search_count([('state', '=', 'in_production')])
            record.total_reclamations = self.env['reclamation'].search_count([])
            record.open_reclamations = self.env['reclamation'].search_count([('state', 'in', ['draft', 'in_progress'])])
            record.total_interventions = self.env['fiche.intervention'].search_count([])
            record.pending_interventions = self.env['fiche.intervention'].search_count(
                [('state', 'in', ['draft', 'in_progress'])])

            # Generate charts data
            record.installation_states_chart = self._get_installation_states_data()
            record.reclamation_monthly_chart = self._get_reclamation_monthly_data()
            record.intervention_states_chart = self._get_intervention_states_data()
            record.alarms_by_type_chart = self._get_alarms_by_type_data()

    def _get_installation_states_data(self):
        """Generate data for installation states chart"""
        states = ['draft', 'in_progress', 'pending', 'in_production', 'in_stop', 'canceled']
        state_labels = {
            'draft': 'Brouillon',
            'in_progress': 'En cours',
            'pending': 'En attente',
            'in_production': 'En production',
            'in_stop': 'En arrêt',
            'canceled': 'Annulé'
        }

        data = []
        for state in states:
            count = self.env['pv.installation'].search_count([('state', '=', state)])
            if count > 0:
                data.append({
                    'label': state_labels.get(state, state),
                    'value': count,
                    'color': self._get_state_color(state)
                })

        return json.dumps(data)

    def _get_reclamation_monthly_data(self):
        """Generate monthly reclamation data for the last 6 months"""
        today = fields.Date.today()
        months_data = []

        for i in range(5, -1, -1):
            start_date = today.replace(day=1) - timedelta(days=i * 30)
            end_date = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(
                year=start_date.year + 1, month=1)

            domain = [
                ('date_heure', '>=', start_date),
                ('date_heure', '<', end_date)
            ]

            month_name = start_date.strftime('%B')
            count = self.env['reclamation'].search_count(domain)

            months_data.append({
                'name': month_name,
                'count': count
            })

        return json.dumps(months_data)

    def _get_intervention_states_data(self):
        """Generate data for intervention states chart"""
        states = ['draft', 'in_progress', 'closed', 'block']
        state_labels = {
            'draft': 'Ouvert',
            'in_progress': 'En cours',
            'closed': 'Fermé',
            'block': 'Bloqué'
        }

        data = []
        for state in states:
            count = self.env['fiche.intervention'].search_count([('state', '=', state)])
            if count > 0:
                data.append({
                    'label': state_labels.get(state, state),
                    'value': count,
                    'color': self._get_state_color(state)
                })

        return json.dumps(data)

    def _get_alarms_by_type_data(self):
        """Generate data for alarms by type chart"""
        alarm_types = self.env['alarm.management'].read_group(
            [],
            fields=['partie', 'id:count'],
            groupby=['partie']
        )

        type_labels = {
            'onduleur': 'Onduleur',
            'module': 'Module',
            'installation': 'Installation',
            'batterie': 'Batterie',
            'autre': 'Autre'
        }

        data = []
        for alarm_type in alarm_types:
            partie = alarm_type.get('partie')
            if partie:
                data.append({
                    'label': type_labels.get(partie, partie),
                    'value': alarm_type.get('partie_count', 0)
                })

        return json.dumps(data)

    def _get_state_color(self, state):
        """Return color for state"""
        colors = {
            'draft': '#17a2b8',  # info/blue
            'in_progress': '#007bff',  # primary/blue
            'pending': '#ffc107',  # warning/yellow
            'in_production': '#28a745',  # success/green
            'in_stop': '#dc3545',  # danger/red
            'canceled': '#6c757d',  # secondary/gray
            'closed': '#28a745',  # success/green
            'block': '#dc3545'  # danger/red
        }
        return colors.get(state, '#6c757d')