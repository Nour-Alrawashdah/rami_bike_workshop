from odoo import api, fields, models
from odoo.exceptions import ValidationError
from .constants import BIKE_TYPE_SELECTION


class Repair(models.Model):
    _name = "bike.workshop.repair"
    _inherit = ["bike.workshop.service.mixin"]
    _description = "Bike Repair Job"
    _rec_name = "reference"

    _unique_repair_reference = models.Constraint(
        "UNIQUE(reference)",
        "Repair Reference Used in another Repair Job",
    )

    reference = fields.Char(
        string="Repair Reference",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
    )

    source = fields.Selection(
        [
            ("workshop", "Workshop Bike"),
            ("external", "External Bike"),
        ],
        string="Bike Source",
        required=True,
    )

    bike_id = fields.Many2one(
        "bike.workshop.bike",
        string="Workshop Bike",
    )

    external_bike_reference = fields.Char(
        string="External Bike Reference",
    )

    external_bike_description = fields.Char(
        string="External Bike Description",
    )

    external_brand = fields.Char(
        string="External Bike Brand",
    )

    external_bike_type = fields.Selection(
        BIKE_TYPE_SELECTION,
        string="External Bike Type",
    )

    reported_issue = fields.Text(
        string="Reported Issue",
        required=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        required=True,
        default="draft",
    )

    part_line_ids = fields.One2many(
        "bike.workshop.repair.part.line",
        "repair_id",
        string="Spare Parts",
    )

    total_spare_parts_cost = fields.Float(
        string="Total Spare Parts Cost",
        compute="_compute_total_spare_parts_cost",
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = self.env["ir.sequence"].next_by_code(
                    "bike.workshop.repair"
                ) or "New"

        return super().create(vals_list)

    @api.depends("part_line_ids.subtotal")
    def _compute_total_spare_parts_cost(self):
        for repair in self:
            repair.total_spare_parts_cost = sum(
                repair.part_line_ids.mapped("subtotal")
            )

    def action_start(self):
        for repair in self:
            if repair.state != "draft":
                raise ValidationError(
                    "Only Draft repair jobs can be started."
                )

            if not repair.customer_id:
                raise ValidationError(
                    "Customer is required before starting the repair."
                )

            if not repair.reported_issue:
                raise ValidationError(
                    "Reported Issue is required before starting the repair."
                )

            if not repair.assigned_mechanic_id:
                raise ValidationError(
                    "Assigned Mechanic is required before starting the repair."
                )

            if repair.source == "workshop" and not repair.bike_id:
                raise ValidationError(
                    "Workshop Bike is required before starting the repair."
                )

            if repair.source == "external":
                if not repair.external_bike_reference:
                    raise ValidationError(
                        "External Bike Reference is required before starting the repair."
                    )

                if not repair.external_bike_description:
                    raise ValidationError(
                        "External Bike Description is required before starting the repair."
                    )

                if not repair.external_brand:
                    raise ValidationError(
                        "External Bike Brand is required before starting the repair."
                    )

                if not repair.external_bike_type:
                    raise ValidationError(
                        "External Bike Type is required before starting the repair."
                    )

            repair.state = "in_progress"

    def action_complete(self):
        for repair in self:
            if repair.state != "in_progress":
                raise ValidationError(
                    "Only In Progress repair jobs can be completed."
                )

            if not repair.service_notes:
                raise ValidationError(
                    "Service Notes are required before completing the repair."
                )

            if not repair.last_service_date:
                raise ValidationError(
                    "Last Service Date is required before completing the repair."
                )

            if repair.source == "workshop" and repair.bike_id:
                repair.bike_id.write(
                    {
                        "last_service_date": repair.last_service_date,
                        "service_notes": repair.service_notes,
                    }
                )

            repair.state = "completed"

    def action_cancel(self):
        for repair in self:
            if repair.state not in ("draft", "in_progress"):
                raise ValidationError(
                    "Only Draft or In Progress repair jobs can be cancelled."
                )

            repair.state = "cancelled"
