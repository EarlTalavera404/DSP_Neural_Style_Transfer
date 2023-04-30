# Generated by Django 4.1.7 on 2023-04-18 11:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('neural_art_transfer', '0002_alter_algorithmpreference_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='images',
            name='user_id',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
