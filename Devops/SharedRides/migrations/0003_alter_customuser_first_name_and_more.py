# Generated by Django 4.2.2 on 2023-11-10 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SharedRides', '0002_remove_customuser_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(max_length=128, null=True, verbose_name='First Name'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(max_length=128, null=True, verbose_name='Last Name'),
        ),
    ]
