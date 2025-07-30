from django.db import models
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    sort_order = models.IntegerField(default=0, db_index=True)

    class Meta:
        db_table = "categories"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def clean(self):
        if self.name and self.name.strip() == "":
            raise ValidationError({"name": "This field cannot be blank."})

    def save(self, *args, **kwargs):
        if self.sort_order is None:
            max_order = Category.objects.aggregate(models.Max("sort_order"))[
                "sort_order__max"
            ]
            self.sort_order = (max_order or 0) + 10
        super().save(*args, **kwargs)
