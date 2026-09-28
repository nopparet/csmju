-- ============================================================
--  Smart Reception Kiosk — ข้อมูลจากเว็บไซต์ csmju.com
--  สาขาวิชาวิทยาการคอมพิวเตอร์ คณะวิทยาศาสตร์ มหาวิทยาลัยแม่โจ้
--  อ้างอิง: https://www.csmju.com/
-- ============================================================
USE cs_kiosk;

-- ------------------------------------------------------------------
-- 1. ห้องต่างๆ
--    ข้อมูลจาก csmju.com/facilities:
--    "อาคารแม่โจ้ 60 ปี และอาคารจุฬาภรณ์ — สำนักงานชั้น 6 อาคาร 60 ปี"
--    ห้องแบ่งเป็น ห้องบรรยายคอมพิวเตอร์ และปฏิบัติการคอมพิวเตอร์
-- ------------------------------------------------------------------
INSERT INTO rooms (code, name, type, floor, pos_x, pos_y, hint) VALUES
-- อาคารแม่โจ้ 60 ปี (ชั้น 6) — ห้องบรรยาย
('CS-601',  'ห้องบรรยายคอมพิวเตอร์ 601',       'lecture', 6,  20,  20,  'อาคารแม่โจ้ 60 ปี ชั้น 6 ออกจากลิฟต์เลี้ยวซ้าย'),
('CS-602',  'ห้องบรรยายคอมพิวเตอร์ 602',       'lecture', 6, 170,  20,  'อาคารแม่โจ้ 60 ปี ชั้น 6 ถัดจาก CS-601'),
-- ห้องปฏิบัติการ
('LAB-1',   'ห้องปฏิบัติการคอมพิวเตอร์ 1',     'lab',     6, 320,  20,  'อาคารแม่โจ้ 60 ปี ชั้น 6 ป้ายสีน้ำเงิน'),
('LAB-2',   'ห้องปฏิบัติการคอมพิวเตอร์ 2',     'lab',     6, 470,  20,  'อาคารแม่โจ้ 60 ปี ชั้น 6 ถัดจาก LAB-1'),
-- สำนักงาน (ข้อมูลจากเว็บ: สำนักงานชั้น 6 อาคารแม่โจ้ 60 ปี)
('OFFICE',  'สำนักงานสาขาวิทยาการคอมพิวเตอร์', 'service', 6, 570,  20,  'ชั้น 6 อาคารแม่โจ้ 60 ปี เปิด 08:30-16:30 (พักเที่ยง 12:00-13:00) โทร 053-873800'),
-- ห้องประชุม
('MEET-1',  'ห้องประชุมสาขา',                   'meeting', 6, 320, 150,  'อาคารแม่โจ้ 60 ปี ชั้น 6 ตรงข้าม LAB-1'),
-- ห้องพักอาจารย์
('CS-601A', 'ห้องพักอาจารย์ 601A',              'office',  6,  20, 150,  'ชั้น 6 อาคาร 60 ปี ฝั่งบันได'),
('CS-601B', 'ห้องพักอาจารย์ 601B',              'office',  6, 145, 150,  'ชั้น 6 อาคาร 60 ปี ถัดจาก 601A'),
('CS-601C', 'ห้องพักอาจารย์ 601C',              'office',  6, 470, 150,  'ชั้น 6 อาคาร 60 ปี ฝั่งตรงข้าม LAB-2');

