from odoo import models, fields

class ResGroups(models.Model):
    _inherit = 'res.groups'

    name = fields.Char(string='Group Name', required=True)
    category_id = fields.Many2one('ir.module.category', string='Application', required=True)
    users = fields.Many2many('res.users', 'res_groups_users_rel', 'gid', 'uid', string='Users')