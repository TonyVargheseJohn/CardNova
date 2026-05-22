from django.db import models
from guest.models import User
from wadmin.models import Product  # Import Product from wadmin app

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, db_index=True)  # For guests
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Now Product is properly imported
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_cart'
        # Prevent duplicate rows for same user+product or session+product
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_user_product',
                condition=models.Q(user__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['session_key', 'product'],
                name='unique_session_product',
                condition=models.Q(user__isnull=True)
            )
        ]

    def __str__(self):
        return f"{self.product.name} (Qty: {self.quantity})"

    @property
    def item_total(self):
        price = self.product.sale_price or self.product.price
        return price * self.quantity