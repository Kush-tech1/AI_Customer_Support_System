from app.data.database import (
    get_order,
    get_payment,
    get_faqs,
)


class OrderPaymentAgent:

    def run(
        self,
        order_id: int | None,
        requires_order_lookup: bool,
        requires_payment_lookup: bool,
    ) -> dict:

        result = {
            "order": None,
            "payment": None,
            "faqs": [],
        }

        if order_id:

            if requires_order_lookup:
                result["order"] = get_order(order_id)

            if requires_payment_lookup:
                result["payment"] = get_payment(order_id)

        result["faqs"] = get_faqs()

        return result