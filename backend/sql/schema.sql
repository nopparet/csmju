-- Smart Reception Kiosk — โครงสร้างฐานข้อมูล
-- ใช้: mysql -u root -p < schema.sql
CREATE DATABASE IF NOT EXISTS cs_kiosk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cs_kiosk;

CREATE TABLE IF NOT EXISTS rooms (
  room_id INT AUTO_INCREMENT PRIMARY KEY,
  code    VARCHAR(20) NOT NULL UNIQUE,
  name    VARCHAR(100),
  type    ENUM('lecture','lab','office','meeting','service') DEFAULT 'lecture',
  floor   SMALLINT DEFAULT 1,
  pos_x   SMALLINT DEFAULT 0,
  pos_y   SMALLINT DEFAULT 0,
  hint    VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS teachers (
  teacher_id   INT AUTO_INCREMENT PRIMARY KEY,
  name         VARCHAR(100) NOT NULL,
  email        VARCHAR(120),
  phone        VARCHAR(30),
  office_hours VARCHAR(120),
  room_id      INT,
  FOREIGN KEY (room_id) REFERENCES rooms(room_id)
);

CREATE TABLE IF NOT EXISTS students (
  student_id VARCHAR(15) PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,
  year_level SMALLINT,
  program    VARCHAR(80),
  card_uid   VARCHAR(50) UNIQUE
);

CREATE TABLE IF NOT EXISTS courses (
  course_id  INT AUTO_INCREMENT PRIMARY KEY,
  code       VARCHAR(20) NOT NULL UNIQUE,
  name       VARCHAR(150) NOT NULL,
  credit     SMALLINT DEFAULT 3,
  year_level SMALLINT
);

CREATE TABLE IF NOT EXISTS schedules (
  schedule_id INT AUTO_INCREMENT PRIMARY KEY,
  course_id   INT NOT NULL,
  teacher_id  INT,
  room_id     INT,
  weekday     ENUM('mon','tue','wed','thu','fri','sat','sun') NOT NULL,
  start_time  TIME NOT NULL,
  end_time    TIME NOT NULL,
  term        VARCHAR(10) DEFAULT '1/2568',
  FOREIGN KEY (course_id)  REFERENCES courses(course_id),
  FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
  FOREIGN KEY (room_id)    REFERENCES rooms(room_id),
  INDEX idx_day (weekday, start_time)
);

CREATE TABLE IF NOT EXISTS class_sessions (
  session_id   INT AUTO_INCREMENT PRIMARY KEY,
  schedule_id  INT NOT NULL,
  session_date DATE NOT NULL,
  start_time   TIME NOT NULL,
  end_time     TIME NOT NULL,
  status       ENUM('open','closed','cancelled') DEFAULT 'open',
  UNIQUE KEY uq_sched_date (schedule_id, session_date),
  FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id)
);

CREATE TABLE IF NOT EXISTS enrollments (
  enroll_id  INT AUTO_INCREMENT PRIMARY KEY,
  course_id  INT NOT NULL,
  student_id VARCHAR(15) NOT NULL,
  UNIQUE KEY uq_enroll (course_id, student_id),
  FOREIGN KEY (course_id)  REFERENCES courses(course_id),
  FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE IF NOT EXISTS activities (
  activity_id     INT AUTO_INCREMENT PRIMARY KEY,
  title           VARCHAR(150) NOT NULL,
  detail          TEXT,
  start_at        DATETIME NOT NULL,
  end_at          DATETIME,
  location        VARCHAR(100),
  is_checkin_open TINYINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS attendance (
  att_id     INT AUTO_INCREMENT PRIMARY KEY,
  ref_type   ENUM('class','activity') NOT NULL,
  ref_id     INT NOT NULL,
  student_id VARCHAR(15) NOT NULL,
  checked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  method     ENUM('qr','card','manual') DEFAULT 'qr',
  result     ENUM('present','late','denied') DEFAULT 'present',
  UNIQUE KEY uq_once (ref_type, ref_id, student_id),
  FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE IF NOT EXISTS visit_logs (
  log_id       INT AUTO_INCREMENT PRIMARY KEY,
  user_type    ENUM('student','teacher','visitor') NOT NULL,
  module       VARCHAR(40),
  started_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  duration_sec INT DEFAULT 0,
  INDEX idx_started (started_at)
);

CREATE TABLE IF NOT EXISTS chat_intents (
  intent_id       INT AUTO_INCREMENT PRIMARY KEY,
  intent_name     VARCHAR(50) NOT NULL UNIQUE,
  keywords        TEXT NOT NULL,
  answer_template TEXT,
  priority        SMALLINT DEFAULT 5,
  is_active       TINYINT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS chat_logs (
  chat_id     INT AUTO_INCREMENT PRIMARY KEY,
  question    TEXT NOT NULL,
  intent_name VARCHAR(50),
  score       FLOAT DEFAULT 0,
  answered    TINYINT DEFAULT 1,
  asked_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_asked (asked_at)
);
