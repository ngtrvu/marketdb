# Generated by Django 4.1.1 on 2024-10-16 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0069_etfpricechart_price_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ETFPriceAnalytics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('symbol', models.CharField(db_index=True, max_length=50, unique=True)),
                ('datetime', models.DateTimeField()),
                ('reference', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('price_1d', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('volume_1d', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('total_trading_value', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('price_1w', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('price_1m', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('price_3m', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('price_6m', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('price_1y', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('price_3y', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('price_5y', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('price_ytd', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('price_inception_date', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('change_percentage_1w', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('change_percentage_1m', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('change_percentage_3m', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('change_percentage_6m', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('change_percentage_1y', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('change_percentage_3y', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('change_percentage_5y', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('change_percentage_ytd', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('change_percentage_inception_date', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('volume_1w', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True)),
                ('volume_1m', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True)),
                ('volume_3m', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True)),
                ('volume_6m', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True)),
                ('volume_1y', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True)),
                ('volume_3y', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True)),
                ('volume_5y', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True)),
                ('volume_ytd', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True)),
            ],
            options={
                'verbose_name_plural': 'etf_price_analytics',
                'db_table': 'etf_price_analytics',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='ETFPriceRealtime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('symbol', models.CharField(db_index=True, max_length=50, unique=True)),
                ('datetime', models.DateTimeField()),
                ('exchange', models.CharField(blank=True, db_index=True, max_length=50, null=True)),
                ('type', models.CharField(db_index=True, default='ETF', max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=20)),
                ('volume', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('fb_volume', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('fs_volume', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('foreign_room', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('total_trading_value', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('open', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('close', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('high', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('low', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('reference', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('ceiling', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('floor', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('change_percentage_1d', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('market_cap', models.DecimalField(decimal_places=0, max_digits=50, null=True)),
                ('outstanding_shares', models.DecimalField(decimal_places=0, max_digits=20, null=True)),
                ('ordering', models.IntegerField(blank=True, db_index=True, null=True)),
            ],
            options={
                'db_table': 'etf_price_realtime',
                'ordering': ('-created',),
            },
        ),
        migrations.AddField(
            model_name='etfpricechart',
            name='movement_ytd',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='etfpricechart',
            name='volume_ytd',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='stockpricechart',
            name='movement_1m',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='stockpricechart',
            name='movement_1w',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='stockpricechart',
            name='movement_1y',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='stockpricechart',
            name='movement_3m',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='stockpricechart',
            name='movement_3y',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='stockpricechart',
            name='movement_5y',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='stockpricechart',
            name='movement_6m',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='stockpricechart',
            name='movement_ytd',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='stockpricechart',
            name='reference',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
    ]
