from django import forms
from django.core.exceptions import ValidationError
from .models import Memory,Note,Lesson
class RevisionForm(forms.ModelForm):
    revision=forms.IntegerField(widget=forms.HiddenInput,required=False)
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if self.instance.pk and not self.is_bound:
            self.fields["revision"].initial=self.instance.revision
class MemoryForm(RevisionForm):
    class Meta:
        model=Memory
        fields=["title","place","date","description"]
        widgets={"date":forms.DateInput(attrs={"type":"date"})}
class NoteForm(RevisionForm):
    class Meta:
        model=Note
        fields=["title","body","type","private"]
class LessonForm(RevisionForm):
    class Meta:
        model=Lesson
        fields=["subject","place","day","start","end"]
        widgets={"start":forms.TimeInput(attrs={"type":"time"},format="%H:%M"),"end":forms.TimeInput(attrs={"type":"time"},format="%H:%M")}
    def clean(self):
        c=super().clean()
        if c.get("start") and c.get("end") and c["start"]>=c["end"]:
            raise ValidationError("เวลาเลิกต้องอยู่หลังเวลาเริ่ม")
        return c
