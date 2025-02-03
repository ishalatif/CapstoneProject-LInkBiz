# Generated by Django 5.1.3 on 2024-12-07 13:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Linkbiz', '0005_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pendanaan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nominal_dana', models.IntegerField()),
                ('bukti_transfer', models.ImageField(upload_to='bukti_transfer/')),
                ('tanggal_pendanaan', models.DateTimeField(auto_now_add=True)),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pendanaan_investor', to='Linkbiz.profile_investor')),
                ('umkm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pendanaan_umkm', to='Linkbiz.umkm')),
            ],
        ),
    ]
