# Generated by Django 2.1.7 on 2019-07-31 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bbscopy', '0005_auto_20190731_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question_title',
            field=models.CharField(max_length=50),
        ),
    ]