from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    is_maintenance_engineer = fields.Boolean(
        string="Maintenance Engineer",
    )