from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class BikeWorkshopPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        if "rental_count" in counters:
            values["rental_count"] = request.env[
                "bike.workshop.rental"
            ].search_count(
                [
                    (
                        "customer_id",
                        "=",
                        request.env.user.partner_id.id,
                    )
                ]
            )

        return values

    @http.route(
        "/my/rentals",
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_rentals(self, **kwargs):
        rentals = request.env["bike.workshop.rental"].search(
            [
                ("customer_id", "=", request.env.user.partner_id.id),
            ],
            order="start_date desc, id desc",
        )

        return request.render(
            "bike_workshop.portal_my_rentals",
            {
                "rentals": rentals,
            },
        )

    @http.route(
        "/my/rentals/<int:rental_id>",
        type="http",
        auth="user",
        website=True,
    )
    def portal_rental_detail(self, rental_id, **kwargs):
        rental = request.env["bike.workshop.rental"].search(
            [
                ("id", "=", rental_id),
                ("customer_id", "=", request.env.user.partner_id.id),
            ],
            limit=1,
        )

        if not rental:
            return request.not_found()

        return request.render(
            "bike_workshop.portal_rental_detail",
            {
                "rental": rental,
            },
        )