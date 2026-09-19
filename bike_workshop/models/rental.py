from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Rental(models.Model):
    _name = "bike.workshop.rental"
    _description = "Bike Rental"
    _rec_name = "reference"

    _unique_rental_reference = models.Constraint(
        "UNIQUE(reference)",
        _("Rental Reference Used in another Rental"),
    )

    reference = fields.Char(
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )

    customer_id = fields.Many2one(
        "res.partner",
        required=True,
    )

    bike_id = fields.Many2one(
        "bike.workshop.bike",
        required=True,
    )
   #for analyzing 
    bike_type = fields.Selection(
    related="bike_id.bike_type",
    store=True,
    readonly=True,
)
    start_date = fields.Date(
        required=True,
    )

    expected_return_date = fields.Date(
        required=True,
    )

    actual_return_date = fields.Date()

    daily_rental_price = fields.Float(
        required=True,
    )

    rental_duration = fields.Integer(
        compute="_compute_rental_duration",
        store=True,
        group_operator="avg",
    )

    total_rental_amount = fields.Float(
        compute="_compute_total_rental_amount",
        store=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("returned", "Returned"),
        ],
        required=True,
        default="draft",
    )

    return_performance = fields.Selection(
        [
            ("on_time", "On Time"),
            ("late", "Late"),
            ("pending", "Pending"),
        ],
        compute="_compute_return_performance",
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = self.env["ir.sequence"].next_by_code(
                    "bike.workshop.rental"
                ) or "New"

            if vals.get("bike_id"):
                bike = self.env["bike.workshop.bike"].browse(
                    vals["bike_id"]
                )

                if not vals.get("daily_rental_price"):
                    vals["daily_rental_price"] = bike.daily_rental_price

        return super().create(vals_list)

    @api.constrains("start_date", "expected_return_date")
    def _check_rental_dates(self):
        for rental in self:
            if (
                rental.start_date
                and rental.expected_return_date
                and rental.expected_return_date <= rental.start_date
            ):
                raise ValidationError(
                    _("Expected Return Date must be after Start Date.")
                )

    @api.constrains(
        "start_date",
        "expected_return_date",
        "daily_rental_price",
    )
    def _check_rental_values(self):
        for rental in self:
            if rental.rental_duration <= 0:
                raise ValidationError(
                    _("Rental Duration must be greater than 0.")
                )

            if rental.daily_rental_price < 0:
                raise ValidationError(
                    _("Daily Rental Price cannot be negative.")
                )

            if rental.total_rental_amount < 0:
                raise ValidationError(
                    _("Total Rental Amount cannot be negative.")
                )

    @api.constrains(
        "bike_id",
        "start_date",
        "expected_return_date",
        "state",
    )
    def _check_rental_conflicts(self):
        for rental in self:
            if rental.state != "confirmed":
                continue

            in_progress_repair = self.env["bike.workshop.repair"].search(
                [
                    ("bike_id", "=", rental.bike_id.id),
                    ("state", "=", "in_progress"),
                ],
                limit=1,
            )

            if in_progress_repair:
                raise ValidationError(
                    _("This bike cannot be rented because it has "
                      "an In Progress repair job.")
                )

            conflicting_rental = self.env["bike.workshop.rental"].search(
                [
                    ("id", "!=", rental.id),
                    ("bike_id", "=", rental.bike_id.id),
                    ("state", "=", "confirmed"),
                    ("start_date", "<=", rental.expected_return_date),
                    ("expected_return_date", ">=", rental.start_date),
                ],
                limit=1,
            )

            if conflicting_rental:
                raise ValidationError(
                    _("This bike already has a confirmed rental "
                      "that overlaps with the selected dates.")
                )

    @api.depends("start_date", "expected_return_date")
    def _compute_rental_duration(self):
        for rental in self:
            if rental.start_date and rental.expected_return_date:
                rental.rental_duration = (
                    rental.expected_return_date - rental.start_date
                ).days
            else:
                rental.rental_duration = 0

    @api.depends("actual_return_date", "expected_return_date")
    def _compute_return_performance(self):
        for rental in self:
            if not rental.actual_return_date:
                rental.return_performance = "pending"
            elif rental.actual_return_date <= rental.expected_return_date:
                rental.return_performance = "on_time"
            else:
                rental.return_performance = "late"

    @api.onchange("bike_id")
    def _onchange_bike_id(self):
        if self.bike_id:
            self.daily_rental_price = self.bike_id.daily_rental_price

    @api.onchange("start_date", "expected_return_date")
    def _onchange_rental_dates(self):
        if (
            self.start_date
            and self.expected_return_date
            and self.expected_return_date <= self.start_date
        ):
            return {
                "warning": {
                    "title": _("Invalid Return Date"),
                    "message": _("Expected Return Date must be after Start Date."),
                }
            }

    @api.depends("rental_duration", "daily_rental_price")
    def _compute_total_rental_amount(self):
        for rental in self:
            rental.total_rental_amount = (
                rental.rental_duration * rental.daily_rental_price
            )

    def write(self, vals):
        if "daily_rental_price" in vals:
            for rental in self:
                if (
                    rental.state != "draft"
                    and vals["daily_rental_price"]
                    != rental.daily_rental_price
                ):
                    raise ValidationError(
                        _("Daily Rental Price cannot be changed after "
                          "the rental is confirmed.")
                    )

        return super().write(vals)

    def action_confirm(self):
        for rental in self:
            if rental.state != "draft":
                raise ValidationError(
                    _("Only Draft rentals can be confirmed.")
                )

            rental.state = "confirmed"

    def action_return(self):
        for rental in self:
            if rental.state != "confirmed":
                raise ValidationError(
                    _("Only Confirmed rentals can be returned.")
                )

            rental.state = "returned"
            rental.actual_return_date = fields.Date.today()