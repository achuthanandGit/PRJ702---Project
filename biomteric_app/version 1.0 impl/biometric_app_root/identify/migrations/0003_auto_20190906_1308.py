# Generated by Django 2.2.4 on 2019-09-06 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identify', '0002_auto_20190906_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fishdata',
            name='imageUrl',
            field=models.ImageField(blank=True, upload_to='dataset/'),
        ),
    ]
