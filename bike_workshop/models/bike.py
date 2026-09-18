from odoo import _, api, fields, models
from .constants import BIKE_TYPE_SELECTION


class Bike(models.Model):
    _name = "bike.workshop.bike"
    _inherit = ["bike.workshop.service.mixin"]
    _description = "Bike Workshop"

    name = fields.Char(
        string="Bike Name / Code",
        required=True,
    )

    brand = fields.Char(
        string="Brand",
    )

    bike_type = fields.Selection(
        BIKE_TYPE_SELECTION,
        string="Bike Type",
    )

    purchase_date = fields.Date(
        string="Purchase Date",
    )

    daily_rental_price = fields.Float(
        string="Daily Rental Price",
    )

    wheel_size = fields.Float(
        string="Wheel Size (inches)",
    )

    rental_ids = fields.One2many(
        "bike.workshop.rental",
        "bike_id",
        string="Rentals",
    )

    rental_count = fields.Integer(
        string="Rental Count",
        compute="_compute_rental_count",
    )

    @api.depends("rental_ids")
    def _compute_rental_count(self):
        for bike in self:
            bike.rental_count = len(bike.rental_ids)

    def action_view_rentals(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": _("Rentals"),
            "res_model": "bike.workshop.rental",
            "view_mode": "list,form",
            "domain": [("bike_id", "=", self.id)],
            "context": {
                "default_bike_id": self.id,
            },
        }
