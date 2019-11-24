# Generated by Django 2.2.4 on 2019-09-05 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identify', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FishData',
            fields=[
                ('imageId', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('imageUrl', models.ImageField(blank=True, upload_to='dataset/')),
                ('spots', models.TextField(blank=True)),
                ('refNose', models.TextField(blank=True)),
                ('refHead', models.TextField(blank=True)),
                ('refTail', models.TextField(blank=True)),
                ('population', models.CharField(blank=True, max_length=100)),
                ('tank', models.CharField(max_length=100)),
                ('date', models.CharField(blank=True, max_length=50)),
                ('time', models.CharField(blank=True, max_length=50)),
            ],
        ),
    ]