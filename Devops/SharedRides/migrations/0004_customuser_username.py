# Generated by Django 4.2.2 on 2023-11-10 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SharedRides', '0003_alter_customuser_first_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='username',
            field=models.CharField(default='aAakrit', max_length=150, unique=True),
        ),
    ]
