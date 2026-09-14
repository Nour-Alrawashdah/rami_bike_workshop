from odoo import fields, models
from .constants import BIKE_TYPE_SELECTION


class ResPartner(models.Model):
    _inherit = "res.partner"

    preferred_bike_type = fields.Selection(
        BIKE_TYPE_SELECTION,
        string="Preferred Bike Type",
    )
