from django.conf import settings
from django.db import migrations,models
import django.db.models.deletion
class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.CreateModel(name="Memory",fields=[("id",models.BigAutoField(primary_key=True,serialize=False)),("title",models.CharField(max_length=160)),("place",models.CharField(blank=True,max_length=180)),("date",models.DateField()),("description",models.TextField(blank=True)),("revision",models.PositiveIntegerField(default=1)),("updated_at",models.DateTimeField(auto_now=True)),("author",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL))],options={"ordering":["-date","-id"]}),
        migrations.CreateModel(name="Photo",fields=[("id",models.BigAutoField(primary_key=True,serialize=False)),("image",models.ImageField(upload_to="photos/%Y/%m/")),("memory",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="photos",to="world.memory"))]),
        migrations.CreateModel(name="Note",fields=[("id",models.BigAutoField(primary_key=True,serialize=False)),("title",models.CharField(max_length=160)),("body",models.TextField()),("type",models.CharField(choices=[("note","บันทึก"),("like","สิ่งที่ชอบ"),("wish","สิ่งที่อยากทำ")],default="note",max_length=8)),("private",models.BooleanField(default=False)),("revision",models.PositiveIntegerField(default=1)),("updated_at",models.DateTimeField(auto_now=True)),("author",models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,to=settings.AUTH_USER_MODEL))],options={"ordering":["-updated_at"]}),
        migrations.CreateModel(name="Lesson",fields=[("id",models.BigAutoField(primary_key=True,serialize=False)),("subject",models.CharField(max_length=160)),("place",models.CharField(blank=True,max_length=160)),("day",models.IntegerField(choices=[(0,"จันทร์"),(1,"อังคาร"),(2,"พุธ"),(3,"พฤหัสบดี"),(4,"ศุกร์"),(5,"เสาร์"),(6,"อาทิตย์")])),("start",models.TimeField()),("end",models.TimeField()),("revision",models.PositiveIntegerField(default=1)),("updated_at",models.DateTimeField(auto_now=True)),("user",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL))],options={"ordering":["day","start"]}),
    ]
