# Generated by Django 2.1.7 on 2019-07-31 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bbscopy', '0006_auto_20190731_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question_text',
            field=models.TextField(default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_title',
            field=models.CharField(max_length=40),
        ),
    ]