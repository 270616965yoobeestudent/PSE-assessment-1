# Car Rental with Real‑Time GPS (cgps)

<div align="center">
  <img src="screenshots/main_menu.png" alt="Main Menu" width="45%" />
  <img src="screenshots/admin_car_realtime_report.png" alt="Real‑time Tracking Report" width="45%" />
  <br/>
  <em>CLI entrypoint and live GPS tracking table in the Textual UI</em>
</div>

## About cgps
`cgps` stands for “`C`ar rental system with real‑time tracking `GPS`.” It is an end‑to‑end car‑rental platform that pairs operational workflows with continuous telemetry from IoT sensors and GPS/cellular hardware installed in every vehicle. The system streams rich signals—location and speed, engine on/off, fuel percentage and remaining litres or battery kWh, plus GPS/GSM signal strength—so fleet managers can monitor utilization, react quickly, and reduce operational risk. Beyond tracking, cgps supports the full rental lifecycle: customer registration and profile updates, selecting dates and vehicles, approvals, hand‑over and return, and invoicing/payments. A terminal‑native Textual UI delivers fast, accessible screens for both admin and customer flows, while services encapsulate business logic behind a dependency‑injected architecture that cleanly separates CLI, service, and persistence layers. SQLite makes local setup instant, and the repository ships with schema/seed scripts plus a realistic mock tracking generator to demo real‑time updates without physical devices. Together these pieces provide a compact, testable foundation for GPS‑aware fleet operations.

## Overview
- Purpose: Manage a car rental business with admin and customer flows, and visualize real‑time GPS tracking for vehicles in a terminal UI.
- Tech stack: Python (>= 3.13.5), SQLite, dependency‑injector, Textual (TUI), Questionary, Keyring, PyJWT.
- Entrypoints: `cgps` (main CLI).

## Repository Structure
- `cgps/`: Application package
  - `__main__.py`: CLI bootstrap (`cgps` entrypoint)
  - `container.py`: Dependency injection container and wiring
  - `db.sql`, `seed.sql`: Schema and seed data
  - `cli/`: Command‑line commands
    - `app_cli.py`: Top‑level command router for `cgps`
    - `admin_cli.py`: Admin commands (cars, GPS devices, orders, tracking report)
    - `customer_cli.py`: Customer commands (register/login, info, rent, orders)
  - `core/`: Core domain
    - `database.py`: Thin SQLite wrapper (migrations, queries, transactions)
    - `models/`: Dataclasses for entities (Car, TrackingDevice, Order, Tracking, etc.)
    - `services/`: Application services encapsulating DB logic (CarService, GpsService, OrderService, TrackingService, auth services)
    - `mock_tracking.py`: Real‑time tracking data generator (simulated)
    - `utils.py`: Helpers (date/decimal parsing, SQL helpers, etc.)
  - `ui/`: Textual TUI screens/components
    - `tracking_report_ui.py`: Real‑time tracking report table
    - `car_list_ui.py`, `gps_list_ui.py`, `gps_register_ui.py`, `order_list_ui.py`, `rent_ui.py`, `register_ui.py`, `login_ui.py`, etc.
- `config.yml`: App configuration (DB path, salts, secrets)
- `pyproject.toml`: Packaging and console scripts
- `requirements.txt`: Runtime dependencies
- `scripts`: Build script
  - `build_pex.sh`: Build .pex file into `dist/`

## How It Works
- Dependency Injection: `container.py` wires services, UIs, and CLIs via `dependency_injector`. `cgps.__main__` resolves `AppCli` and runs it; the DB connection is closed afterward.
- Storage: SQLite database at the path from `config.yml` (default `cgps.db`).
- Database Lifecycle: `cgps db init` executes `db.sql` then `seed.sql` to create tables and seed sample data.
- Admin Flow (via `cgps admin`):
  - Manage cars and GPS devices (list/update/register) in Textual TUIs.
  - View orders and search customers.
  - Real‑time tracking report: Launches a Textual table showing live positions, engine/fuel/battery, and signal strengths. Uses `core/mock_tracking.trackings_iter` to simulate streaming data per car (with a tracking device). New tracking rows are inserted through `TrackingService.insert_batch` and displayed incrementally.
- Customer Flow (via `cgps customer`):
  - Register/login, update profile, browse available cars for a date range, rent and pay, and view orders.
- Authentication: Admin and customer auth services store credentials with salted hashing and JWT tokens; Keychain service name is configurable in `config.yml`.

## Prerequisites
- Python: >= 3.13.5 (as declared in `pyproject.toml`).
- OS: macOS/Linux/Windows with a terminal that supports Textual.

## Setup
1) Install dependencies (and console scripts)
```bash
pip install -e .        # preferred; installs `cgps`
# or
pip install -r requirements.txt
```

