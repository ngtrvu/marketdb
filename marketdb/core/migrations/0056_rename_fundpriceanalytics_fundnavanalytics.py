# Generated by Django 4.1.1 on 2023-08-10 09:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0055_fundpriceanalytics_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FundPriceAnalytics',
            new_name='FundNavAnalytics',
        ),
    ]
