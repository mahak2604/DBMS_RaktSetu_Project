-- ============================================================
--  RaktSetu — Blood Bridge Management System
--  DBMS Mini Project | NMIMS MPSTME 2025-26
--  Compatible with MySQL 5.7 and above
-- ============================================================

CREATE DATABASE IF NOT EXISTS raktsetu;
USE raktsetu;

-- Drop in reverse FK order so re-imports are clean
DROP TABLE IF EXISTS blood_requests;
DROP TABLE IF EXISTS blood_inventory;
DROP TABLE IF EXISTS hospitals;
DROP TABLE IF EXISTS donors;

-- ============================================================
--  TABLE CREATION
-- ============================================================

CREATE TABLE donors (
    donor_id     VARCHAR(10)  PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    age          INT,
    blood_group  VARCHAR(5)   NOT NULL,
    phone        VARCHAR(15),
    city         VARCHAR(50),
    last_donated DATE,
    CONSTRAINT chk_age CHECK (age BETWEEN 18 AND 65)
);

CREATE TABLE hospitals (
    hospital_id  VARCHAR(10)  PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    city         VARCHAR(50),
    contact      VARCHAR(15)
);

CREATE TABLE blood_inventory (
    inv_id        VARCHAR(10)  PRIMARY KEY,
    blood_group   VARCHAR(5)   NOT NULL,
    units         INT          NOT NULL DEFAULT 0,
    expiry_date   DATE,
    received_date DATE,
    donor_id      VARCHAR(10),
    CONSTRAINT fk_inv_donor FOREIGN KEY (donor_id)
        REFERENCES donors(donor_id) ON DELETE SET NULL
);

CREATE TABLE blood_requests (
    req_id       VARCHAR(10)  PRIMARY KEY,
    hospital_id  VARCHAR(10),
    patient      VARCHAR(100) NOT NULL,
    blood_group  VARCHAR(5)   NOT NULL,
    units        INT          NOT NULL DEFAULT 1,
    priority     ENUM('CRITICAL','HIGH','NORMAL') DEFAULT 'NORMAL',
    status       ENUM('PENDING','APPROVED','FULFILLED') DEFAULT 'PENDING',
    contact      VARCHAR(15),
    request_date DATE,
    CONSTRAINT fk_req_hospital FOREIGN KEY (hospital_id)
        REFERENCES hospitals(hospital_id) ON DELETE SET NULL
);

-- ============================================================
--  INDEXES
-- ============================================================

CREATE INDEX idx_donor_bg   ON donors(blood_group);
CREATE INDEX idx_inv_bg     ON blood_inventory(blood_group);
CREATE INDEX idx_req_status ON blood_requests(status);

-- ============================================================
--  SEED DATA — DONORS (20 rows)
-- ============================================================

INSERT INTO donors VALUES
('D001','Arjun Sharma',    28,'O+', '9876543210','Pune',       '2024-11-10'),
('D002','Priya Patil',     24,'A+', '9123456789','Mumbai',     '2024-12-01'),
('D003','Ravi Kumar',      35,'B+', '9988776655','Nashik',     '2024-10-20'),
('D004','Sneha Joshi',     22,'AB+','9011223344','Pune',       '2025-01-05'),
('D005','Aditya Rane',     30,'O-', '9555666777','Aurangabad', '2024-09-15'),
('D006','Kavita Desai',    26,'A-', '9444333222','Mumbai',     '2025-02-12'),
('D007','Rohit Nair',      32,'B-', '9333111000','Thane',      '2025-01-20'),
('D008','Anjali Mehta',    29,'AB-','9222444555','Pune',       '2024-12-18'),
('D009','Suresh Bhat',     45,'O+', '9111222333','Nagpur',     '2025-03-01'),
('D010','Pooja Yadav',     27,'A+', '9000111222','Mumbai',     '2025-03-10'),
('D011','Manish Gupta',    38,'B+', '9777888999','Nashik',     '2024-11-25'),
('D012','Deepa Iyer',      23,'O-', '9666777888','Pune',       '2025-02-28'),
('D013','Rahul Verma',     31,'O+', '9811122233','Delhi',      '2025-03-15'),
('D014','Neha Kapoor',     26,'A+', '9822233344','Mumbai',     '2025-03-18'),
('D015','Amit Kulkarni',   34,'B+', '9833344455','Pune',       '2025-03-20'),
('D016','Simran Kaur',     25,'AB+','9844455566','Delhi',      '2025-03-22'),
('D017','Vikas Singh',     29,'O-', '9855566677','Lucknow',    '2025-03-25'),
('D018','Meera Nair',      33,'A-', '9866677788','Kochi',      '2025-03-28'),
('D019','Karan Malhotra',  36,'B-', '9877788899','Delhi',      '2025-04-01'),
('D020','Ritu Sharma',     27,'AB-','9888899900','Chandigarh', '2025-04-03');

