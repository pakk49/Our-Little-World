import base64
import json
import os
from io import BytesIO
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Q
from django.http import Http404,FileResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from PIL import Image,UnidentifiedImageError
from .models import Memory,Photo,Note,Lesson
from .forms import MemoryForm,NoteForm,LessonForm

MAX_IMAGE=8*1024*1024
def checked_image(file):
    if file.size>MAX_IMAGE: raise ValueError("รูปต้องไม่เกิน 8MB")
    blob=file.read()
    try:
        with Image.open(BytesIO(blob)) as image:
            image.verify()
        with Image.open(BytesIO(blob)) as image:
            ext={"JPEG":".jpg","PNG":".png","WEBP":".webp"}.get(image.format)
            if not ext or image.width*image.height>35000000: raise ValueError("รองรับ JPG PNG WEBP ขนาดไม่เกิน 35 ล้านพิกเซล")
    except (OSError,UnidentifiedImageError,Image.DecompressionBombError) as exc:
        raise ValueError("ไฟล์รูปไม่ถูกต้อง") from exc
    return ContentFile(blob,name="photo"+ext)

def save(form,owner_field,request):
    if not form.is_valid(): return False
    obj=form.instance
    with transaction.atomic():
        if obj.pk:
            current=type(obj).objects.select_for_update().get(pk=obj.pk)
            if form.cleaned_data["revision"]!=current.revision:
                form.add_error(None,"ข้อมูลถูกแก้ไขจากอีกอุปกรณ์ กรุณาโหลดหน้าใหม่")
                return False
            obj.revision=current.revision+1
        else: setattr(obj,owner_field,request.user)
        obj=form.save(commit=False)
        if obj.pk: obj.revision=current.revision+1
        else: setattr(obj,owner_field,request.user)
        obj.save()
        form.instance=obj
        return True

@login_required
def home(request):
    return render(request,"world/home.html",{"items":Memory.objects.prefetch_related("photos")[:4],"total":Memory.objects.count(),"notes":Note.objects.filter(Q(private=False)|Q(author=request.user))[:3]})
@login_required
def memories(request):
    return render(request,"world/memories.html",{"items":Memory.objects.prefetch_related("photos")})
@login_required
def memory_edit(request,pk=None):
    obj=get_object_or_404(Memory,pk=pk) if pk else Memory(author=request.user)
    form=MemoryForm(request.POST or None,instance=obj)
    if request.method=="POST":
        uploads=request.FILES.getlist("images")
        if len(uploads)+(obj.photos.count() if obj.pk else 0)>8:
            form.add_error(None,"รูปภาพไม่เกิน 8 รูปต่อความทรงจำ")
        else:
            try: images=[checked_image(upload) for upload in uploads]
            except ValueError as exc: form.add_error(None,str(exc))
            else:
                if save(form,"author",request):
                    for image in images:
                        photo=Photo(memory=form.instance)
                        photo.image.save(image.name,image,save=True)
                    messages.success(request,"บันทึกความทรงจำแล้ว ♡")
                    return redirect("memories")
    return render(request,"world/form.html",{"form":form,"heading":"ความทรงจำ","upload":True})
@login_required
@require_POST
def memory_delete(request,pk):
    obj=get_object_or_404(Memory,pk=pk)
    for photo in obj.photos.all(): photo.image.delete(save=False)
    obj.delete()
    return redirect("memories")
@login_required
def notes(request):
    return render(request,"world/notes.html",{"items":Note.objects.filter(Q(private=False)|Q(author=request.user))})
@login_required
def note_edit(request,pk=None):
    obj=get_object_or_404(Note.objects.filter(Q(private=False)|Q(author=request.user)),pk=pk) if pk else Note(author=request.user)
    form=NoteForm(request.POST or None,instance=obj)
    if request.method=="POST" and save(form,"author",request):
        messages.success(request,"บันทึกแล้ว ♡")
        return redirect("notes")
    return render(request,"world/form.html",{"form":form,"heading":"บันทึกของเรา"})
