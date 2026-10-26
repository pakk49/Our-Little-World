const root=document.getElementById("app"),nav=document.getElementById("nav"),status=document.getElementById("status"),signout=document.getElementById("signout");
const BASE=(window.OUR_WORLD_API_BASE||"").replace(/\/$/,"");
let token=sessionStorage.getItem("ourworld_token")||"",me=null,cache={},images=[];
const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const days=["จันทร์","อังคาร","พุธ","พฤหัสบดี","ศุกร์","เสาร์","อาทิตย์"];
const date=v=>v?new Date(v+"T12:00:00").toLocaleDateString("th-TH",{day:"numeric",month:"short",year:"numeric"}):"";
const show=(html)=>{root.innerHTML=html;window.scrollTo({top:0,behavior:"instant"})};
function error(e){show('<div class="alert">'+esc(e.message||e)+'</div><div class="buttons"><button class="btn secondary" id="retry">ลองอีกครั้ง</button></div>');document.getElementById("retry").onclick=render}
async function api(path,{method="GET",body=null,form=false}={}){
  if(!BASE)throw new Error("ยังไม่ได้เชื่อม Backend: ผู้ดูแลต้องตั้งค่า API_BASE_URL ใน GitHub Actions Variables");
  const headers={};if(token)headers.Authorization="Token "+token;
  if(body&&!form)headers["Content-Type"]="application/json";
  let res;try{res=await fetch(BASE+"/api/"+path,{method,headers,body:body?(form?body:JSON.stringify(body)):undefined,cache:"no-store"})}catch{throw new Error("ติดต่อ Backend ไม่ได้ โปรดตรวจสอบ API_BASE_URL และ CORS")}
  let data;try{data=await res.json()}catch{data={detail:"Backend ส่งผลลัพธ์ที่อ่านไม่ได้"}}
  if(res.status===401){token="";sessionStorage.removeItem("ourworld_token");me=null}
  if(!res.ok)throw new Error(typeof data.detail==="string"?data.detail:JSON.stringify(data));
  return data
}
function template(){return '<div class="hero"><div class="eyebrow">OUR STORY, FOREVER</div><h1>โลกเล็ก ๆ ที่มี<br><span class="rose">แค่เราสองคน ♡</span></h1><p>เก็บทุกภาพ ทุกวันพิเศษ และเรื่องราวที่อยากจดจำไว้ด้วยกัน</p><div class="buttons"><a class="btn" href="#memories">เปิดสมุดความทรงจำ</a><a class="btn secondary" href="#notes">เขียนโน้ตถึงกัน</a></div></div>'}
function btn(t,p){return '<a class="btn" href="#'+p+'">+ '+t+'</a>'}
function photo(i){return i?'<img class="cover private-image" data-photo="'+Number(i)+'" alt="ภาพความทรงจำที่แชร์กัน">':'<div class="placeholder">♡</div>'}
async function hydrateImages(){for(const el of document.querySelectorAll("[data-photo]")){if(!token)return;try{let res=await fetch(BASE+"/api/photos/"+el.dataset.photo+"/",{headers:{Authorization:"Token "+token}});if(res.ok){let u=URL.createObjectURL(await res.blob());images.push(u);el.src=u}}catch{}}}
function memoryCard(x){return '<article class="polaroid">'+photo(x.photo_ids?.[0])+'<div class="card" style="border:none;box-shadow:none;padding:10px 6px"><h3>'+esc(x.title)+'</h3><p class="subtle">'+esc(x.place)+' · '+date(x.date)+'</p><p>'+esc(x.description)+'</p><a href="#memory/'+x.id+'">แก้ไขและเพิ่มรูป</a></div></article>'}
function noteCard(x){return '<article class="card"><div class="eyebrow">'+esc(x.type_label)+(x.private?" · ส่วนตัว":"")+'</div><h3>'+esc(x.title)+'</h3><p>'+esc(x.body)+'</p><p class="subtle">โดย '+esc(x.author)+'</p><a href="#note/'+x.id+'">แก้ไข</a></article>'}
async function fetchAll(){let [m,n,l]=await Promise.all([api("memories/"),api("notes/"),api("lessons/")]);cache={memories:m.items,notes:n.items,lessons:l.items}}
async function render(){
  images.forEach(URL.revokeObjectURL);images=[];
  const hash=(location.hash||"#home").slice(1),[section,id]=hash.split("/");
  if(!BASE){nav.hidden=true;signout.hidden=true;show(template()+'<div class="card"><h2>เตรียมพร้อมเปิดใช้งาน ♡</h2><p>หน้าเว็บบน GitHub Pages พร้อมแล้ว แต่ยังไม่ได้กำหนด URL ของ Django Backend จึงยังไม่สามารถเข้าสู่ระบบหรือบันทึกข้อมูลได้</p><p class="subtle">ผู้ดูแล: Deploy Django API ผ่าน HTTPS แล้วเพิ่ม Repository variable ชื่อ API_BASE_URL และรัน Workflow ใหม่</p></div>');return}
  if(!token){nav.hidden=true;signout.hidden=true;show('<div class="card login"><div class="eyebrow">JUST THE TWO OF US</div><h1>ยินดีต้อนรับกลับบ้าน ♡</h1><p class="lead">พื้นที่ส่วนตัวของเราสองคน</p><form id="login"><div class="field"><label>ชื่อผู้ใช้</label><input name="username" required autocomplete="username"></div><div class="field"><label>รหัสผ่าน</label><input type="password" name="password" required autocomplete="current-password"></div><button class="btn">เข้าสู่โลกของเรา</button></form></div>');document.getElementById("login").onsubmit=async e=>{e.preventDefault();let b=new FormData(e.currentTarget);try{let d=await api("login/",{method:"POST",body:{username:b.get("username"),password:b.get("password")}});token=d.token;sessionStorage.setItem("ourworld_token",token);me=d.user;location.hash="#home";await render()}catch(err){alert(err.message)}};return}
  try{
    if(!me)me=(await api("me/")).user;
    nav.hidden=false;signout.hidden=false;status.textContent="สวัสดี "+me.username;
    for(let link of nav.querySelectorAll("a"))link.setAttribute("aria-current",link.hash==="#"+section?"page":"false");
    if(!Object.keys(cache).length)await fetchAll();
    if(section==="home"){show(template()+'<div class="heading"><h2>ความทรงจำล่าสุด</h2><a href="#memories">ดูทั้งหมด →</a></div><div class="grid">'+(cache.memories.slice(0,3).map(memoryCard).join("")||'<div class="card empty">เริ่มบันทึกความทรงจำแรก ♡</div>')+'</div><div class="heading"><h2>โน้ตของเรา</h2><a href="#notes">ดูทั้งหมด →</a></div><div class="grid">'+cache.notes.slice(0,3).map(noteCard).join("")+'</div>')}
    else if(section==="memories"){show('<div class="heading"><div><div class="eyebrow">OUR MEMORY BOOK</div><h1>ความทรงจำ ♡</h1></div>'+btn("เพิ่มความทรงจำ","memory/new")+'</div><div class="grid">'+(cache.memories.map(memoryCard).join("")||'<div class="card empty">ยังไม่มีความทรงจำ</div>')+'</div>')}
    else if(section==="notes"){show('<div class="heading"><div><div class="eyebrow">OUR THOUGHTS</div><h1>บันทึกของเรา</h1></div>'+btn("เพิ่มโน้ต","note/new")+'</div><div class="grid">'+(cache.notes.map(noteCard).join("")||'<div class="card empty">เขียนโน้ตแรกได้เลย</div>')+'</div>')}
    else if(section==="schedule"){show('<div class="heading"><div><div class="eyebrow">OUR WEEKLY PLAN</div><h1>ตารางเรียนของเรา</h1></div>'+btn("เพิ่มวิชา","lesson/new")+'</div><div class="card"><h3>✨ อ่านตารางเรียนจากรูป</h3><p>AI จะเสนอรายการให้ตรวจสอบก่อนบันทึกจริง</p><form id="scan"><input type="file" name="image" accept="image/jpeg,image/png,image/webp" required><button class="btn">อ่านตาราง</button></form></div><div style="margin-top:22px">'+(cache.lessons.map(x=>'<div class="card lesson row"><div><div class="eyebrow">'+days[x.day]+' · '+esc(x.start)+'–'+esc(x.end)+'</div><h3>'+esc(x.subject)+'</h3><p class="subtle">'+esc(x.place)+' · '+esc(x.user)+'</p></div>'+(x.user_id===me.id?'<a href="#lesson/'+x.id+'">แก้ไข</a>':"")+'</div>').join("")||'<p class="empty">ยังไม่มีรายวิชา</p>')+'</div>');document.getElementById("scan").onsubmit=scanSubmit}
    else if(section==="us")show(template()+'<div class="card"><h2>เราสองคน ♡</h2><p>เรื่องราวดี ๆ เก็บไว้ตรงนี้สำหรับคนสำคัญของเรา</p><p class="subtle">บัญชีของคุณ: '+esc(me.username)+'</p></div>');
    else if(["memory","note","lesson"].includes(section))await formView(section,id);
    else location.hash="#home";
    await hydrateImages()
  }catch(e){error(e)}
}
function field(label,name,value="",type="text",required=false){return '<div class="field"><label for="f_'+name+'">'+label+'</label><input id="f_'+name+'" name="'+name+'" type="'+type+'" value="'+esc(value)+'" '+(required?"required":"")+'></div>'}
function textarea(label,name,value=""){return '<div class="field"><label for="f_'+name+'">'+label+'</label><textarea id="f_'+name+'" name="'+name+'">'+esc(value)+'</textarea></div>'}
async function formView(kind,id){const isNew=id==="new",collection={memory:"memories",note:"notes",lesson:"lessons"}[kind],x=isNew?{}:cache[collection].find(x=>x.id===Number(id));if(!x){if(!isNew)throw Error("ไม่พบข้อมูล");}let html='<div class="card formcard"><div class="eyebrow">MADE WITH LOVE</div><h1>'+{memory:"ความทรงจำ",note:"บันทึก",lesson:"รายวิชา"}[kind]+'</h1><form id="record">';
if(kind==="memory"){html+=field("ชื่อความทรงจำ","title",x?.title,"text",true)+field("สถานที่","place",x?.place)+field("วันที่","date",x?.date,"date",true)+textarea("เรื่องราว","description",x?.description)+'<div class="field"><label>รูปภาพ JPG/PNG/WebP (สูงสุด 8 รูป)</label><input type="file" name="images" multiple accept="image/jpeg,image/png,image/webp"></div>'}
if(kind==="note"){html+=field("ชื่อโน้ต","title",x?.title,"text",true)+textarea("ข้อความ","body",x?.body)+'<div class="field"><label>ประเภท</label><select name="type">'+[["note","บันทึก"],["like","สิ่งที่ชอบ"],["wish","สิ่งที่อยากทำ"]].map(o=>'<option value="'+o[0]+'" '+(o[0]===x?.type?"selected":"")+'>'+o[1]+'</option>').join("")+'</select></div><label><input type="checkbox" name="private" '+(x?.private?"checked":"")+'>ส่วนตัว (เห็นได้เฉพาะฉัน)</label>'}
if(kind==="lesson"){html+=field("วิชา","subject",x?.subject,"text",true)+field("ห้องเรียน","place",x?.place)+'<div class="field"><label>วันเรียน</label><select name="day">'+days.map((d,i)=>'<option value="'+i+'" '+(i===x?.day?"selected":"")+'>'+d+'</option>').join("")+'</select></div>'+field("เวลาเริ่ม","start",x?.start,"time",true)+field("เวลาเลิก","end",x?.end,"time",true)}
html+='<div class="buttons"><button class="btn" type="submit">บันทึก ♡</button><a class="btn secondary" href="#'+collection+'">ยกเลิก</a></div></form>';
if(!isNew)html+='<button id="remove" class="danger">ลบรายการนี้</button>';html+='</div>';show(html);
document.getElementById("record").onsubmit=async e=>{e.preventDefault();const fd=new FormData(e.currentTarget);let data={};for(let [k,v]of fd)if(k!=="images")data[k]=v; if(kind==="note")data.private=fd.has("private");if(!isNew)data.revision=x.revision;try{if(kind==="memory"){for(let file of fd.getAll("images"))if(file.size>8*1024*1024)throw Error("ไฟล์รูปเกิน 8 MB");await api(collection+"/"+(isNew?"":id+"/"),{method:isNew?"POST":"PUT",body:fd,form:true})}else await api(collection+"/"+(isNew?"":id+"/"),{method:isNew?"POST":"PUT",body:data});await fetchAll();location.hash="#"+collection;await render()}catch(err){alert(err.message)}};
if(!isNew)document.getElementById("remove").onclick=async()=>{if(!confirm("ต้องการลบรายการนี้หรือไม่?"))return;try{await api(collection+"/"+id+"/",{method:"DELETE"});await fetchAll();location.hash="#"+collection;await render()}catch(err){alert(err.message)}}}
async function scanSubmit(e){e.preventDefault();try{let fd=new FormData(e.currentTarget),d=await api("scan/",{method:"POST",body:fd,form:true});let rows=d.rows||[];show('<div class="card formcard"><div class="eyebrow">AI SCHEDULE DRAFT</div><h1>ตรวจสอบผล AI</h1><p>หากข้อมูลไม่ตรง โปรดยกเลิกแล้วเพิ่มด้วยตัวเอง</p>'+rows.map(r=>'<div class="preview"><b>'+esc(r.subject)+'</b><div class="subtle">'+esc(days[r.day])+' · '+esc(r.start)+'–'+esc(r.end)+' · '+esc(r.place)+'</div></div>').join("")+'<div class="buttons">'+(rows.length?'<button id="confirm" class="btn">ยืนยันเพิ่ม '+rows.length+' วิชา</button>':"")+'<a href="#schedule" class="btn secondary">ยกเลิก</a></div></div>');if(rows.length)document.getElementById("confirm").onclick=async()=>{try{await api("scan/confirm/",{method:"POST",body:{rows}});await fetchAll();location.hash="#schedule";await render()}catch(err){alert(err.message)}}}catch(err){alert(err.message)}}
document.getElementById("theme").onclick=()=>{let dark=document.documentElement.dataset.theme!=="dark";document.documentElement.dataset.theme=dark?"dark":"light";localStorage.setItem("ourworld-theme",dark?"dark":"light")};
if(localStorage.getItem("ourworld-theme")==="dark")document.documentElement.dataset.theme="dark";
signout.onclick=async()=>{try{if(token)await api("logout/",{method:"POST"})}catch{}token="";sessionStorage.removeItem("ourworld_token");me=null;cache={};await render()};
window.addEventListener("hashchange",render);render();
