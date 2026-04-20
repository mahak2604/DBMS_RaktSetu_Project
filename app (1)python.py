import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error as MySQLError

app = Flask(__name__)
CORS(app)

# ── DB CONFIG ──────────────────────────────────────────────
# Change 'your_password' to your actual MySQL root password.
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'root',
    'database': 'raktsetu'
}

# ── DB HELPER ──────────────────────────────────────────────
def get_db():
    """Open a new MySQL connection. Raises a clean error if DB is unreachable."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except MySQLError as e:
        raise RuntimeError(f"Cannot connect to MySQL: {e}")

def serialize(obj):
    """
    JSON-serialize MySQL rows.
    mysql-connector returns date/datetime as Python objects — Flask's
    default jsonify can't handle them, so we convert them to ISO strings here.
    """
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def rows_to_json(rows):
    """Convert a list of dict rows (possibly containing date objects) to JSON-safe dicts."""
    clean = []
    for row in rows:
        clean.append({k: (v.isoformat() if isinstance(v, (datetime.date, datetime.datetime)) else v)
                      for k, v in row.items()})
    return clean


# ── SERVE FRONTEND ─────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


# ── STATS ──────────────────────────────────────────────────
@app.route('/api/stats')
def stats():
    db = None
    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) AS c FROM donors")
        donors = cur.fetchone()['c']
        cur.execute("SELECT COALESCE(SUM(units), 0) AS c FROM blood_inventory")
        units = cur.fetchone()['c']
        cur.execute("SELECT COUNT(*) AS c FROM blood_requests WHERE status = 'PENDING'")
        pending = cur.fetchone()['c']
        cur.execute("SELECT COUNT(*) AS c FROM hospitals")
        hospitals = cur.fetchone()['c']
        return jsonify(donors=donors, units=int(units), pending=pending, hospitals=hospitals)
    except Exception as e:
        return jsonify(error=str(e)), 500
    finally:
        if db and db.is_connected():
            db.close()


# ── DONORS ─────────────────────────────────────────────────
@app.route('/api/donors', methods=['GET'])
def get_donors():
    db = None
    try:
        search = request.args.get('search', '').strip()
        bg     = request.args.get('blood_group', '').strip()
        db  = get_db()
        cur = db.cursor(dictionary=True)
        sql    = "SELECT * FROM donors WHERE 1=1"
        params = []
        if search:
            sql += " AND (name LIKE %s OR blood_group LIKE %s)"
            params += [f'%{search}%', f'%{search}%']
        if bg:
            sql += " AND blood_group = %s"
            params.append(bg)
        sql += " ORDER BY donor_id"
        cur.execute(sql, params)
        return jsonify(rows_to_json(cur.fetchall()))
    except Exception as e:
        return jsonify(error=str(e)), 500
    finally:
        if db and db.is_connected():
            db.close()


@app.route('/api/donors', methods=['POST'])
def add_donor():
    db = None
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify(error='No JSON body received'), 400

        name  = (data.get('name') or '').strip()
        age   = data.get('age')
        bg    = (data.get('blood_group') or '').strip()
        phone = (data.get('phone') or '').strip()
        city  = (data.get('city') or '').strip()
        last  = data.get('last_donated') or None

        if not name or not bg or not age:
            return jsonify(error='name, age and blood_group are required'), 400
        age = int(age)
        if not (18 <= age <= 65):
            return jsonify(error='Age must be between 18 and 65'), 400

        db  = get_db()
        cur = db.cursor()

        # Generate next unique donor_id
        cur.execute("SELECT donor_id FROM donors ORDER BY donor_id DESC LIMIT 1")
        last_row = cur.fetchone()
        if last_row:
            try:
                n = int(last_row[0][1:]) + 1
            except ValueError:
                n = 1
        else:
            n = 1

        donor_id = f"D{n:03d}"
        while True:
            cur.execute("SELECT 1 FROM donors WHERE donor_id = %s", (donor_id,))
            if not cur.fetchone():
                break
            n += 1
            donor_id = f"D{n:03d}"

        cur.execute(
            "INSERT INTO donors (donor_id, name, age, blood_group, phone, city, last_donated) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (donor_id, name, age, bg, phone, city, last)
        )
        db.commit()
        return jsonify(success=True, donor_id=donor_id)
    except Exception as e:
        if db and db.is_connected():
            db.rollback()
        return jsonify(error=str(e)), 500
    finally:
        if db and db.is_connected():
            db.close()


@app.route('/api/donors/<donor_id>', methods=['DELETE'])
def delete_donor(donor_id):
    db = None
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("DELETE FROM donors WHERE donor_id = %s", (donor_id,))
        db.commit()
        if cur.rowcount == 0:
            return jsonify(error=f"Donor {donor_id} not found"), 404
        return jsonify(success=True)
    except Exception as e:
        if db and db.is_connected():
            db.rollback()
        return jsonify(error=str(e)), 500
    finally:
        if db and db.is_connected():
            db.close()


# ── INVENTORY ──────────────────────────────────────────────
# NOTE: /api/inventory/summary MUST be defined before /api/inventory/<inv_id>/dispense
# so Flask matches the literal "summary" before treating it as a variable.

@app.route('/api/inventory/summary', methods=['GET'])
def inventory_summary():
    db = None
    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            "SELECT blood_group, CAST(SUM(units) AS UNSIGNED) AS units "
            "FROM blood_inventory GROUP BY blood_group ORDER BY blood_group"
        )
        return jsonify(rows_to_json(cur.fetchall()))
    except Exception as e:
        return jsonify(error=str(e)), 500
    finally:
        if db and db.is_connected():
            db.close()


@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    db = None
    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM blood_inventory ORDER BY blood_group, inv_id")
        return jsonify(rows_to_json(cur.fetchall()))
    except Exception as e:
        return jsonify(error=str(e)), 500
    finally:
        if db and db.is_connected():
            db.close()


@app.route('/api/inventory', methods=['POST'])
def add_inventory():
    db = None
    try:
        data  = request.get_json(force=True)
        bg    = (data.get('blood_group') or '').strip()
        units = data.get('units')
        exp   = data.get('expiry_date') or None
        donor = (data.get('donor_id') or '').strip() or None

        if not bg or not units or not exp:
            return jsonify(error='blood_group, units and expiry_date are required'), 400
        units = int(units)
        if units <= 0:
            return jsonify(error='units must be a positive number'), 400

        db  = get_db()
        cur = db.cursor()

        cur.execute("SELECT inv_id FROM blood_inventory ORDER BY inv_id DESC LIMIT 1")
        last_row = cur.fetchone()
        if last_row:
            try:
                n = int(last_row[0][1:]) + 1
            except ValueError:
                n = 1
        else:
            n = 1

        inv_id = f"I{n:03d}"
        while True:
            cur.execute("SELECT 1 FROM blood_inventory WHERE inv_id = %s", (inv_id,))
            if not cur.fetchone():
                break
            n += 1
            inv_id = f"I{n:03d}"

        cur.execute(
            "INSERT INTO blood_inventory (inv_id, blood_group, units, expiry_date, donor_id) "
            "VALUES (%s, %s, %s, %s, %s)",
            (inv_id, bg, units, exp, donor)
        )
        db.commit()
        return jsonify(success=True, inv_id=inv_id)
    except Exception as e:
        if db and db.is_connected():
            db.rollback()
        return jsonify(error=str(e)), 500
    finally:
        if db and db.is_connected():
            db.close()


@app.route('/api/inventory/<inv_id>/dispense', methods=['POST'])
def dispense(inv_id):
    db = None
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute(
            "UPDATE blood_inventory SET units = units - 1 WHERE inv_id = %s AND units > 0",
            (inv_id,)
        )
        db.commit()
        if cur.rowcount == 0:
            return jsonify(error='No units left to dispense or inv_id not found'), 400
        return jsonify(success=True)
    except Exception as e:
        if db and db.is_connected():
            db.rollback()
        return jsonify(error=str(e)), 500
    finally:
        if db and db.is_connected():
            db.close()


# ── REQUESTS ───────────────────────────────────────────────
@app.route('/api/requests', methods=['GET'])
def get_requests():
    db = None
    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("""
            SELECT br.req_id, br.hospital_id, h.name AS hospital_name,
                   br.patient, br.blood_group, br.units,
                   br.priority, br.status, br.contact, br.request_date
            FROM blood_requests br
            LEFT JOIN hospitals h ON br.hospital_id = h.hospital_id
            ORDER BY br.request_date DESC, br.req_id DESC
        """)
        return jsonify(rows_to_json(cur.fetchall()))
    except Exception as e:
        return jsonify(error=str(e)), 500
    finally:
        if db and db.is_connected():
            db.close()


@app.route('/api/requests', methods=['POST'])
def add_request():
    db = None
    try:
        data     = request.get_json(force=True)
        hospital = (data.get('hospital') or '').strip()
        patient  = (data.get('patient') or '').strip()
        bg       = (data.get('blood_group') or 'O+').strip()
        units    = int(data.get('units') or 1)
        priority = (data.get('priority') or 'NORMAL').strip().upper()
        contact  = (data.get('contact') or '').strip()

        if not hospital or not patient:
            return jsonify(error='hospital and patient are required'), 400
        if priority not in ('CRITICAL', 'HIGH', 'NORMAL'):
            priority = 'NORMAL'

        db  = get_db()
        cur = db.cursor()

        # Resolve hospital name → hospital_id
        cur.execute("SELECT hospital_id FROM hospitals WHERE name = %s", (hospital,))
        row = cur.fetchone()
        hospital_id = row[0] if row else None

        # Generate next req_id
        cur.execute("SELECT req_id FROM blood_requests ORDER BY req_id DESC LIMIT 1")
        last_row = cur.fetchone()
        if last_row:
            try:
                n = int(last_row[0][1:]) + 1
            except ValueError:
                n = 1
        else:
            n = 1

        req_id = f"R{n:03d}"
        while True:
            cur.execute("SELECT 1 FROM blood_requests WHERE req_id = %s", (req_id,))
            if not cur.fetchone():
                break
            n += 1
            req_id = f"R{n:03d}"

        cur.execute(
            "INSERT INTO blood_requests "
            "(req_id, hospital_id, patient, blood_group, units, priority, contact) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (req_id, hospital_id, patient, bg, units, priority, contact)
        )
        db.commit()
        return jsonify(success=True, req_id=req_id)
    except Exception as e:
        if db and db.is_connected():
            db.rollback()
        return jsonify(error=str(e)), 500
    finally:
        if db and db.is_connected():
            db.close()


@app.route('/api/requests/<req_id>/status', methods=['PATCH'])
def update_request_status(req_id):
    db = None
    try:
        data   = request.get_json(force=True)
        status = (data.get('status') or '').strip().upper()
        if status not in ('APPROVED', 'FULFILLED'):
            return jsonify(error="status must be 'APPROVED' or 'FULFILLED'"), 400
        db  = get_db()
        cur = db.cursor()
        cur.execute(
            "UPDATE blood_requests SET status = %s WHERE req_id = %s",
            (status, req_id)
        )
        db.commit()
        if cur.rowcount == 0:
            return jsonify(error=f"Request {req_id} not found"), 404
        return jsonify(success=True)
    except Exception as e:
        if db and db.is_connected():
            db.rollback()
        return jsonify(error=str(e)), 500
    finally:
        if db and db.is_connected():
            db.close()


# ── HOSPITALS ──────────────────────────────────────────────
@app.route('/api/hospitals', methods=['GET'])
def get_hospitals():
    db = None
    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM hospitals ORDER BY name")
        return jsonify(rows_to_json(cur.fetchall()))
    except Exception as e:
        return jsonify(error=str(e)), 500
    finally:
        if db and db.is_connected():
            db.close()


# ── SQL CONSOLE ────────────────────────────────────────────
@app.route('/api/sql', methods=['POST'])
def run_sql():
    db = None
    try:
        body  = request.get_json(force=True)
        query = (body.get('query') or '').strip()
        if not query:
            return jsonify(error='No query provided'), 400

        first_word = query.split()[0].lower()
        is_read  = first_word in ('select', 'show', 'describe', 'explain')
        is_write = first_word in ('insert', 'update', 'delete')

        if not (is_read or is_write):
            return jsonify(error='Only SELECT / SHOW / DESCRIBE / INSERT / UPDATE / DELETE allowed.'), 400

        db  = get_db()
        # Use buffered=True so we can call fetchall() safely even for DML
        cur = db.cursor(dictionary=True, buffered=True)
        cur.execute(query)

        if is_read:
            result_rows = cur.fetchall()
            # Extract column names from description (use key 'name' for each descriptor)
            col_names = [desc[0] for desc in cur.description] if cur.description else []
            clean_rows = rows_to_json(result_rows)
            return jsonify(columns=col_names, rows=clean_rows)
        else:
            db.commit()
            affected = cur.rowcount
            return jsonify(message=f'Query OK — {affected} row(s) affected.')

    except MySQLError as e:
        if db and db.is_connected():
            try:
                db.rollback()
            except Exception:
                pass
        return jsonify(error=str(e)), 400
    except Exception as e:
        return jsonify(error=str(e)), 500
    finally:
        if db and db.is_connected():
            db.close()


# ── RUN ────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)