-- ------------------------------------------------------------------
-- 2. อาจารย์ประจำสาขา
--    ข้อมูลจาก https://www.csmju.com/personnels
-- ------------------------------------------------------------------
INSERT INTO teachers (name, email, phone, office_hours, room_id) VALUES
(
  'อ.ดร.กิตติกร หาญตระกูล',
  'kittikorn.h@mju.ac.th',
  '053-873800 ต่อ 6001',
  'จันทร์ 13:00-15:00, พุธ 13:00-15:00',
  (SELECT room_id FROM rooms WHERE code = 'CS-601A')
),
(
  'ผศ.ก่องกาญจน์ ดุลยไชย',
  'kongkarn.d@mju.ac.th',
  '053-873800 ต่อ 6002',
  'อังคาร 09:00-11:00, พฤหัสบดี 09:00-11:00',
  (SELECT room_id FROM rooms WHERE code = 'CS-601A')
),
(
  'ผศ.ดร.ปวีณ เขื่อนแก้ว',
  'paween.k@mju.ac.th',
  '053-873800 ต่อ 6003',
  'จันทร์ 09:00-11:00, พุธ 09:00-11:00',
  (SELECT room_id FROM rooms WHERE code = 'CS-601A')
),
(
  'อ.ดร.พยุงศักดิ์ เกษมสำราญ',
  'payungsak.k@mju.ac.th',
  '053-873800 ต่อ 6004',
  'อังคาร 13:00-15:00, ศุกร์ 13:00-15:00',
  (SELECT room_id FROM rooms WHERE code = 'CS-601B')
),
(
  'ผศ.ดร.พาสน์ ปราโมกข์ชน',
  'part.p@mju.ac.th',
  '053-873800 ต่อ 6005',
  'พุธ 13:00-15:00, ศุกร์ 09:00-11:00',
  (SELECT room_id FROM rooms WHERE code = 'CS-601B')
),
(
  'ผศ.ภานุวัฒน์ เมฆะ',
  'panuwat.m@mju.ac.th',
  '053-873800 ต่อ 6006',
  'จันทร์ 13:00-15:00, พฤหัสบดี 13:00-15:00',
  (SELECT room_id FROM rooms WHERE code = 'CS-601B')
),
(
  'ผศ.ดร.สนิท สิทธิ',
  'snit.s@mju.ac.th',
  '053-873800 ต่อ 6007',
  'อังคาร 09:00-11:00, พุธ 09:00-11:00',
  (SELECT room_id FROM rooms WHERE code = 'CS-601C')
),
(
  'ผศ.ดร.สมนึก สินธุปวน',
  'somnuek.s@mju.ac.th',
  '053-873800 ต่อ 6008',
  'จันทร์ 09:00-11:00, ศุกร์ 09:00-11:00',
  (SELECT room_id FROM rooms WHERE code = 'CS-601C')
),
(
  'อ.อรรถวิท ชังคมานนท์',
  'attawit.c@mju.ac.th',
  '053-873800 ต่อ 6009',
  'พุธ 13:00-15:00, พฤหัสบดี 13:00-15:00',
  (SELECT room_id FROM rooms WHERE code = 'CS-601C')
),
(
  'อ.อลงกต กองมณี',
  'alongkot.g@mju.ac.th',
  '053-873800 ต่อ 6010',
  'อังคาร 13:00-15:00, ศุกร์ 13:00-15:00',
  (SELECT room_id FROM rooms WHERE code = 'CS-601C')
);

-- ------------------------------------------------------------------
-- 3. รายวิชา
--    ข้อมูลจาก csmju.com/programs: หลักสูตร วท.บ. 2565 120 หน่วยกิต 4 ปี
--    โครงสร้างหมวดวิชา: วิทยาการคอมพิวเตอร์ / AI / เว็บ / IoT / Data Science
-- ------------------------------------------------------------------
INSERT INTO courses (code, name, credit, year_level) VALUES
-- ปี 1: พื้นฐาน
('CS101',  'การโปรแกรมคอมพิวเตอร์เบื้องต้น',       3, 1),
('CS102',  'คณิตศาสตร์สำหรับวิทยาการคอมพิวเตอร์',  3, 1),
('CS103',  'สถาปัตยกรรมคอมพิวเตอร์',               3, 1),
('CS104',  'การคิดเชิงคำนวณ',                       3, 1),
-- ปี 2: แกนวิชา
('CS201',  'โครงสร้างข้อมูลและอัลกอริทึม',          3, 2),
('CS202',  'การโปรแกรมเชิงวัตถุ',                   3, 2),
('CS203',  'ระบบฐานข้อมูล',                         3, 2),
('CS204',  'เครือข่ายคอมพิวเตอร์',                  3, 2),
('CS205',  'ระบบปฏิบัติการ',                        3, 2),
-- ปี 3: วิชาเฉพาะ (เว็บ/ซอฟต์แวร์, AI/Data, IoT)
('CS301',  'การพัฒนาเว็บและซอฟต์แวร์ Full-Stack',   3, 3),
('CS302',  'ปัญญาประดิษฐ์และการเรียนรู้ของเครื่อง', 3, 3),
('CS303',  'วิทยาการข้อมูล',                        3, 3),
('CS304',  'อินเทอร์เน็ตในทุกสิ่ง (IoT)',           3, 3),
('CS305',  'วิศวกรรมซอฟต์แวร์',                    3, 3),
('CS306',  'ความมั่นคงของระบบสารสนเทศ',             3, 3),
-- ปี 4: โครงงาน
('CS401',  'โครงงานด้านวิทยาการคอมพิวเตอร์ 1',     3, 4),
('CS402',  'โครงงานด้านวิทยาการคอมพิวเตอร์ 2',     3, 4),
('CS403',  'สหกิจศึกษาหรือฝึกงาน',                  6, 4);

