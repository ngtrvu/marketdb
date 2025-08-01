# Generated by Django 4.1.1 on 2023-01-16 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_alter_feargreedindexdaily_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feargreedindexdaily',
            name='market_index_diff',
            field=models.DecimalField(decimal_places=10, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='feargreedindexdaily',
            name='momentum',
            field=models.DecimalField(decimal_places=10, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='feargreedindexdaily',
            name='momentum_diff',
            field=models.DecimalField(decimal_places=10, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='feargreedindexdaily',
            name='price_breadth',
            field=models.DecimalField(decimal_places=10, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='feargreedindexdaily',
            name='price_breadth_diff',
            field=models.DecimalField(decimal_places=10, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='feargreedindexdaily',
            name='price_strength',
            field=models.DecimalField(decimal_places=10, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='feargreedindexdaily',
            name='rsi',
            field=models.DecimalField(decimal_places=10, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='feargreedindexdaily',
            name='volatility',
            field=models.DecimalField(decimal_places=10, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='feargreedindexdaily',
            name='volatility_sma',
            field=models.DecimalField(decimal_places=10, max_digits=20, null=True),
        ),
    ]
