# Generated by Django 4.1.1 on 2024-10-01 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0065_delete_etfiindexdaily_delete_etfnavdaily_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fb_volume_1d',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fb_volume_1m',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fb_volume_1w',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fb_volume_1y',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fb_volume_3m',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fb_volume_3y',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fb_volume_5y',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fb_volume_6m',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fs_volume_1d',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fs_volume_1m',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fs_volume_1w',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fs_volume_1y',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fs_volume_3m',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fs_volume_3y',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fs_volume_5y',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='fs_volume_6m',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='last_price_1d',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='last_price_1m',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='last_price_1w',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='last_price_1y',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='last_price_3m',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='last_price_3y',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='last_price_5y',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='last_price_6m',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='last_price_inception_date',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='last_price_ytd',
        ),
        migrations.RemoveField(
            model_name='etfpricechart',
            name='last_volume_1d',
        ),
        migrations.AddField(
            model_name='etfpricechart',
            name='price_1d',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='etfpricechart',
            name='price_1m',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='etfpricechart',
            name='price_1w',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='etfpricechart',
            name='price_1y',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='etfpricechart',
            name='price_3m',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='etfpricechart',
            name='price_3y',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='etfpricechart',
            name='price_5y',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='etfpricechart',
            name='price_6m',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='etfpricechart',
            name='price_inception_date',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='etfpricechart',
            name='price_ytd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='etfpricechart',
            name='volume_1d',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='change_percentage_1m',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='change_percentage_1w',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='change_percentage_1y',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='change_percentage_3m',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='change_percentage_3y',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='change_percentage_5y',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='change_percentage_6m',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='change_percentage_inception_date',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='change_percentage_ytd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='movement_1m',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='movement_1w',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='movement_1y',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='movement_3m',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='movement_3y',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='movement_5y',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='movement_6m',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='reference',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='volume_1m',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='volume_1w',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='volume_1y',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='volume_3m',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='volume_3y',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='volume_5y',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='etfpricechart',
            name='volume_6m',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20, null=True),
        ),
    ]
