# Generated by Django 4.1.6 on 2023-04-22 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eab', '0053_alter_experience_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parcours',
            name='niveau',
            field=models.CharField(choices=[('Baccalauréat', 'Baccalauréat'), ('Bac + 1', 'Bac + 1'), ('Bac + 2', 'Bac + 2'), ('Bac + 3', 'Bac + 3'), ('Bac + 4', 'Bac + 4'), ('Bac + 5', 'Bac + 5'), ('Bac + 6', 'Bac + 6'), ('Bac + 7', 'Bac + 7')], max_length=200, null=True),
        ),
    ]