2) Initialize the Database
```bash
cgps db init  
```
- Applies `cgps/db.sql`, then seeds with `cgps/seed.sql`.
- Produces or resets the SQLite file configured in `config.yml`.

3) Configure (optional)
- Edit `config.yml` to change:
  - `database.path`: SQLite file location
  - `app.keychain_service`: name used for secure credential storage
  - `admin.*` and `customer.*`: password salts and JWT secret keys
  
2) Run
```bash
cgps -h  
```

## Mock Accounts
- Seeded users for quick login (passwords are plain text here; hashes in `seed.sql` are `SHA-256(salt || password)` using salts from `config.yml`).
- Admins:
  - username: `admin1`, password: `Admin@123`
  - username: `admin2`, password: `Admin@456`
- Customers:
  - `alice` / `Cust@001`
  - `bob` / `Cust@002`
  - `charlie` / `Cust@003`
  - `diana` / `Cust@004`
  - `edward` / `Cust@005`

## Usage

Show top‑level help
```bash
cgps -h
```

### Customer
Common commands
```bash
cgps customer register      # register a new customer (TUI)
cgps customer login         # login as customer (TUI)
cgps customer logout        # logout
cgps customer info          # view/update profile (TUI)
cgps customer rent          # pick dates, car, and confirm (TUI)
cgps customer order         # list all orders (TUI)
```

Quick login example
```bash
cgps customer login
# username: alice
# password: Cust@001
```

### Admin
Common commands
```bash
cgps admin login            # login as admin (TUI)
cgps admin logout           # logout
cgps admin customer         # customer list/update (TUI)
cgps admin gps              # GPS list/update (TUI)
cgps admin gps register     # register a new GPS (TUI)
cgps admin car              # car list/update/register (TUI)
cgps admin car report       # live tracking report (TUI)
cgps admin order            # order list/update (TUI)
cgps admin order search     # search orders (TUI)
```

Quick login example
```bash
cgps admin login
# username: admin1
# password: Admin@123
```

## Build a self-contained .pyz

This app can be bundled as a zipapp that includes third‑party dependencies.

1. Install pex:

   ```bash
   python3 -m pip install pex     
   ```

2. Build:

   ```bash
   sh scripts/build_pex.sh
   ```

3. Run:

   ```bash
   dist/cgps.pex -h
   ```

## Textual UI Tips
- Navigation and actions are guided onscreen.
- Common keys:
  - Select/submit: Enter
  - Back/cancel: Esc
  - Quit certain screens: `q` or Esc (e.g., Tracking Report)

## Development Notes
- Code style: typed Python with dataclasses for models; services encapsulate SQL.
- Transactions: write ops call `Database.begin()`/`commit()`.
- Tracking stream: `ui/tracking_report_ui.py` filters cars with a `tracking_device_id` and schedules periodic updates; the mock iterator simulates GPS/engine/fuel/signal values.

## Troubleshooting
- No `cgps` command after install: ensure you ran `pip install -e .` in an active venv and that your shell has the venv’s `bin` (or `Scripts`) on PATH.
- Textual UI rendering issues: try a different terminal or disable exotic themes; ensure a Unicode/UTF‑8 locale.
- Database errors: re‑initialize with `cgps db init`, or delete the SQLite file configured in `config.yml` and rerun.

## Screenshots
- Main menu
  
  ![Main Menu](screenshots/main_menu.png)

- Admin
  
  ![Admin Login](screenshots/admin_login.png)
  
  ![GPS List](screenshots/admin_gps_list.png)
  
  ![Register GPS](screenshots/admin_gps_register.png)
  
  ![Car List](screenshots/admin_car_list.png)
  
  ![Car Detail](screenshots/admin_car_detail.png)
  
  ![Register Car](screenshots/admin_car_register.png)
  
  ![Real‑time Tracking Report](screenshots/admin_car_realtime_report.png)
  
  ![Orders List](screenshots/admin_order_list.png)
  
  ![Order Search](screenshots/admin_order_search.png)
  
  ![Order Search Result](screenshots/admin_order_search_result.png)
  
  ![Order Pick Up](screenshots/admin_order_pick_up.png)
  
  ![Order Approve/Reject](screenshots/admin_order_approve_reject.png)
  
  ![Order Drop Off](screenshots/admin_order_drop_off.png)

- Customer
  
  ![Customer Register](screenshots/customer_register.png)
  
  ![Customer Login](screenshots/customer_login.png)
  
  ![Customer Info](screenshots/customer_info.png)
  
  ![Rent Select Date](screenshots/customer_rent_select_date.png)
  
  ![Rent Select Car](screenshots/customer_rent_select_car.png)
  
  ![Rent Summary](screenshots/customer_rent_summary.png)
  
  ![Customer Orders](screenshots/customer_order_list.png)
  
  ![Customer Order Detail](screenshots/customer_order_detail.png)

## License
- For educational/course assessment use. No warranty.
