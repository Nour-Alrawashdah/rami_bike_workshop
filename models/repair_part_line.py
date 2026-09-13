from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RepairPartLine(models.Model):
    _name = "bike.workshop.repair.part.line"
    _description = "Repair Spare Part Line"

    repair_id = fields.Many2one(
        "bike.workshop.repair",
        string="Repair Job",
        required=True,
        ondelete="cascade",
    )

    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
    )

    quantity = fields.Float(
        string="Quantity",
        required=True,
        default=1.0,
    )

    unit_price = fields.Float(
        string="Unit Price",
        required=True,
    )

    subtotal = fields.Float(
        string="Subtotal",
        compute="_compute_subtotal",
        store=True,
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.lst_price
   #حساب توتل كامل للبرودكت
    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
#لو دخلت كمية بالسالب 
    @api.constrains("quantity", "unit_price")
    def _check_non_negative_values(self):
        for line in self:
            if line.quantity < 0:
                raise ValidationError(
                    "Quantity cannot be negative."
                )

            if line.unit_price < 0:
                raise ValidationError(
                    "Unit Price cannot be negative."
                )