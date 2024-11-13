from odoo import models, fields, api

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    equipment_assign_to = fields.Selection(
        [('department', 'Department'), ('employee', 'Employee'), ('client', 'Cliente'), ('other', 'Other')],
        string='Used By',
        required=True,
        default='employee'
    )

    partner_id = fields.Many2one('res.partner', string='Cliente')
