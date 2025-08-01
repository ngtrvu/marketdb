# Generated by Django 4.1.1 on 2022-12-02 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_stockpricerealtime_fb_volume_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="bank",
            old_name="loan_to_deposit",
            new_name="loan_to_deposit_ratio",
        ),
        migrations.AddField(
            model_name="bank",
            name="capital_adequacy_ratio",
            field=models.DecimalField(decimal_places=4, max_digits=20, null=True),
        ),
    ]
