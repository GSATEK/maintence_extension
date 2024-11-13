from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    def set_portal_worker_group(self):
        portal_worker_group = self.env.ref('maintence_extension.group_portal_worker')
        for user in self:
            user.groups_id = [(4, portal_worker_group.id)]