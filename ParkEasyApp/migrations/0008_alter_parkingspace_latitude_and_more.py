# Generated by Django 5.1.4 on 2025-01-16 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ParkEasyApp', '0007_alter_parkingspace_price_per_hour'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parkingspace',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='parkingspace',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]