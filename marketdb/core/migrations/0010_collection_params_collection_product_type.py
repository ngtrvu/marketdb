# Generated by Django 4.1.1 on 2022-12-05 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_rename_loan_to_deposit_bank_loan_to_deposit_ratio_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="collection",
            name="params",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="collection",
            name="product_type",
            field=models.CharField(default="stock", max_length=50),
        ),
    ]
