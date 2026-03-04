from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "secret123"



# ------------------ DATABASE CONNECTION ------------------
def get_db_connection():
    conn = sqlite3.connect("db.sqlite")
    conn.row_factory = sqlite3.Row
    return conn

# ------------------ HOME ------------------
@app.route("/")
def home():
    return redirect("/events")

# ------------------ REGISTER ------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# ------------------ LOGIN ------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            return redirect("/events")

    return render_template("login.html")

# ------------------ LOGOUT ------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ------------------ EVENTS LIST ------------------
@app.route("/events")
def events():
    conn = get_db_connection()
    events = conn.execute("SELECT * FROM events").fetchall()
    conn.close()
    return render_template("events.html", events=events)

# ------------------ CREATE EVENT (ADMIN ONLY) ------------------
@app.route("/create-event", methods=["GET", "POST"])
def create_event():
    if session.get("role") != "admin":
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        date = request.form["date"]
        venue = request.form["venue"]
        price = request.form["price"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO events (title, description, date, venue, price) VALUES (?, ?, ?, ?, ?)",
            (title, description, date, venue, price)
        )
        conn.commit()
        conn.close()

        return redirect("/events")

    return render_template("create_event.html")


# ------------------ PAY FOR EVENT ------------------
@app.route("/pay/<int:event_id>")
def pay(event_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    event = conn.execute(
        "SELECT * FROM events WHERE id = ?",
        (event_id,)
    ).fetchone()
    conn.close()

    return render_template("payment.html", event=event)


# ------------------ PAYMENT SUCCESS ------------------
@app.route("/payment-success/<int:event_id>")
def payment_success(event_id):
    user_id = session.get("user_id")

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO bookings (user_id, event_id, payment_status) VALUES (?, ?, ?)",
        (user_id, event_id, "Paid")
    )
    conn.commit()
    conn.close()

    return "Payment Successful & Booking Confirmed"

@app.route("/confirm-booking/<int:event_id>", methods=["POST"])
def confirm_booking(event_id):
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO bookings (user_id, event_id) VALUES (?, ?)",
        (user_id, event_id)
    )
    conn.commit()
    conn.close()

    return redirect("/my-bookings")


# ------------------ ADMIN: VIEW BOOKINGS ------------------
@app.route("/admin/bookings")
def admin_bookings():
    if session.get("role") != "admin":
        return redirect("/login")

    conn = get_db_connection()
    bookings = conn.execute("""
        SELECT users.name, events.title, bookings.payment_status
        FROM bookings
        JOIN users ON bookings.user_id = users.id
        JOIN events ON bookings.event_id = events.id
    """).fetchall()
    conn.close()

    return render_template("admin_bookings.html", bookings=bookings)

@app.route("/my-bookings")
def my_bookings():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    bookings = conn.execute("""
        SELECT events.title, events.date, events.venue
        FROM bookings
        JOIN events ON bookings.event_id = events.id
        WHERE bookings.user_id = ?
    """, (session["user_id"],)).fetchall()
    conn.close()

    return render_template("my_bookings.html", bookings=bookings)

@app.route("/admin_dashboard")
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    total_events = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    cursor.close()

    return render_template(
        "admin_dashboard.html",
        total_events=total_events,
        total_users=total_users,
        total_bookings=total_bookings
    )

# ---------------- ADMIN VIEW EVENTS ----------------
@app.route("/admin/events")
def admin_events():
    if session.get("role") != "admin":
        return redirect("/login")

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    cursor.close()

    return render_template("admin_events.html", events=events)


# ---------------- ADD EVENT ----------------
@app.route("/admin/add-event", methods=["GET", "POST"])
def admin_add_event():
    if session.get("role") != "admin":
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        date = request.form["date"]
        venue = request.form["venue"]
        price = request.form["price"]

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO events (title, description, date, venue, price) VALUES (%s,%s,%s,%s,%s)",
            (title, description, date, venue, price)
        )
        mysql.connection.commit()
        cursor.close()

        return redirect("/admin/events")

    return render_template("admin_add_event.html")


# ---------------- EDIT EVENT ----------------
@app.route("/admin/edit-event/<int:id>", methods=["GET", "POST"])
def admin_edit_event(id):
    if session.get("role") != "admin":
        return redirect("/login")

    cursor = mysql.connection.cursor()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        date = request.form["date"]
        venue = request.form["venue"]
        price = request.form["price"]

        cursor.execute(
            "UPDATE events SET title=%s, description=%s, date=%s, venue=%s, price=%s WHERE id=%s",
            (title, description, date, venue, price, id)
        )
        mysql.connection.commit()
        cursor.close()
        return redirect("/admin/events")

    cursor.execute("SELECT * FROM events WHERE id=%s", (id,))
    event = cursor.fetchone()
    cursor.close()

    return render_template("admin_edit_event.html", event=event)


# ---------------- DELETE EVENT ----------------
@app.route("/admin/delete-event/<int:id>")
def admin_delete_event(id):
    if session.get("role") != "admin":
        return redirect("/login")

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM events WHERE id=%s", (id,))
    mysql.connection.commit()
    cursor.close()

    return redirect("/admin/events")


# ------------------ MAIN ------------------
if __name__ == "__main__":
    app.run(debug=True)

