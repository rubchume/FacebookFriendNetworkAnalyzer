# Generated by Django 3.2.5 on 2021-07-07 10:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ScanInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('user', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='networks')),
            ],
        ),
        migrations.DeleteModel(
            name='LogEvents',
        ),
        migrations.AddField(
            model_name='logevent',
            name='scan_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.scaninstance'),
        ),
    ]