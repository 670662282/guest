# Generated by Django 2.0.6 on 2018-07-19 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sign', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='numbers',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]