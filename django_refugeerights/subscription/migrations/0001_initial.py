# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djcelery', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contact_key', models.CharField(max_length=36)),
                ('to_addr', models.CharField(max_length=255)),
                ('messageset_id', models.IntegerField()),
                ('next_sequence_number', models.IntegerField(default=1)),
                ('lang', models.CharField(max_length=6)),
                ('active', models.BooleanField(default=True)),
                ('completed', models.BooleanField(default=False)),
                ('process_status', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('schedule', models.ForeignKey(related_name='subscriptions', to='djcelery.PeriodicTask')),
            ],
        ),
    ]
