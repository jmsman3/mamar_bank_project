# Generated by Django 5.0.6 on 2024-08-04 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_remove_userbankaccount_is_bankrupt'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbankaccount',
            name='is_bankrupt',
            field=models.BooleanField(default=False),
        ),
    ]
