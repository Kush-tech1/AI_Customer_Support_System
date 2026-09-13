from app.data.database import (
    get_order,
    get_payment,
    get_faqs,
)

print(get_order(1003))
print(get_payment(1003))
print(get_faqs())