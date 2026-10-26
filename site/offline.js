// Browser-only preview: NOT persisted online or shared between devices.
(function(){
const el=document.getElementById("app"),nav=document.getElementById("nav"),status=document.getElementById("status");
const days=["จันทร์","อังคาร","พุธ","พฤหัสบดี","ศุกร์","เสาร์","อาทิตย์"];
let records={memories:[],notes:[],schedule:[]};
const escape=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const notice='<div class="alert"><b>โหมดทดลองใช้งาน (Preview)</b> — เมนูและแบบฟอร์มใช้งานได้ แต่ข้อมูลเก็บชั่วคราวในหน้านี้เท่านั้น ไม่ส่งขึ้นฐานข้อมูล ไม่ซิงก์กับอีกเครื่อง และจะหายเมื่อรีเฟรชหน้า กรุณาอย่าใส่ข้อมูลส่วนตัวจริง</div>';
const hero='<section class="hero"><div class="eyebrow">OUR STORY, FOREVER</div><h1>โลกใบเล็กที่มี<br><span class="rose">แค่เราสองคน ♡</span></h1><p>เก็บทุกความทรงจำและเรื่องราวพิเศษของเรา</p><div class="buttons"><a class="btn" href="#memories">เปิดอัลบั้ม</a><a class="btn secondary" href="#notes">เขียนโน้ต</a></div></section>';
function card(t,html){return '<article class="card">'+t+html+'</article>'}
function all(section){
let rows=records[section],labels={memories:"ความทรงจำ",notes:"บันทึกของเรา",schedule:"ตารางเรียน"};
let list=rows.map((r,i)=>card('<div class="eyebrow">'+(section==="schedule"?days[+r.day]+" · "+escape(r.start)+" - "+escape(r.end):section==="notes"?escape(r.type):escape(r.date))+'</div><h3>'+escape(r.title||r.subject)+'</h3>',(r.image?'<img class="cover" src="'+r.image+'" alt="ภาพทดลอง">':'')+'<p>'+escape(r.description||r.body||r.place)+'</p><div class="buttons"><button class="btn secondary" data-action="edit" data-section="'+section+'" data-id="'+i+'">แก้ไข</button><button class="danger" data-action="delete" data-section="'+section+'" data-id="'+i+'">ลบ</button></div>')).join("");
return '<div class="heading"><h1>'+labels[section]+' ♡</h1><a class="btn" href="#'+section+'/new">+ เพิ่มรายการ</a></div>'+(section==="schedule"?card("<h3>✨ AI อ่านภาพตารางเรียน</h3>","<p>ฟีเจอร์นี้ต้องเชื่อม Backend และ OpenAI API ก่อน</p>"):"")+'<div class="grid">'+(list||'<div class="card empty">ยังไม่มีรายการ ลองกดปุ่มเพิ่มได้เลย ♡</div>')+'</div>'
}
function form(section,id){let old=id==="new"?{}:records[section][+id]||{},input=(name,label,value="",type="text")=>'<label>'+label+'<input name="'+name+'" value="'+escape(value)+'" type="'+type+'" '+(name==="title"||name==="subject"?"required":"")+'></label>';
let html='';
if(section==="memories")html=input("title","ชื่อความทรงจำ",old.title)+input("place","สถานที่",old.place)+input("date","วันที่",old.date,"date")+'<label>เรื่องราว<textarea name="description">'+escape(old.description)+'</textarea></label><label>รูปภาพสำหรับทดลอง<input type="file" name="image" accept="image/png,image/jpeg,image/webp"></label>';
if(section==="notes")html=input("title","ชื่อบันทึก",old.title)+'<label>ประเภท<select name="type"><option>บันทึก</option><option>สิ่งที่ชอบ</option><option>สิ่งที่อยากทำ</option></select></label><label>เนื้อหา<textarea name="body">'+escape(old.body)+'</textarea></label>';
if(section==="schedule")html=input("subject","วิชา",old.subject)+input("place","ห้องเรียน",old.place)+'<label>วัน<select name="day">'+days.map((d,i)=>'<option value="'+i+'" '+(old.day==i?"selected":"")+'>'+d+'</option>').join("")+'</select></label>'+input("start","เริ่ม",old.start,"time")+input("end","สิ้นสุด",old.end,"time");
return '<div class="card formcard"><div class="eyebrow">PREVIEW MODE</div><h1>เพิ่ม / แก้ไขรายการ ♡</h1><form id="preview-form" data-section="'+section+'" data-id="'+id+'">'+html+'<div class="buttons"><button class="btn">บันทึกชั่วคราว</button><a class="btn secondary" href="#'+section+'">ยกเลิก</a></div></form></div>';
}
window.ourworldPreview=function(){
nav.hidden=false;status.textContent="โหมดทดลอง";
const parts=(location.hash||"#home").slice(1).split("/"),section=parts[0],id=parts[1];
for(const a of nav.querySelectorAll("a"))a.setAttribute("aria-current",a.hash==="#"+section?"page":"false");
let body="";
if(section==="home")body=hero+'<div class="heading"><h2>ความทรงจำล่าสุด</h2><a href="#memories">ดูทั้งหมด →</a></div><div class="grid">'+records.memories.slice(-3).map(r=>card("<h3>"+escape(r.title)+"</h3>","<p>"+escape(r.place)+"</p>")).join("")+'</div>';
else if(["memories","notes","schedule"].includes(section))body=id!==undefined?form(section,id):all(section);
else if(section==="us")body=hero+card("<h2>เราสองคน ♡</h2>","<p>เมื่อเชื่อม Backend แล้ว จะสามารถบันทึกความทรงจำและแชร์ข้อมูลระหว่างสองบัญชีได้</p>");
else{location.hash="#home";return}
el.innerHTML=notice+body;
el.querySelectorAll("[data-action]").forEach(b=>b.onclick=()=>{const {section:s,id:i,action:a}=b.dataset;if(a==="edit")location.hash="#"+s+"/"+i;else if(confirm("ลบรายการนี้?")){records[s].splice(+i,1);window.ourworldPreview()}});
const frm=document.getElementById("preview-form");
if(frm)frm.onsubmit=async e=>{e.preventDefault();const fd=new FormData(frm),s=frm.dataset.section,id=frm.dataset.id;let row={};for(const [k,v] of fd)if(k!=="image")row[k]=v;
if(s==="memories"){const file=fd.get("image");if(file&&file.size){if(file.size>3*1024*1024)return alert("โหมดทดลองจำกัดรูปไม่เกิน 3 MB");row.image=await new Promise(resolve=>{const f=new FileReader();f.onload=()=>resolve(f.result);f.readAsDataURL(file)});}else if(id!=="new")row.image=records[s][+id].image;}
if(id==="new")records[s].push(row);else records[s][+id]=row;
location.hash="#"+s;window.ourworldPreview()};
};
})();
