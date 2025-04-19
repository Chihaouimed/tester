# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PVInstallation(models.Model):
    _name = 'pv.installation'
    _description = 'Solar PV Installation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    module_ids = fields.One2many('pv.module', 'installation_id', string='Modules PV')
    inverters_ids = fields.One2many('pv.inverter', 'installation_id', string='Onduleur PV')

    # Fields
    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Nom Instalation')
    code = fields.Char(string='Code', readonly=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('pv.installation.sequence') or 'Nouveau')
    client = fields.Many2one('res.partner', string='Client')
    date_mise_en_service = fields.Date(string='Date de Mise en Service')
    address_id = fields.Char(string='Street', related='client.street', readonly=True)
    type_installation = fields.Selection([
        ('bt_residentiel', 'BT - Résidentiel'),
        ('bt_commercial', 'BT - Commercial'),
        ('mt_industriel', 'MT - Industriel')
    ], string="Type d'Installation")
    district_steg_id = fields.Many2one('configuration.district.steg', string='District STEG')
    reference_steg = fields.Integer(string='Reference STEG')
    type_compteur = fields.Selection([
        ('monophase', 'Monophasé'),
        ('triphase', 'Triphasé')
    ], string='Type de Compteur')

    calibre_disjoncteur_existant_id = fields.Many2one('configuration.district.steg',
                                                      string='Calibre Disjoncteur Existant (A)')
    calibre_disjoncteur_steg_id = fields.Many2one('configuration.district.steg', string='Calibre Disjoncteur STEG (A)')
    puissance_souscrite = fields.Float(string='Puissance Souscrite')
    consommation_annuelle = fields.Integer(string='Consommation Annuelle')
    # State Field
    state = fields.Selection(
        selection=[
            ('draft', 'Brouillon'),
            ('in_progress', 'En cours'),
            ('pending', 'En attente'),
            ('in_production', 'En production'),
            ('in_stop', 'En arrêt'),
            ('canceled', 'Annulé'),
        ],
        string='État',
        default='draft',
        tracking=True
    )

    @api.model
    def create(self, vals):
        if vals.get('code', 'Nouveau') == 'Nouveau':
            vals['code'] = self.env['ir.sequence'].next_by_code('pv.installation.sequence') or 'Nouveau'
        return super(PVInstallation, self).create(vals)

    # State Change Methods
    def action_draft(self):
        self.write({'state': 'draft'})

    def action_in_progress(self):
        self.write({'state': 'in_progress'})

    def action_pending(self):
        self.write({'state': 'pending'})

    def action_in_production(self):
        self.write({'state': 'in_production'})

    def action_in_stop(self):
        self.write({'state': 'in_stop'})

    def action_cancel(self):
        self.write({'state': 'canceled'})