# Generated by Django 5.1.3 on 2024-11-29 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Linkbiz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile_investor',
            name='foto',
            field=models.ImageField(default='default_foto.jpeg', upload_to='foto_investor/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='umkm',
            name='foto_umkm',
            field=models.ImageField(upload_to='foto_umkm/'),
        ),
    ]