-- ------------------------------------------------------------------
-- 4. ตารางเรียน-สอน ภาค 1/2568
-- ------------------------------------------------------------------
INSERT INTO schedules (course_id, teacher_id, room_id, weekday, start_time, end_time, term) VALUES
-- จันทร์
((SELECT course_id FROM courses WHERE code='CS101'),
 (SELECT teacher_id FROM teachers WHERE email='kittikorn.h@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='CS-601'), 'mon','08:00','11:00','1/2568'),

((SELECT course_id FROM courses WHERE code='CS201'),
 (SELECT teacher_id FROM teachers WHERE email='paween.k@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='CS-602'), 'mon','09:00','12:00','1/2568'),

((SELECT course_id FROM courses WHERE code='CS301'),
 (SELECT teacher_id FROM teachers WHERE email='somnuek.s@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='LAB-1'),  'mon','13:00','16:00','1/2568'),

-- อังคาร
((SELECT course_id FROM courses WHERE code='CS102'),
 (SELECT teacher_id FROM teachers WHERE email='kongkarn.d@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='CS-601'), 'tue','08:00','11:00','1/2568'),

((SELECT course_id FROM courses WHERE code='CS202'),
 (SELECT teacher_id FROM teachers WHERE email='attawit.c@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='LAB-2'),  'tue','09:00','12:00','1/2568'),

((SELECT course_id FROM courses WHERE code='CS302'),
 (SELECT teacher_id FROM teachers WHERE email='payungsak.k@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='LAB-1'),  'tue','13:00','16:00','1/2568'),

-- พุธ
((SELECT course_id FROM courses WHERE code='CS103'),
 (SELECT teacher_id FROM teachers WHERE email='snit.s@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='CS-601'), 'wed','08:00','11:00','1/2568'),

((SELECT course_id FROM courses WHERE code='CS204'),
 (SELECT teacher_id FROM teachers WHERE email='part.p@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='CS-602'), 'wed','09:00','12:00','1/2568'),

((SELECT course_id FROM courses WHERE code='CS303'),
 (SELECT teacher_id FROM teachers WHERE email='alongkot.g@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='LAB-2'),  'wed','13:00','16:00','1/2568'),

-- พฤหัสบดี
((SELECT course_id FROM courses WHERE code='CS203'),
 (SELECT teacher_id FROM teachers WHERE email='panuwat.m@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='CS-601'), 'thu','08:00','11:00','1/2568'),

((SELECT course_id FROM courses WHERE code='CS304'),
 (SELECT teacher_id FROM teachers WHERE email='kittikorn.h@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='LAB-1'),  'thu','13:00','16:00','1/2568'),

((SELECT course_id FROM courses WHERE code='CS401'),
 (SELECT teacher_id FROM teachers WHERE email='paween.k@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='MEET-1'), 'thu','13:00','16:00','1/2568'),

-- ศุกร์
((SELECT course_id FROM courses WHERE code='CS305'),
 (SELECT teacher_id FROM teachers WHERE email='somnuek.s@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='CS-602'), 'fri','08:00','11:00','1/2568'),

((SELECT course_id FROM courses WHERE code='CS402'),
 (SELECT teacher_id FROM teachers WHERE email='part.p@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='CS-602'), 'fri','09:00','12:00','1/2568'),

((SELECT course_id FROM courses WHERE code='CS306'),
 (SELECT teacher_id FROM teachers WHERE email='payungsak.k@mju.ac.th'),
 (SELECT room_id FROM rooms WHERE code='LAB-2'),  'fri','13:00','16:00','1/2568');

-- ------------------------------------------------------------------
-- 5. นักศึกษาตัวอย่าง
-- ------------------------------------------------------------------
INSERT INTO students (student_id, name, year_level, program, card_uid) VALUES
('6706101301', 'สุภาพร ใจดี',        2, 'วิทยาการคอมพิวเตอร์', 'CARD-MJU01'),
('6706101302', 'ธนกร พงศ์ไพร',       2, 'วิทยาการคอมพิวเตอร์', 'CARD-MJU02'),
('6706101303', 'อาทิตยา สุขสวัสดิ์', 2, 'วิทยาการคอมพิวเตอร์', 'CARD-MJU03'),
('6606101201', 'ปิยะ มานะกิจ',       3, 'วิทยาการคอมพิวเตอร์', 'CARD-MJU04'),
('6606101202', 'นภัสสร วงศ์สุวรรณ',  3, 'วิทยาการคอมพิวเตอร์', 'CARD-MJU05');

-- ------------------------------------------------------------------
-- 6. ลงทะเบียนเรียน
-- ------------------------------------------------------------------
INSERT INTO enrollments (course_id, student_id) VALUES
((SELECT course_id FROM courses WHERE code='CS201'), '6706101301'),
((SELECT course_id FROM courses WHERE code='CS201'), '6706101302'),
((SELECT course_id FROM courses WHERE code='CS202'), '6706101301'),
((SELECT course_id FROM courses WHERE code='CS202'), '6706101303'),
((SELECT course_id FROM courses WHERE code='CS203'), '6706101302'),
((SELECT course_id FROM courses WHERE code='CS301'), '6606101201'),
((SELECT course_id FROM courses WHERE code='CS301'), '6606101202'),
((SELECT course_id FROM courses WHERE code='CS302'), '6606101201'),
((SELECT course_id FROM courses WHERE code='CS303'), '6606101202');

-- ------------------------------------------------------------------
-- 7. กิจกรรม
--    (ปรับตามปฏิทินจริงได้ที่ csmju.com/newsroom)
-- ------------------------------------------------------------------
INSERT INTO activities (title, detail, start_at, end_at, location, is_checkin_open) VALUES
(
  'Open House CSMJU 2568',
  'งานเปิดบ้านแนะนำหลักสูตรและแสดงผลงานนักศึกษา ชมได้ฟรี สนใจสมัครเรียนดูข้อมูลที่ csmju.com',
  DATE_ADD(NOW(), INTERVAL 14 DAY),
  DATE_ADD(NOW(), INTERVAL 14 DAY) + INTERVAL 8 HOUR,
  'ชั้น 6 อาคารแม่โจ้ 60 ปี คณะวิทยาศาสตร์ มหาวิทยาลัยแม่โจ้',
  0
),
(
  'อบรม Git & GitHub เบื้องต้น',
  'Workshop การใช้ Version Control สำหรับนักศึกษาใหม่ รับ 40 คน สมัครที่สำนักงานสาขา',
  DATE_ADD(NOW(), INTERVAL 7 DAY),
  DATE_ADD(NOW(), INTERVAL 7 DAY) + INTERVAL 3 HOUR,
  'LAB-1 ชั้น 6 อาคารแม่โจ้ 60 ปี',
  0
),
(
  'สัมมนา AI & Data Science ยุคใหม่',
  'บรรยายพิเศษโดยวิทยากรจากภาคอุตสาหกรรม ไม่มีค่าใช้จ่าย ลงทะเบียนที่ csmju.com',
  DATE_ADD(NOW(), INTERVAL 21 DAY),
  DATE_ADD(NOW(), INTERVAL 21 DAY) + INTERVAL 4 HOUR,
  'ห้อง CS-601 ชั้น 6 อาคาร 60 ปี',
  0
);

-- ------------------------------------------------------------------
-- 8. Chat Intents — อ้างอิงข้อมูลจาก csmju.com
-- ------------------------------------------------------------------
INSERT INTO chat_intents (intent_name, keywords, answer_template, priority) VALUES
-- intent ดึงข้อมูลจาก DB
('room_status',
 'ว่าง,สถานะห้อง,ใช้ห้อง,ห้องไหนว่าง,ห้องนี้ว่าง,ห้องเรียนว่าง',
 NULL, 8),

('teacher_room',
 'อาจารย์,อาจารย์อยู่ที่ไหน,ห้องพักอาจารย์,ติดต่ออาจารย์,office hour,เวลาให้คำปรึกษา,กิตติกร,ก่องกาญจน์,ปวีณ,พยุงศักดิ์,พาสน์,ภานุวัฒน์,สนิท,สมนึก,อรรถวิท,อลงกต',
 NULL, 9),

('schedule',
 'ตาราง,ตารางเรียน,ตารางสอน,เรียนอะไร,สอนอะไร,คาบ,วันนี้เรียน,พรุ่งนี้เรียน',
 NULL, 7),

('activity',
 'กิจกรรม,ข่าว,อบรม,สัมมนา,open house,เปิดบ้าน,งาน,ปฏิทิน,newsroom',
 NULL, 6),

-- intent ตอบด้วยข้อความ (อ้างอิงจาก csmju.com)
('checkin',
 'เช็คชื่อ,สแกน,qr,บัตรนักศึกษา,เข้าเรียน',
 'เช็คชื่อได้ที่เมนู "เช็คชื่อเข้าเรียน" โดยสแกน QR บนหน้าจอด้วยมือถือ หรือยื่นบัตรนักศึกษาที่เครื่องอ่าน ระบบเปิดรับ 15 นาทีก่อนถึง 30 นาทีหลังเริ่มคาบ', 5),

('contact',
 'ติดต่อ,สำนักงาน,ธุรการ,เอกสาร,เบอร์โทร,โทรศัพท์,อีเมล,email,cs@mju',
 'สำนักงานสาขาวิทยาการคอมพิวเตอร์ ชั้น 6 อาคารแม่โจ้ 60 ปี คณะวิทยาศาสตร์ มหาวิทยาลัยแม่โจ้\nเปิด 08:30-16:30 (พักเที่ยง 12:00-13:00)\nโทร. 053-873800\nเว็บไซต์: csmju.com', 6),

('website',
 'เว็บไซต์,เว็บ,website,csmju,ออนไลน์,ลิงก์',
 'เว็บไซต์สาขา: csmju.com\nFacebook: facebook.com/computersciencemju\nYouTube: youtube.com/@comscimaejo\nTikTok: tiktok.com/@cs_mju\nระบบทะเบียน: reg.mju.ac.th', 5),

('wifi',
 'wifi,ไวไฟ,อินเทอร์เน็ต,รหัสเน็ต,เน็ต,wireless,internet',
 'WiFi มหาวิทยาลัยแม่โจ้:\n- นักศึกษา: SSID "MJU-Student" (login ด้วยรหัสนักศึกษา)\n- eduroam สำหรับบุคลากร\nรหัสผ่านและการตั้งค่าขอได้ที่สำนักงานสาขา', 5),

('exam',
 'สอบ,กลางภาค,ปลายภาค,ตารางสอบ,ข้อสอบ',
 'ตารางสอบประกาศที่บอร์ดหน้าสำนักงานและที่ระบบทะเบียน reg.mju.ac.th\nดูตารางเรียนได้ในเมนู "ตารางเรียน-สอน"', 5),

('scholarship',
 'ทุน,ทุนการศึกษา,ทุนสนับสนุน,เงินทุน,กยศ,กู้ยืม',
 'ข้อมูลทุนการศึกษาและกองทุน กยศ. ดูได้ที่:\n- csmju.com หัวข้อ "บริการนักศึกษา"\n- กองพัฒนานักศึกษา มหาวิทยาลัยแม่โจ้\n- LINE Official: @csmju', 4),

('admission',
 'สมัคร,สมัครเรียน,รับสมัคร,tcas,dek,รับตรง,เกณฑ์,จำนวนรับ,admissions',
 'รายละเอียดการรับสมัครนักศึกษาใหม่:\n- เว็บไซต์: admissions.mju.ac.th\n- ข้อมูลหลักสูตร: csmju.com/programs\n- หลักสูตร วท.บ. วิทยาการคอมพิวเตอร์ 120 หน่วยกิต 4 ปี\nสอบถามสำนักงานสาขา โทร. 053-873800', 4),

('location',
 'อยู่ที่ไหน,ทางไป,เดินทาง,แผนที่,ตั้งอยู่,ที่อยู่,อาคาร,60ปี,จุฬาภรณ์',
 'สาขาวิชาวิทยาการคอมพิวเตอร์ คณะวิทยาศาสตร์ มหาวิทยาลัยแม่โจ้\nสำนักงาน: ชั้น 6 อาคารแม่โจ้ 60 ปี\nห้องเรียน: อาคารแม่โจ้ 60 ปี และอาคารจุฬาภรณ์\n63 ม.4 ต.หนองหาร อ.สันทราย จ.เชียงใหม่ 50290\nGoogle Maps: maps.app.goo.gl/y2Xn7d3w5zV2bKj59', 4),

('program',
 'หลักสูตร,วิชา,เรียนอะไรบ้าง,สาขา,ปริญญา,วทบ,วิทยาศาสตร์บัณฑิต',
 'หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาวิทยาการคอมพิวเตอร์\n- ระยะเวลา 4 ปี | 120 หน่วยกิต\n- วุฒิ: วท.บ. (วิทยาการคอมพิวเตอร์)\n- เน้น: เว็บ/ซอฟต์แวร์, AI/Data Science, IoT\nรายละเอียด: csmju.com/programs', 4);
