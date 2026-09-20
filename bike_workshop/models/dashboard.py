from odoo import _, fields, models


class BikeWorkshopDashboard(models.Model):
    _name = "bike.workshop.dashboard"
    _description = "Bike Workshop Dashboard"

    
    name = fields.Char(
    default="Workshop Dashboard",
    readonly=True,
)
    active_rentals_today = fields.Integer(
        string="Active Rentals Today",
        compute="_compute_counts",
    )

    returns_due_today = fields.Integer(
        string="Returns Due Today",
        compute="_compute_counts",
    )

    repairs_in_progress = fields.Integer(
        string="Repairs In Progress",
        compute="_compute_counts",
    )

    def _compute_counts(self):
        today = fields.Date.context_today(self)

        rental_model = self.env["bike.workshop.rental"]
        repair_model = self.env["bike.workshop.repair"]

        active_rentals = rental_model.search_count(
            [
                ("state", "=", "confirmed"),
                ("start_date", "<=", today),
                ("expected_return_date", ">=", today),
            ]
        )

        returns_due = rental_model.search_count(
            [
                ("state", "=", "confirmed"),
                ("expected_return_date", "=", today),
            ]
        )

        repairs_in_progress = repair_model.search_count(
            [
                ("state", "=", "in_progress"),
            ]
        )
       
        for dashboard in self:
            dashboard.active_rentals_today = active_rentals
            dashboard.returns_due_today = returns_due
            dashboard.repairs_in_progress = repairs_in_progress

    def action_open_active_rentals(self):
        today = fields.Date.context_today(self)

        return {
            "type": "ir.actions.act_window",
            "name": _("Active Rentals Today"),
            "res_model": "bike.workshop.rental",
            "view_mode": "list,form",
            "domain": [
                ("state", "=", "confirmed"),
                ("start_date", "<=", today),
                ("expected_return_date", ">=", today),
            ],
        }

    def action_open_returns_due(self):
        today = fields.Date.context_today(self)

        return {
            "type": "ir.actions.act_window",
            "name": _("Returns Due Today"),
            "res_model": "bike.workshop.rental",
            "view_mode": "list,form",
            "domain": [
                ("state", "=", "confirmed"),
                ("expected_return_date", "=", today),
            ],
        }

    def action_open_repairs_in_progress(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Repairs In Progress"),
            "res_model": "bike.workshop.repair",
            "view_mode": "list,form",
            "domain": [
                ("state", "=", "in_progress"),
            ],
        }
