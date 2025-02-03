# Generated by Django 5.1.3 on 2024-12-12 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Linkbiz', '0009_remove_profile_investor_perjanjian_pendanaan_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pendanaan',
            name='denda',
        ),
        migrations.AlterField(
            model_name='pendanaan',
            name='status_pendanaan',
            field=models.CharField(blank=True, choices=[('Lancar', 'Lancar'), ('Terlambat 30-60 Hari', 'Terlambat 30-60 Hari'), ('Terlambat 61-90 Hari', 'Terlambat 61-90 Hari'), ('Kurang Lancar > 90 Hari', 'Kurang Lancar > 90 Hari')], max_length=50, null=True),
        ),
    ]
