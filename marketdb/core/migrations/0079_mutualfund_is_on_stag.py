# Generated by Django 4.1.1 on 2025-03-11 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0078_fundnavanalytics_fund_mutualfundpricechart_fund'),
    ]

    operations = [
        migrations.AddField(
            model_name='mutualfund',
            name='is_on_stag',
            field=models.BooleanField(default=False),
        ),
    ]
