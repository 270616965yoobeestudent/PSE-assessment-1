PRAGMA foreign_keys = ON;

BEGIN;

DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS trackings;
DROP TABLE IF EXISTS cars;
DROP TABLE IF EXISTS tracking_devices;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS passports;
DROP TABLE IF EXISTS driver_licenses;
DROP TABLE IF EXISTS admins;

CREATE TABLE passports (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  no              TEXT,
  country_code    TEXT NOT NULL,
  gender          TEXT,
  first_name      TEXT NOT NULL,
  last_name       TEXT NOT NULL,
  expired_at      TEXT,                
  created_at      TEXT,
  updated_at      TEXT
);

CREATE TABLE driver_licenses (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  no              TEXT,
  country_code    TEXT NOT NULL,
  expired_at      TEXT,               
  created_at      TEXT,
  updated_at      TEXT
);

CREATE TABLE tracking_devices (
  no              TEXT PRIMARY KEY,
  gsm_provider    TEXT,
  gsm_no          TEXT,
  created_at      TEXT,
  updated_at      TEXT
);

CREATE TABLE admins (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  username        TEXT NOT NULL,
  password        TEXT NOT NULL
);

CREATE TABLE customers (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  username          TEXT NOT NULL,
  password          TEXT NOT NULL,
  email_address     TEXT,
  address           TEXT,
  birthdate         TEXT,              
  mobile_no         TEXT,
  passport_id       TEXT,
  driver_license_id TEXT,
  created_at        TEXT,
  updated_at        TEXT,
  FOREIGN KEY (passport_id)        REFERENCES passports(id),
  FOREIGN KEY (driver_license_id)  REFERENCES driver_licenses(id)
);

CREATE TABLE cars (
  plate_license      TEXT PRIMARY KEY,
  engine_number      TEXT,
  fuel_type          TEXT,
  make               TEXT,
  model              TEXT,
  year               INTEGER,
  color              TEXT,
  type               TEXT,
  seat               INTEGER,
  mileage            INTEGER,
  minimum_rent       INTEGER,
  maximum_rent       INTEGER,
  factory_date       TEXT,
  weekday_rate       NUMERIC,
  weekend_rate       NUMERIC,
  available          INTEGER,          
  tracking_device_no TEXT,
  created_at         TEXT,
  updated_at         TEXT,
  FOREIGN KEY (tracking_device_no) REFERENCES tracking_devices(no)
);

CREATE TABLE trackings (
  id                  INTEGER PRIMARY KEY AUTOINCREMENT,
  latitude            REAL,
  longitude           REAL,
  fuel_level          REAL,
  fuel_litre          REAL,
  fuel_kwh            REAL,
  speed_kmh           REAL,
  engine_status       INTEGER,         
  gps_signal_level    REAL,
  gsm_signal_level    REAL,
  car_plate_license   TEXT NOT NULL,
  tracking_device_no  TEXT,
  created_at          TEXT,
  updated_at          TEXT,
  FOREIGN KEY (car_plate_license)  REFERENCES cars(plate_license),
  FOREIGN KEY (tracking_device_no) REFERENCES tracking_devices(no)
);

CREATE TABLE orders (
  id                   INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id          INTEGER NOT NULL,
  car_plate_license    TEXT NOT NULL,
  started_at           TEXT,
  ended_at             TEXT,
  receive_at           TEXT,
  return_at            TEXT,
  total_day            INTEGER,
  total_weekday_amount NUMERIC,
  total_weekend_amount NUMERIC,
  total_amount         NUMERIC,
  created_at           TEXT,
  updated_at           TEXT,
  deleted_at           TEXT,
  FOREIGN KEY (customer_id)       REFERENCES customers(id),
  FOREIGN KEY (car_plate_license) REFERENCES cars(plate_license)
);

CREATE TABLE invoices (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id    INTEGER NOT NULL,
  amount      NUMERIC NOT NULL,
  paid_amount NUMERIC,
  paid_at     TEXT,
  created_at  TEXT,
  updated_at  TEXT,
  FOREIGN KEY (order_id) REFERENCES orders(id)
);

COMMIT;
