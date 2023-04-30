# Generated by Django 4.1.7 on 2023-04-19 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neural_art_transfer', '0003_alter_images_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='algorithmpreference',
            name='algorithm',
            field=models.CharField(choices=[('Original', 'Original'), ('Histogram', 'Histogram'), ('Normalised', 'Normalised'), ('Combined', 'Combined')], max_length=10),
        ),
    ]