-- ============================================================
--  SEED DATA — HOSPITALS (10 rows)
-- ============================================================

INSERT INTO hospitals VALUES
('H001','Ruby Hall Clinic',     'Pune',   '020-66455000'),
('H002','KEM Hospital',         'Mumbai', '022-24107000'),
('H003','Sassoon Hospital',     'Pune',   '020-26128000'),
('H004','Jehangir Hospital',    'Pune',   '020-66455100'),
('H005','Lilavati Hospital',    'Mumbai', '022-26751000'),
('H006','Wockhardt Hospital',   'Mumbai', '022-66214444'),
('H007','AIIMS Nagpur',         'Nagpur', '0712-2802000'),
('H008','Deenanath Mangeshkar', 'Pune',   '020-66020000'),
('H009','Global Hospital',      'Mumbai', '022-67670101'),
('H010','Fortis Hospital',      'Thane',  '022-41255555');

-- ============================================================
--  SEED DATA — BLOOD INVENTORY (20 rows)
-- ============================================================

INSERT INTO blood_inventory VALUES
('I001','O+', 180,'2026-05-01','2025-01-10','D001'),
('I002','A+', 220,'2026-05-15','2025-01-15','D002'),
('I003','B+', 160,'2026-04-28','2025-01-20','D003'),
('I004','AB+', 90,'2026-06-01','2025-01-25','D004'),
('I005','O-',  75,'2026-05-20','2025-02-01','D005'),
('I006','A-', 110,'2026-05-10','2025-02-05','D006'),
('I007','B-',  45,'2026-04-25','2025-02-10','D007'),
('I008','AB-', 30,'2026-06-10','2025-02-15','D008'),
('I009','O+',  60,'2026-05-30','2025-03-01','D009'),
('I010','A+',  80,'2026-06-20','2025-03-05','D010'),
('I011','B+',  50,'2026-06-15','2025-03-08','D011'),
('I012','O-',  40,'2026-05-25','2025-03-12','D012'),
('I013','O+', 100,'2026-06-01','2025-03-15','D013'),
('I014','A+', 120,'2026-06-05','2025-03-18','D014'),
('I015','B+',  90,'2026-06-08','2025-03-20','D015'),
('I016','AB+', 60,'2026-06-10','2025-03-22','D016'),
('I017','O-',  70,'2026-06-12','2025-03-25','D017'),
('I018','A-',  85,'2026-06-15','2025-03-28','D018'),
('I019','B-',  55,'2026-06-18','2025-04-01','D019'),
('I020','AB-', 40,'2026-06-20','2025-04-03','D020');

-- ============================================================
--  SEED DATA — BLOOD REQUESTS (18 rows)
-- ============================================================

INSERT INTO blood_requests VALUES
('R001','H001','Mohan Das',    'O+', 2,'CRITICAL','PENDING',   '9876500001','2025-04-01'),
('R002','H002','Sunita Rao',   'A+', 3,'HIGH',    'APPROVED',  '9876500002','2025-04-02'),
('R003','H003','Vijay Mehta',  'B+', 1,'NORMAL',  'FULFILLED', '9876500003','2025-04-03'),
('R004','H004','Anita Singh',  'O-', 4,'CRITICAL','PENDING',   '9876500004','2025-04-04'),
('R005','H005','Raj Bhat',     'AB+',2,'HIGH',    'PENDING',   '9876500005','2025-04-05'),
('R006','H006','Neha Kulkarni','A-', 1,'NORMAL',  'APPROVED',  '9876500006','2025-04-06'),
('R007','H007','Anil Tiwari',  'B-', 3,'CRITICAL','PENDING',   '9876500007','2025-04-07'),
('R008','H008','Rekha Soni',   'AB-',2,'HIGH',    'FULFILLED', '9876500008','2025-04-08'),
('R009','H001','Sanjay Dubey', 'O+', 5,'CRITICAL','PENDING',   '9876500009','2025-04-09'),
('R010','H002','Meera Shah',   'A+', 1,'NORMAL',  'PENDING',   '9876500010','2025-04-10'),
('R011','H003','Rakesh Jain',  'O+', 2,'HIGH',    'PENDING',   '9876500011','2025-04-11'),
('R012','H004','Pallavi Desai','A+', 1,'NORMAL',  'APPROVED',  '9876500012','2025-04-12'),
('R013','H005','Farhan Ali',   'B+', 3,'CRITICAL','PENDING',   '9876500013','2025-04-13'),
('R014','H006','Jyoti Mishra', 'AB+',1,'HIGH',    'FULFILLED', '9876500014','2025-04-14'),
('R015','H007','Harish Pillai','O-', 4,'CRITICAL','PENDING',   '9876500015','2025-04-15'),
('R016','H008','Snehal Patil', 'A-', 2,'HIGH',    'APPROVED',  '9876500016','2025-04-16'),
('R017','H009','Imran Sheikh', 'B-', 1,'NORMAL',  'PENDING',   '9876500017','2025-04-17'),
('R018','H010','Kiran More',   'AB-',2,'CRITICAL','PENDING',   '9876500018','2025-04-18');

