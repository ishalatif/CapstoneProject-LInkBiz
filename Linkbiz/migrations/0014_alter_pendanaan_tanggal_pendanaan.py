# Generated by Django 5.1.3 on 2024-12-14 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Linkbiz', '0013_remove_profile_investor_total_aset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pendanaan',
            name='tanggal_pendanaan',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
