# Generated by Django 5.0.6 on 2024-07-14 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('energyMeter', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='configData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sync_duration', models.IntegerField()),
                ('load_deactivation_duration', models.IntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('load_threshold', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.AddField(
            model_name='meterdata',
            name='power_factor',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='meterdata',
            name='save_counter',
            field=models.IntegerField(default=1),
        ),
    ]