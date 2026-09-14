from odoo import models, fields


class ServiceMixin(models.AbstractModel):
    _name = "bike.workshop.service.mixin"
    _description = "Shared Service Information"

    assigned_mechanic_id = fields.Many2one(
        "res.users",
        string="Assigned Mechanic",
    )

    last_service_date = fields.Date(
        string="Last Service Date",
    )

    service_notes = fields.Text(
        string="Service Notes",
    )