@login_required
@require_POST
def note_delete(request,pk):
    get_object_or_404(Note.objects.filter(Q(private=False)|Q(author=request.user)),pk=pk).delete()
    return redirect("notes")
@login_required
def schedule(request):
    return render(request,"world/schedule.html",{"items":Lesson.objects.select_related("user")})
@login_required
def lesson_edit(request,pk=None):
    obj=get_object_or_404(Lesson,pk=pk,user=request.user) if pk else Lesson(user=request.user)
    form=LessonForm(request.POST or None,instance=obj)
    if request.method=="POST" and save(form,"user",request):
        messages.success(request,"บันทึกตารางเรียนแล้ว")
        return redirect("schedule")
    return render(request,"world/form.html",{"form":form,"heading":"รายวิชา"})
@login_required
@require_POST
def lesson_delete(request,pk):
    get_object_or_404(Lesson,pk=pk,user=request.user).delete()
    return redirect("schedule")
@login_required
def private_image(request,pk):
    photo=get_object_or_404(Photo,pk=pk)
    return redirect(photo.image.url) if settings.S3_BUCKET else FileResponse(photo.image.open("rb"),content_type="image/jpeg")
@login_required
def us(request):
    from django.contrib.auth import get_user_model
    return render(request,"world/us.html",{"members":get_user_model().objects.filter(is_active=True)[:2]})
@login_required
@require_POST
def scan(request):
    upload=request.FILES.get("image")
    if not upload:
        messages.error(request,"โปรดเลือกรูป")
        return redirect("schedule")
    try: blob=checked_image(upload)
    except ValueError as exc:
        messages.error(request,str(exc))
        return redirect("schedule")
    if not os.environ.get("OPENAI_API_KEY"):
        messages.error(request,"ต้องกำหนด OPENAI_API_KEY ก่อน")
        return redirect("schedule")
    try:
        from openai import OpenAI
        ext=blob.name.rsplit(".",1)[-1]
        mime={"jpg":"image/jpeg","png":"image/png","webp":"image/webp"}[ext]
        data=base64.b64encode(blob.read()).decode()
        result=OpenAI().chat.completions.create(
            model=os.environ.get("OPENAI_MODEL","gpt-4.1-mini"),
            response_format={"type":"json_object"},
            messages=[{"role":"system","content":"Extract lessons from timetable image. Return JSON object with classes array; each object must have subject, place, day (integer 0=Monday to 6=Sunday), start, end (HH:MM 24h). Exclude uncertain records. Never fabricate."},{"role":"user","content":[{"type":"text","text":"Read this schedule"},{"type":"image_url","image_url":{"url":"data:"+mime+";base64,"+data}}]}],
            timeout=40)
        obj=json.loads(result.choices[0].message.content)
        rows=[]
        for item in obj.get("classes",[])[:30]:
            form=LessonForm(item)
            if form.is_valid():
                row=form.cleaned_data
                rows.append({"subject":row["subject"],"place":row["place"],"day":row["day"],"start":row["start"].strftime("%H:%M"),"end":row["end"].strftime("%H:%M")})
        request.session["pending_schedule"]=rows
        return render(request,"world/scan.html",{"rows":rows})
    except Exception:
        messages.error(request,"อ่านรูปไม่สำเร็จ กรุณาเพิ่มตารางเรียนเองหรือลองภาพใหม่")
        return redirect("schedule")
@login_required
@require_POST
def scan_confirm(request):
    rows=request.session.pop("pending_schedule",[])
    for row in rows:
        form=LessonForm(row)
        if form.is_valid():
            obj=form.save(commit=False)
            obj.user=request.user
            obj.save()
    messages.success(request,"เพิ่มตารางเรียนแล้ว")
    return redirect("schedule")
