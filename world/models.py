from django.db import models
from django.conf import settings
class Memory(models.Model):
    title=models.CharField(max_length=160)
    place=models.CharField(max_length=180,blank=True)
    date=models.DateField()
    description=models.TextField(blank=True)
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    revision=models.PositiveIntegerField(default=1)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=["-date","-id"]
    def __str__(self): return self.title
class Photo(models.Model):
    memory=models.ForeignKey(Memory,on_delete=models.CASCADE,related_name="photos")
    image=models.ImageField(upload_to="photos/%Y/%m/")
class Note(models.Model):
    TYPES=[("note","บันทึก"),("like","สิ่งที่ชอบ"),("wish","สิ่งที่อยากทำ")]
    title=models.CharField(max_length=160)
    body=models.TextField()
    type=models.CharField(max_length=8,choices=TYPES,default="note")
    private=models.BooleanField(default=False)
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    revision=models.PositiveIntegerField(default=1)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=["-updated_at"]
class Lesson(models.Model):
    DAYS=[(i,s) for i,s in enumerate(["จันทร์","อังคาร","พุธ","พฤหัสบดี","ศุกร์","เสาร์","อาทิตย์"])]
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    subject=models.CharField(max_length=160)
    place=models.CharField(max_length=160,blank=True)
    day=models.IntegerField(choices=DAYS)
    start=models.TimeField()
    end=models.TimeField()
    revision=models.PositiveIntegerField(default=1)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=["day","start"]
    def __str__(self): return self.subject
