from odoo import models, fields, api


class AgendaInterventionLine(models.Model):
    _name = 'agenda.intervention.line'
    _description = "Ligne d'agenda d'intervention"

    date_intervention = fields.Date(string="Date d'intervention", required=True)
    description = fields.Text(string="Description de l'intervention", required=True)
    fiche_intervention_id = fields.Many2one('fiche.intervention', string="Fiche d'intervention")


class FicheIntervention(models.Model):
    _name = 'fiche.intervention'
    _description = 'Fiche d\'intervention'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Référence', required=True, copy=False, readonly=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code(
                           'fiche.intervention.sequence') or 'Nouveau')
    # Type d'intervention (new field)
    type_intervention = fields.Selection([
        ('maintenance', 'Maintenance'),
        ('installation', 'Installation'),
        ('reparation', 'Réparation'),
        ('inspection', 'Inspection'),
        ('autre', 'Autre')
    ], string='Type d\'intervention', required=True, tracking=True)

    date = fields.Date(string='Date d\'intervention', required=True, default=fields.Date.today)
    # Heure d'intervention (new field)
    heure_intervention = fields.Float(string='Heure d\'intervention', copy=True)
    # Agenda (new field)
    agenda_line_ids = fields.One2many('agenda.intervention.line', 'fiche_intervention_id',
                                      string='Agenda', help="Programme prévu pour l'intervention")

    adresse =  fields.Many2one( 'res.partner', string='Adresse')
    installation_id = fields.Many2one('pv.installation', string='Installation')
    reclamation_id = fields.Many2one('reclamation', string='Réclamation associée')
    code_alarm_id = fields.Many2one('alarm.management', string='Code Alarm')
    date_cloture = fields.Date(string='Date de cloture', required=True)
    actions_effectuees = fields.Text(string='Actions effectuées')

    # Updated state field to match Help Desk
    state = fields.Selection([
        ('draft', 'Ouvert'),
        ('in_progress', 'En cours'),
        ('closed', 'Fermé'),
        ('block', 'Bloqué')
    ], string='État', default='draft', tracking=True)

    # Field for technician - may need to be expanded to team
    technicien_id = fields.Many2one('hr.employee', string='Technicien')
    # Team field (new)
    equipe_intervention_ids = fields.Many2many('hr.employee', string='Équipe d\'Intervention')

    # Intervention text (conditional field)
    intervention_text = fields.Text(string='Bilan d\'intervention',
                                    help="Bilan final de l'intervention après fermeture")

    def action_view_reclamation(self):
        """Bouton pour revenir à la réclamation d'origine"""
        self.ensure_one()
        if not self.reclamation_id:
            return

        return {
            'name': 'Réclamation',
            'view_mode': 'form',
            'res_model': 'reclamation',
            'res_id': self.reclamation_id.id,
            'type': 'ir.actions.act_window',
        }

    # Add state change methods
    def action_draft(self):
        self.write({'state': 'draft'})

    def action_in_progress(self):
        self.write({'state': 'in_progress'})

    def action_closed(self):
        self.write({'state': 'closed'})

    def action_block(self):
        self.write({'state': 'block'})

        def action_closed(self):
            # Do any validation if needed before closing
            # For example, ensure required fields are filled
            self.write({
                'state': 'closed',
                # You could set a timestamp here if needed
                # 'closed_date': fields.Datetime.now(),
            })
