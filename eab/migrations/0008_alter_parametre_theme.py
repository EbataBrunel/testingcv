# Generated by Django 4.1.6 on 2023-03-06 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eab', '0007_alter_parametre_theme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametre',
            name='theme',
            field=models.CharField(choices=[('primary', 'Primary'), ('info', 'Info'), ('success', 'Success'), ('danger', 'Danger'), ('secondary', 'Secondary'), ('dark', 'Dark')], max_length=200, null=True),
        ),
    ]