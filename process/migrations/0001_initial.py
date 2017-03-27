# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='App_Incidence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('removed', models.DateTimeField(default=None, null=True, editable=False, blank=True)),
                ('longitude', models.DecimalField(verbose_name=b'\xe7\xbb\x8f\xe5\xba\xa6', max_digits=10, decimal_places=7)),
                ('latitude', models.DecimalField(verbose_name=b'\xe7\xba\xac\xe5\xba\xa6', max_digits=10, decimal_places=7)),
                ('place', models.TextField(verbose_name=b'\xe5\x9c\xb0\xe7\x82\xb9')),
                ('create_time', models.DateTimeField(verbose_name=b'\xe4\xb8\xbe\xe6\x8a\xa5\xe6\x97\xb6\xe9\x97\xb4')),
                ('region', models.SmallIntegerField(default=0, verbose_name=b'\xe5\x8c\xba\xe5\x8e\xbf\xe7\xbc\x96\xe5\x8f\xb7')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Call_Incidence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('removed', models.DateTimeField(default=None, null=True, editable=False, blank=True)),
                ('region', models.SmallIntegerField(default=0, verbose_name=b'\xe5\x8c\xba\xe5\x8e\xbf\xe7\xbc\x96\xe5\x8f\xb7')),
                ('create_time', models.DateTimeField(verbose_name=b'122\xe6\x8a\xa5\xe8\xad\xa6\xe6\x97\xb6\xe9\x97\xb4')),
                ('longitude', models.DecimalField(verbose_name=b'\xe7\xbb\x8f\xe5\xba\xa6', max_digits=10, decimal_places=7)),
                ('latitude', models.DecimalField(verbose_name=b'\xe7\xba\xac\xe5\xba\xa6', max_digits=10, decimal_places=7)),
                ('event_content', models.TextField(verbose_name=b'\xe4\xba\x8b\xe4\xbb\xb6\xe6\x8f\x8f\xe8\xbf\xb0')),
                ('place', models.TextField(verbose_name=b'\xe5\x9c\xb0\xe7\x82\xb9')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Crowd_Index',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('removed', models.DateTimeField(default=None, null=True, editable=False, blank=True)),
                ('region', models.SmallIntegerField(default=0, verbose_name=b'\xe5\x8c\xba\xe5\x8e\xbf\xe7\xbc\x96\xe5\x8f\xb7')),
                ('bussiness_area', models.TextField(default=None, null=True, verbose_name=b'\xe5\x95\x86\xe5\x9c\x88\xe5\x90\x8d\xe7\xa7\xb0')),
                ('avg_car_speed', models.DecimalField(verbose_name=b'\xe5\xb9\xb3\xe5\x9d\x87\xe8\xbd\xa6\xe9\x80\x9f', max_digits=5, decimal_places=2)),
                ('crowd_index', models.DecimalField(verbose_name=b'\xe6\x8b\xa5\xe5\xa0\xb5\xe5\xbb\xb6\xe6\x97\xb6\xe6\x8c\x87\xe6\x95\xb0', max_digits=5, decimal_places=2)),
                ('create_time', models.DateTimeField(verbose_name=b'\xe6\x97\xb6\xe9\x97\xb4')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Police',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('removed', models.DateTimeField(default=None, null=True, editable=False, blank=True)),
                ('region', models.SmallIntegerField(default=0, verbose_name=b'\xe5\x8c\xba\xe5\x8e\xbf\xe7\xbc\x96\xe5\x8f\xb7')),
                ('people_cnt', models.IntegerField(verbose_name=b'\xe4\xba\xba\xe6\x95\xb0')),
                ('create_time', models.DateTimeField(verbose_name=b'\xe6\x97\xb6\xe9\x97\xb4')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Violation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('removed', models.DateTimeField(default=None, null=True, editable=False, blank=True)),
                ('breach_type', models.IntegerField(default=-1, verbose_name=b'\xe8\xbf\x9d\xe6\xb3\x95\xe7\xb1\xbb\xe5\x9e\x8b')),
                ('region', models.SmallIntegerField(default=0, verbose_name=b'\xe5\x8c\xba\xe5\x8e\xbf\xe7\xbc\x96\xe5\x8f\xb7')),
                ('longitude', models.DecimalField(verbose_name=b'\xe7\xbb\x8f\xe5\xba\xa6', max_digits=10, decimal_places=7)),
                ('latitude', models.DecimalField(verbose_name=b'\xe7\xba\xac\xe5\xba\xa6', max_digits=10, decimal_places=7)),
                ('create_time', models.DateTimeField(verbose_name=b'\xe4\xb8\xbe\xe6\x8a\xa5\xe6\x97\xb6\xe9\x97\xb4')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
