# Generated by Django 4.1.1 on 2025-03-07 07:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0072_alter_marketindexstock_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundnavanalytics',
            name='fund',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.mutualfund'),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='annualized_return_n_year',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='annualized_return_percentage',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='change_percentage_1m',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='change_percentage_1w',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='change_percentage_1y',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='change_percentage_3m',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='change_percentage_3y',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='change_percentage_5y',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='change_percentage_6m',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='change_percentage_inception_date',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='change_percentage_ytd',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='fund',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.mutualfund'),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='maximum_drawdown_percentage',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='nav_1m',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='nav_1w',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='nav_1y',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='nav_3m',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='nav_3y',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='nav_5y',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='nav_6m',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='nav_inception_date',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundnavindex',
            name='nav_ytd',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='mutualfundpricechart',
            name='fund',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.mutualfund'),
        ),
        migrations.AlterModelTable(
            name='mutualfundnavindex',
            table='fund_nav',
        ),
        migrations.AlterModelTable(
            name='mutualfundpricechart',
            table='fund_nav_chart',
        ),
    ]
