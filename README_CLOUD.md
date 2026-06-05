# คู่มือการติดตั้ง JadVen.ai บนระบบคลาวด์ (ฟรี 100%)
คู่มือนี้จะอธิบายขั้นตอนการย้ายระบบ JadVen.ai จากเครื่อง Local ไปยังระบบ Cloud โดยใช้ **Supabase (Database)**, **Render (Backend)** และ **Vercel (Frontend)**

---

## 🛠️ ขั้นตอนที่ 1: ตั้งค่าฐานข้อมูลบน Supabase
1. สมัครใช้งาน [Supabase](https://supabase.com)
2. สร้างโปรเจกต์ใหม่ (เช่น `JadVen-DB`) ตั้งรหัสผ่านของฐานข้อมูล และเลือก Region ใกล้เคียง (แนะนำ Singapore)
3. เมื่อสร้างเสร็จแล้ว ไปที่เมนู **Project Settings -> Database** (รูปฟันเฟืองด้านล่างซ้าย)
4. เลื่อนลงมาที่หัวข้อ **Connection string** -> เลือกแท็บ **URI**
5. คัดลอกลิงก์เก็บไว้ (เช่น `postgresql://postgres.xxxx:[รหัสผ่าน]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres`)
   * *อย่าลืมแทนที่ `[รหัสผ่าน]` ด้วยรหัสผ่านจริงที่คุณตั้งไว้ตอนสร้างโปรเจกต์*

### 📥 การนำเข้าตารางและข้อมูลตั้งต้น (Seeding)
รันคำสั่งนี้ใน **VS Code Terminal (PowerShell)** บนเครื่องของคุณ เพื่อสร้างตารางและข้อมูลผู้ใช้เริ่มต้นเข้าสู่ระบบ Supabase โดยตรง:
```powershell
cd d:\Project_DEV\JadVen.ai\backend
$env:DATABASE_URL="ลิงก์_Connection_string_ที่คัดลอกมาจาก_Supabase"
python seed_db.py
```
*(ระบบจะสร้างตารางและบัญชีผู้ใช้ตั้งต้นให้ทันทีใน Supabase)*

---

## 🚀 ขั้นตอนที่ 2: ตั้งค่า API Backend บน Render.com
1. สมัครใช้งาน [Render](https://render.com)
2. กดปุ่ม **New + -> Web Service**
3. เชื่อมต่อบัญชี GitHub ของคุณ และเลือก Repository โค้ดของ **JadVen.ai**
4. ตั้งค่าบริการดังนี้:
   * **Name**: `jadven-backend`
   * **Region**: สิงคโปร์ (หรือตามสะดวก)
   * **Language**: `Docker` (เนื่องจากในโปรเจกต์มี Dockerfile เรียบร้อยแล้ว)
   * **Root Directory**: `backend` (ระบุเพื่อให้ดึงเฉพาะโค้ดหลังบ้านไปรัน)
5. เลื่อนลงไปที่ **Environment Variables** (หรือกดปุ่ม Advanced) แล้วเพิ่มตัวแปรดังนี้:
   * `DATABASE_URL` = (วางลิงก์ Connection string ของ Supabase ที่ระบุในขั้นตอนที่ 1)
   * `CORS_ORIGINS` = `*` (หรือวางลิงก์เว็บ Frontend จาก Vercel เมื่อ Deploy เสร็จแล้วเพื่อความปลอดภัยสูงสุด)
6. กด **Create Web Service** และรอระบบทำการ Build เสร็จสิ้น คุณจะได้ลิงก์ภายนอก เช่น `https://jadven-backend.onrender.com`

---

## 💻 ขั้นตอนที่ 3: ตั้งค่า Frontend บน Vercel.com
1. สมัครใช้งาน [Vercel](https://vercel.com)
2. กดปุ่ม **Add New -> Project**
3. เลือก Repository เดียวกันกับขั้นตอนก่อนหน้า
4. ตั้งค่าหน้า Deploy ดังนี้:
   * **Root Directory**: เลือกโฟลเดอร์ `frontend`
   * **Framework Preset**: ระบบจะเลือก `Next.js` ให้อัตโนมัติ
5. เลื่อนลงมาที่ **Environment Variables** เพิ่มตัวแปรนี้:
   * `NEXT_PUBLIC_API_URL` = (วางลิงก์ backend ที่ได้จาก Render.com เช่น `https://jadven-backend.onrender.com`)
6. กดปุ่ม **Deploy**

---

### 🎉 พร้อมใช้งาน!
เมื่อหน้าจอ Vercel แสดงผลสำเร็จ คุณจะได้ URL สาธารณะของระบบเวรพยาบาล (เช่น `https://jadven-frontend.vercel.app`) ซึ่งสามารถส่งให้เพื่อนๆ หรือโรงพยาบาลอื่นๆ นำไปทดลองใช้งานร่วมกันได้ทันทีครับ!
