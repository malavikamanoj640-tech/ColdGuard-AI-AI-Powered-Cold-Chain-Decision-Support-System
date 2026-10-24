import json, hashlib
from datetime import datetime
import pymysql
from pymysql.cursors import DictCursor
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

SCHEMA_STATEMENTS = [
"""CREATE TABLE IF NOT EXISTS shipments(id INT AUTO_INCREMENT PRIMARY KEY,batch_id VARCHAR(100) UNIQUE NOT NULL,product VARCHAR(255) DEFAULT 'Temperature-sensitive goods',origin VARCHAR(255),destination VARCHAR(255),location VARCHAR(255),logistics_stage VARCHAR(100),transport_mode VARCHAR(100),thermal_temp DOUBLE,room_temperature DOUBLE,humidity DOUBLE,expiry_hours DOUBLE,oob_hours DOUBLE DEFAULT 0,freezer_hours DOUBLE DEFAULT 0,refrigeration_hours DOUBLE DEFAULT 0,delay_hours DOUBLE DEFAULT 0,risk_probability DOUBLE,risk_level VARCHAR(30),quality_risk DOUBLE,delay_risk DOUBLE,environment_risk DOUBLE,operational_risk DOUBLE,predicted_outcome VARCHAR(255),created_at VARCHAR(40),updated_at VARCHAR(40)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS telemetry(id INT AUTO_INCREMENT PRIMARY KEY,batch_id VARCHAR(100),temperature DOUBLE,room_temperature DOUBLE,humidity DOUBLE,expiry_hours DOUBLE,oob_hours DOUBLE,risk_probability DOUBLE,risk_level VARCHAR(30),recorded_at VARCHAR(40),INDEX(batch_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS alerts(id INT AUTO_INCREMENT PRIMARY KEY,batch_id VARCHAR(100),severity VARCHAR(30),title VARCHAR(255),message TEXT,acknowledged TINYINT DEFAULT 0,status VARCHAR(40) DEFAULT 'OPEN',assigned_to VARCHAR(255),resolved_at VARCHAR(40),created_at VARCHAR(40),INDEX(batch_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS simulations(id INT AUTO_INCREMENT PRIMARY KEY,batch_id VARCHAR(100),baseline_risk DOUBLE,simulated_risk DOUBLE,inputs LONGTEXT,created_at VARCHAR(40)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS audit_log(id INT AUTO_INCREMENT PRIMARY KEY,event_type VARCHAR(100),batch_id VARCHAR(100),payload LONGTEXT,previous_hash VARCHAR(64),event_hash VARCHAR(64),created_at VARCHAR(40)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS product_passports(batch_id VARCHAR(100) PRIMARY KEY,passport_json LONGTEXT,created_at VARCHAR(40),updated_at VARCHAR(40)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS cv_inspections(id INT AUTO_INCREMENT PRIMARY KEY,batch_id VARCHAR(100),result_json LONGTEXT,created_at VARCHAR(40)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS scenario_runs(id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255),result_json LONGTEXT,created_at VARCHAR(40)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS inventory(product VARCHAR(255) PRIMARY KEY,stock DOUBLE DEFAULT 0,safety_stock DOUBLE DEFAULT 0,lead_time DOUBLE DEFAULT 3,updated_at VARCHAR(40)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS users(id INT AUTO_INCREMENT PRIMARY KEY,fullname VARCHAR(255),email VARCHAR(255) UNIQUE,password_hash VARCHAR(255),role VARCHAR(50) DEFAULT 'manager',active TINYINT DEFAULT 1,created_at VARCHAR(40)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS intervention_outcomes(id INT AUTO_INCREMENT PRIMARY KEY,batch_id VARCHAR(100),action VARCHAR(255),baseline_risk DOUBLE,predicted_risk DOUBLE,actual_risk DOUBLE,status VARCHAR(50),user_email VARCHAR(255),created_at VARCHAR(40)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS model_registry(id INT AUTO_INCREMENT PRIMARY KEY,model_name VARCHAR(255),version VARCHAR(100),metrics_json LONGTEXT,status VARCHAR(50),created_at VARCHAR(40)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS alert_actions(id INT AUTO_INCREMENT PRIMARY KEY,alert_id INT,batch_id VARCHAR(100),action VARCHAR(100),user_email VARCHAR(255),note TEXT,created_at VARCHAR(40),INDEX(batch_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS devices(id INT AUTO_INCREMENT PRIMARY KEY,device_id VARCHAR(100) UNIQUE,device_type VARCHAR(100),status VARCHAR(50),last_seen VARCHAR(40),packets INT DEFAULT 0) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS notifications(id INT AUTO_INCREMENT PRIMARY KEY,batch_id VARCHAR(100),title VARCHAR(255),message TEXT,severity VARCHAR(30) DEFAULT 'INFO',read_flag TINYINT DEFAULT 0,target_url VARCHAR(500),created_at VARCHAR(40)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS shipment_events(id INT AUTO_INCREMENT PRIMARY KEY,batch_id VARCHAR(100),event_type VARCHAR(100),title VARCHAR(255),detail TEXT,severity VARCHAR(30) DEFAULT 'INFO',created_at VARCHAR(40),INDEX(batch_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS twin_states(id INT AUTO_INCREMENT PRIMARY KEY,batch_id VARCHAR(100),scenario VARCHAR(100),baseline_risk DOUBLE,simulated_risk DOUBLE,temperature DOUBLE,delay_hours DOUBLE,action VARCHAR(255),created_at VARCHAR(40),INDEX(batch_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS recovery_resources(id INT AUTO_INCREMENT PRIMARY KEY,resource_code VARCHAR(100) UNIQUE,name VARCHAR(255),resource_type VARCHAR(100),city VARCHAR(100),latitude DOUBLE,longitude DOUBLE,cooling TINYINT DEFAULT 0,reefer TINYINT DEFAULT 0,quality_lab TINYINT DEFAULT 0,capacity_status VARCHAR(50) DEFAULT 'Available',operating_hours VARCHAR(100) DEFAULT '24/7',active TINYINT DEFAULT 1) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS recovery_plans(id INT AUTO_INCREMENT PRIMARY KEY,batch_id VARCHAR(100),action_code VARCHAR(100),resource_code VARCHAR(100),baseline_risk DOUBLE,predicted_risk DOUBLE,risk_reduction DOUBLE,predicted_status VARCHAR(50),status VARCHAR(50) DEFAULT 'PROPOSED',approved_by VARCHAR(255),created_at VARCHAR(40),updated_at VARCHAR(40),INDEX(batch_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS support_routes(id INT AUTO_INCREMENT PRIMARY KEY,batch_id VARCHAR(100),resource_code VARCHAR(100),start_lat DOUBLE,start_lon DOUBLE,dest_lat DOUBLE,dest_lon DOUBLE,distance_km DOUBLE,eta_min INT,status VARCHAR(50) DEFAULT 'IN_PROGRESS',progress DOUBLE DEFAULT 0,started_at VARCHAR(40),arrived_at VARCHAR(40),created_by VARCHAR(255),INDEX(batch_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
]

def _server_connection(database=None):
    return pymysql.connect(host=DB_HOST,port=DB_PORT,user=DB_USER,password=DB_PASSWORD,database=database,charset='utf8mb4',cursorclass=DictCursor,autocommit=False)

def ensure_database():
    c=_server_connection()
    try:
        with c.cursor() as cur: cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        c.commit()
    finally: c.close()

class CompatConnection:
    def __init__(self, raw): self.raw=raw
    def cursor(self): return self.raw.cursor()
    def execute(self, q, args=()):
        q=q.replace('?', '%s').replace("datetime('now')", 'NOW()')
        cur=self.raw.cursor(); cur.execute(q,args); return cur
    def commit(self): return self.raw.commit()
    def rollback(self): return self.raw.rollback()
    def close(self): return self.raw.close()
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb):
        if exc_type: self.raw.rollback()
        self.raw.close()

def connect():
    return CompatConnection(_server_connection(DB_NAME))

def init_db():
    ensure_database()
    with connect() as c:
        with c.cursor() as cur:
            for s in SCHEMA_STATEMENTS: cur.execute(s)
        c.commit()

def init_phase7():
    init_db(); now=datetime.now().isoformat(timespec='seconds')
    with connect() as c:
        with c.cursor() as cur:
            for did,typ in [('TEMP-001','Temperature'),('GPS-102','GPS'),('HUM-021','Humidity'),('DOOR-004','Door')]:
                cur.execute("INSERT INTO devices(device_id,device_type,status,last_seen,packets) VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE device_type=VALUES(device_type)",(did,typ,'Connected',now,14829))
        c.commit()

def init_ops8():
    init_db()
    demo=[
      ('MUM-CS-01','Mumbai Recovery Cold Hub','Cold Storage','Mumbai',19.0760,72.8777,1,1,0,'Available','24/7'),
      ('MUM-LAB-01','Mumbai Quality Assessment Lab','Quality Lab','Mumbai',19.0178,73.0169,1,0,1,'Available','24/7'),
      ('PUN-CS-01','Pune Recovery Warehouse','Cold Storage','Pune',18.5204,73.8567,1,1,0,'Available','24/7'),
      ('PUN-LAB-01','Pune Supply Quality Lab','Quality Lab','Pune',18.5314,73.8446,1,0,1,'Available','08:00-22:00'),
      ('DEL-CS-01','Delhi Refrigerated Logistics Hub','Cold Storage','Delhi',28.6139,77.2090,1,1,0,'Available','24/7'),
      ('NAS-CS-01','Nashik Reefer Recovery Point','Cold Storage','Nashik',19.9975,73.7898,1,1,0,'Available','24/7'),
      ('NAG-CS-01','Nagpur Recovery Hub','Cold Storage','Nagpur',21.1458,79.0882,1,1,0,'Available','24/7')
    ]
    with connect() as c:
        with c.cursor() as cur:
            for x in demo:
                cur.execute("INSERT INTO recovery_resources(resource_code,name,resource_type,city,latitude,longitude,cooling,reefer,quality_lab,capacity_status,operating_hours) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name),resource_type=VALUES(resource_type)",x)
        c.commit()

def rows(q,args=()):
    q=q.replace('?', '%s').replace("datetime('now')", 'NOW()')
    with connect() as c:
        with c.cursor() as cur: cur.execute(q,args); return list(cur.fetchall())

def upsert_shipment(r):
    now=datetime.now().isoformat(timespec='seconds')
    fields=['batch_id','product','origin','destination','location','logistics_stage','transport_mode','thermal_temp','room_temperature','humidity','expiry_hours','oob_hours','freezer_hours','refrigeration_hours','delay_hours','risk_probability','risk_level','quality_risk','delay_risk','environment_risk','operational_risk','predicted_outcome','created_at','updated_at']
    vals=[r.get('batch_id'),r.get('product','Temperature-sensitive goods'),r.get('origin'),r.get('destination'),r.get('location'),r.get('logistics_stage'),r.get('transport_mode'),r.get('thermal_temp'),r.get('room_temperature'),r.get('humidity'),r.get('expiry_hours'),r.get('oob_hours',0),r.get('freezer_hours',0),r.get('refrigeration_hours',0),r.get('delay_hours',0),r.get('risk_probability'),r.get('risk_level'),r.get('quality_risk'),r.get('delay_risk'),r.get('environment_risk'),r.get('operational_risk'),r.get('predicted_outcome'),now,now]
    updates=','.join(f'{f}=VALUES({f})' for f in fields[1:-2])+',updated_at=VALUES(updated_at)'
    with connect() as c:
        with c.cursor() as cur: cur.execute(f"INSERT INTO shipments({','.join(fields)}) VALUES({','.join(['%s']*len(fields))}) ON DUPLICATE KEY UPDATE {updates}",vals)
        c.commit()

def _insert(sql,args):
    with connect() as c:
        with c.cursor() as cur: cur.execute(sql,args)
        c.commit()

def add_telemetry(r): _insert('INSERT INTO telemetry(batch_id,temperature,room_temperature,humidity,expiry_hours,oob_hours,risk_probability,risk_level,recorded_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',(r.get('batch_id'),r.get('thermal_temp'),r.get('room_temperature'),r.get('humidity'),r.get('expiry_hours'),r.get('oob_hours',0),r.get('risk_probability'),r.get('risk_level'),datetime.now().isoformat(timespec='seconds')))
def add_alert(batch,severity,title,message): _insert('INSERT INTO alerts(batch_id,severity,title,message,created_at) VALUES(%s,%s,%s,%s,%s)',(batch,severity,title,message,datetime.now().isoformat(timespec='seconds')))
def add_simulation(batch,base,sim,inputs): _insert('INSERT INTO simulations(batch_id,baseline_risk,simulated_risk,inputs,created_at) VALUES(%s,%s,%s,%s,%s)',(batch,base,sim,json.dumps(inputs),datetime.now().isoformat(timespec='seconds')))
def add_event(batch,event_type,title,detail='',severity='INFO'): _insert('INSERT INTO shipment_events(batch_id,event_type,title,detail,severity,created_at) VALUES(%s,%s,%s,%s,%s,%s)',(batch,event_type,title,detail,severity,datetime.now().isoformat(timespec='seconds')))
def add_notification(batch,title,message,severity='INFO',target_url=None): _insert('INSERT INTO notifications(batch_id,title,message,severity,target_url,created_at) VALUES(%s,%s,%s,%s,%s,%s)',(batch,title,message,severity,target_url or (f'/shipment/{batch}' if batch else '/alerts'),datetime.now().isoformat(timespec='seconds')))
def add_audit(event_type,batch_id,payload):
    prev=rows('SELECT event_hash FROM audit_log ORDER BY id DESC LIMIT 1'); prev=prev[0]['event_hash'] if prev else 'GENESIS'
    text=json.dumps(payload,sort_keys=True,default=str); h=hashlib.sha256(f'{prev}|{event_type}|{batch_id}|{text}'.encode()).hexdigest()
    _insert('INSERT INTO audit_log(event_type,batch_id,payload,previous_hash,event_hash,created_at) VALUES(%s,%s,%s,%s,%s,%s)',(event_type,batch_id,text,prev,h,datetime.now().isoformat(timespec='seconds'))); return h

def save_passport(batch_id,payload):
    now=datetime.now().isoformat(timespec='seconds')
    _insert('INSERT INTO product_passports(batch_id,passport_json,created_at,updated_at) VALUES(%s,%s,%s,%s) ON DUPLICATE KEY UPDATE passport_json=VALUES(passport_json),updated_at=VALUES(updated_at)',(batch_id,json.dumps(payload),now,now))
