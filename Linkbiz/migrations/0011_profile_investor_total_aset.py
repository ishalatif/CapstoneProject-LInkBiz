# Generated by Django 5.1.3 on 2024-12-13 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Linkbiz', '0010_remove_pendanaan_denda_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile_investor',
            name='total_aset',
            field=models.IntegerField(default=0),
        ),
    ]
