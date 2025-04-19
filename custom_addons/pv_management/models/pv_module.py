from odoo import models, fields, api

class PVModule(models.Model):
    _name = 'pv.module'
    _description = 'PV Module'
    installation_id = fields.Many2one('pv.installation', string='Installation')

    reference = fields.Many2one('configuration.district.steg', string='Reference Module PV')
    brand = fields.Char(string='Marque Module PV')
    power = fields.Char(string='Puissance Module PV (WC)')
    number_of_modules = fields.Integer(string='Nombre de Module')




