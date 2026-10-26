import base64
import json
import os
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse, HttpResponseRedirect
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Memory, Note, Lesson, Photo
from .forms import MemoryForm, NoteForm, LessonForm
from .views import checked_image

def fail(message, code=400):
    return Response({"detail":message},status=code)

def serialize(obj):
    if isinstance(obj,Memory):
        return {"id":obj.pk,"title":obj.title,"place":obj.place,"date":str(obj.date),"description":obj.description,"revision":obj.revision,"photo_ids":list(obj.photos.values_list("pk",flat=True))}
    if isinstance(obj,Note):
        return {"id":obj.pk,"title":obj.title,"body":obj.body,"type":obj.type,"type_label":obj.get_type_display(),"private":obj.private,"author":obj.author.username,"revision":obj.revision}
    return {"id":obj.pk,"subject":obj.subject,"place":obj.place,"day":obj.day,"start":obj.start.strftime("%H:%M"),"end":obj.end.strftime("%H:%M"),"user":obj.user.username,"user_id":obj.user_id,"revision":obj.revision}

class LoginThrottle(AnonRateThrottle):
    rate="8/min"

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle])
def login(request):
    user=authenticate(request,username=request.data.get("username",""),password=request.data.get("password",""))
    if not user or not user.is_active:
        return fail("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง",401)
    token,_=Token.objects.get_or_create(user=user)
    return Response({"token":token.key,"user":{"id":user.id,"username":user.username}})

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    if request.auth: request.auth.delete()
    return Response({"ok":True})

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({"user":{"id":request.user.pk,"username":request.user.username}})

def list_or_create(request,model,form_class,owner,queryset):
    if request.method=="GET":return Response({"items":[serialize(x) for x in queryset]})
    form=form_class(request.data)
    if not form.is_valid():return Response(form.errors,status=400)
    if model is Memory:
        images=request.FILES.getlist("images")
        if len(images)>8:return fail("รูปภาพเกิน 8 รูป")
        try:prepared=[checked_image(i) for i in images if i.size]
        except ValueError as e:return fail(str(e))
    with transaction.atomic():
        obj=form.save(commit=False)
        setattr(obj,owner,request.user)
        obj.save()
        if model is Memory:
            for content in prepared:
                photo=Photo(memory=obj)
                photo.image.save(content.name,content,save=True)
    return Response(serialize(obj),status=201)

def detail(request,model,form_class,queryset):
    obj=queryset.select_for_update().get(pk=request.resolved_pk)
    if request.method=="DELETE":
        if isinstance(obj,Memory):
            for p in obj.photos.all():p.image.delete(save=False)
        obj.delete()
        return Response(status=204)
    form=form_class(request.data,instance=obj)
    if not form.is_valid():return Response(form.errors,status=400)
    if form.cleaned_data.get("revision")!=obj.revision:return fail("ข้อมูลมีการแก้ไขจากอุปกรณ์อื่น กรุณาโหลดหน้าใหม่",409)
    if isinstance(obj,Memory):
        images=request.FILES.getlist("images")
        if obj.photos.count()+len(images)>8:return fail("รูปภาพเกิน 8 รูป")
        try:prepared=[checked_image(i) for i in images if i.size]
        except ValueError as e:return fail(str(e))
    changed=form.save(commit=False);changed.revision=obj.revision+1;changed.save()
    if isinstance(obj,Memory):
        for content in prepared:
            p=Photo(memory=changed)
            p.image.save(content.name,content,save=True)
    return Response(serialize(changed))

@api_view(["GET","POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def memories(request):
    return list_or_create(request,Memory,MemoryForm,"author",Memory.objects.prefetch_related("photos"))

@api_view(["PUT","DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def memory_detail(request,pk):
    if not Memory.objects.filter(pk=pk).exists():return fail("ไม่พบความทรงจำ",404)
    request.resolved_pk=pk
    with transaction.atomic():
        return detail(request,Memory,MemoryForm,Memory.objects.all())

@api_view(["GET","POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def notes(request):
    return list_or_create(request,Note,NoteForm,"author",Note.objects.filter(Q(private=False)|Q(author=request.user)))

@api_view(["PUT","DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def note_detail(request,pk):
    if not Note.objects.filter(pk=pk).filter(Q(private=False)|Q(author=request.user)).exists():return fail("ไม่พบโน้ต",404)
    request.resolved_pk=pk
    with transaction.atomic():
        return detail(request,Note,NoteForm,Note.objects.filter(Q(private=False)|Q(author=request.user)))

@api_view(["GET","POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def lessons(request):
    return list_or_create(request,Lesson,LessonForm,"user",Lesson.objects.select_related("user"))

@api_view(["PUT","DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def lesson_detail(request,pk):
    if not Lesson.objects.filter(pk=pk,user=request.user).exists():return fail("ไม่มีสิทธิ์แก้ไขรายวิชานี้",404)
    request.resolved_pk=pk
    with transaction.atomic():
        return detail(request,Lesson,LessonForm,Lesson.objects.filter(user=request.user))

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def photo(request,pk):
    from django.shortcuts import get_object_or_404
    item=get_object_or_404(Photo,pk=pk)
    if os.environ.get("S3_BUCKET"):
        return HttpResponseRedirect(item.image.url)
    return FileResponse(item.image.open("rb"),content_type="image/jpeg")

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def scan(request):
    upload=request.FILES.get("image")
    if not upload:return fail("ไม่ได้เลือกรูปตารางเรียน")
    try: blob=checked_image(upload)
    except ValueError as e:return fail(str(e))
    if not os.environ.get("OPENAI_API_KEY"):return fail("Backend ยังไม่เปิดระบบ AI")
    try:
        from openai import OpenAI
        ext=blob.name.rsplit(".",1)[-1]
        mime={"jpg":"image/jpeg","png":"image/png","webp":"image/webp"}[ext]
        encoded=base64.b64encode(blob.read()).decode("ascii")
        result=OpenAI().chat.completions.create(model=os.environ.get("OPENAI_MODEL","gpt-4.1-mini"),response_format={"type":"json_object"},messages=[{"role":"system","content":"Read a timetable image. Return JSON with classes array containing subject,place,day (0 Monday through 6 Sunday),start,end in HH:MM. Omit uncertain rows. Never fabricate."},{"role":"user","content":[{"type":"text","text":"Extract schedule"},{"type":"image_url","image_url":{"url":"data:"+mime+";base64,"+encoded}}]}],timeout=40)
        entries=json.loads(result.choices[0].message.content).get("classes",[])
        rows=[]
        if not isinstance(entries,list):return fail("ผลลัพธ์ AI ไม่ถูกต้อง")
        for item in entries[:30]:
            f=LessonForm(item)
            if f.is_valid():
                d=f.cleaned_data
                rows.append({"subject":d["subject"],"place":d["place"],"day":d["day"],"start":d["start"].strftime("%H:%M"),"end":d["end"].strftime("%H:%M")})
        return Response({"rows":rows})
    except Exception:return fail("AI อ่านภาพไม่สำเร็จ กรุณาลองใหม่",502)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def scan_confirm(request):
    rows=request.data.get("rows",[])
    if not isinstance(rows,list) or len(rows)>30:return fail("ข้อมูลไม่ถูกต้อง")
    forms=[LessonForm(row) for row in rows]
    if any(not f.is_valid() for f in forms):return fail("ตารางมีข้อมูลไม่ถูกต้อง")
    with transaction.atomic():
        for f in forms:
            obj=f.save(commit=False)
            obj.user=request.user
            obj.save()
    return Response({"count":len(forms)})
