# Generated by Django 2.2.14 on 2020-12-16 07:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('buckets', '0014_bucket_lock'),
    ]

    operations = [
        migrations.CreateModel(
            name='BucketToken',
            fields=[
                ('key', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='键')),
                ('permission', models.CharField(choices=[('readwrite', '可读写'), ('readonly', '只读')], default='readwrite', max_length=20, verbose_name='访问权限')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('bucket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='token_set', to='buckets.Bucket', verbose_name='存储桶')),
            ],
            options={
                'verbose_name': '存储桶Token',
                'verbose_name_plural': '存储桶Token',
                'db_table': 'bucket_token',
            },
        ),
    ]
