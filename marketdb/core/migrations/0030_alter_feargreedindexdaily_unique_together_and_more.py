# Generated by Django 4.1.1 on 2023-01-16 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_searchindex_brand_name'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='feargreedindexdaily',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='feargreedindexdaily',
            name='market_index',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='feargreedindexdaily',
            name='market_index_1d',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='feargreedindexdaily',
            name='market_index_diff',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='feargreedindexdaily',
            name='momentum',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='feargreedindexdaily',
            name='momentum_diff',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='feargreedindexdaily',
            name='price_breadth',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='feargreedindexdaily',
            name='price_breadth_diff',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='feargreedindexdaily',
            name='price_strength',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='feargreedindexdaily',
            name='rsi',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='feargreedindexdaily',
            name='volatility',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='feargreedindexdaily',
            name='volatility_sma',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='feargreedindexdaily',
            name='date',
            field=models.DateField(db_index=True, unique=True),
        ),
        migrations.AlterField(
            model_name='feargreedindexdaily',
            name='datetime',
            field=models.DateTimeField(),
        ),
        migrations.RemoveField(
            model_name='feargreedindexdaily',
            name='exchange',
        ),
    ]