-- ============================================================
--  SQL QUERIES (22) — Section VI of DBMS Report
-- ============================================================

-- Q1: All donors
SELECT * FROM donors;

-- Q2: All blood inventory
SELECT * FROM blood_inventory;

-- Q3: All hospitals
SELECT * FROM hospitals;

-- Q4: All pending blood requests
SELECT * FROM blood_requests WHERE status = 'PENDING';

-- Q5: O+ donors (WHERE filter)
SELECT name, phone, city FROM donors WHERE blood_group = 'O+';

-- Q6: Total units per blood group (GROUP BY + SUM)
SELECT blood_group, SUM(units) AS total_units
FROM blood_inventory
GROUP BY blood_group
ORDER BY total_units DESC;

-- Q7: Donor count per blood group (GROUP BY + COUNT)
SELECT blood_group, COUNT(*) AS donor_count
FROM donors
GROUP BY blood_group
ORDER BY donor_count DESC;

-- Q8: Average donor age per blood group (AVG)
SELECT blood_group, ROUND(AVG(age), 1) AS avg_age
FROM donors
GROUP BY blood_group;

-- Q9: Donor details with inventory (INNER JOIN)
SELECT d.name, d.blood_group, bi.units, bi.expiry_date
FROM donors d
JOIN blood_inventory bi ON d.donor_id = bi.donor_id;

-- Q10: Request details with hospital name (JOIN)
SELECT br.req_id, h.name AS hospital, br.patient,
       br.blood_group, br.units, br.priority, br.status
FROM blood_requests br
JOIN hospitals h ON br.hospital_id = h.hospital_id;

-- Q11: Critical pending requests with hospital (JOIN + WHERE)
SELECT br.req_id, h.name AS hospital, br.patient, br.blood_group, br.units
FROM blood_requests br
JOIN hospitals h ON br.hospital_id = h.hospital_id
WHERE br.priority = 'CRITICAL' AND br.status = 'PENDING';

-- Q12: Blood groups with stock below 100 units (HAVING)
SELECT blood_group, SUM(units) AS total
FROM blood_inventory
GROUP BY blood_group
HAVING total < 100;

-- Q13: Donors who donated in the last 6 months
SELECT name, blood_group, last_donated
FROM donors
WHERE last_donated >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH);

-- Q14: Inventory expiring within 30 days
SELECT inv_id, blood_group, units, expiry_date
FROM blood_inventory
WHERE expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY);

-- Q15: Total units requested per blood group
SELECT blood_group, SUM(units) AS units_requested
FROM blood_requests
GROUP BY blood_group
ORDER BY units_requested DESC;

-- Q16: Hospitals with more than 1 request (HAVING)
SELECT hospital_id, COUNT(*) AS total_requests
FROM blood_requests
GROUP BY hospital_id
HAVING total_requests > 1;

-- Q17: Donors from Pune
SELECT name, age, blood_group, phone
FROM donors
WHERE city = 'Pune';

-- Q18: UPDATE — approve a pending request
UPDATE blood_requests
SET status = 'APPROVED'
WHERE req_id = 'R001';

-- Q19: UPDATE — dispense 1 unit from inventory
UPDATE blood_inventory
SET units = units - 1
WHERE inv_id = 'I001' AND units > 0;

-- Q20: Fulfilled requests with hospital info (3-table JOIN)
SELECT br.req_id, h.name AS hospital, br.patient,
       br.blood_group, br.units, br.request_date
FROM blood_requests br
JOIN hospitals h ON br.hospital_id = h.hospital_id
WHERE br.status = 'FULFILLED';

-- Q21: Inventory with donor city (LEFT JOIN)
SELECT bi.blood_group, bi.units, d.name AS donor_name, d.city
FROM blood_inventory bi
LEFT JOIN donors d ON bi.donor_id = d.donor_id
ORDER BY bi.blood_group;

-- Q22: Inventory units above average (subquery)
SELECT inv_id, blood_group, units
FROM blood_inventory
WHERE units > (SELECT AVG(units) FROM blood_inventory);