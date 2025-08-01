# Generated by Django 4.1.1 on 2022-12-06 03:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_collection_params_collection_product_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feargreedindexdaily',
            old_name='market',
            new_name='exchange',
        ),
        migrations.RenameField(
            model_name='feargreedindexdaily',
            old_name='fear_greed_score',
            new_name='score',
        ),
        migrations.AlterUniqueTogether(
            name='feargreedindexdaily',
            unique_together={('exchange', 'date')},
        ),
    ]
