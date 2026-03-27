import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, usd, lookup

# Cấu hình ứng dụng
app = Flask(__name__)

# Đảm bảo các phản hồi không được lưu vào bộ nhớ đệm
@app.after_request
def after_request(request):
    """Ensure responses aren't cached"""
    request.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    request.headers["Expires"] = 0
    request.headers["Pragma"] = "no-cache"
    return request

# Cấu hình custom filter cho tiền tệ
app.jinja_env.filters["usd"] = usd

# Cấu hình session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Kết nối database
db = SQL("sqlite:///project.db")

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
    level = user["role_level"]
    now = datetime.now()
    month = now.month
    year = now.year

    # 1. Định nghĩa chuỗi truy vấn gốc (Base Query)
    # Dùng để lấy chi tiết từng nhân viên hiện lên bảng
    base_query_string = """
        SELECT
            u.id AS user_id, u.full_name, u.manager_id, u.role_level,
            t.amount AS target,
            IFNULL(SUM(s.amount), 0) AS actual,
            CASE
                WHEN t.amount > 0 THEN (IFNULL(SUM(s.amount), 0) * 1.0 / t.amount) * 100
                ELSE 0
            END AS percentage
        FROM users u
        JOIN targets t ON u.id = t.user_id
        LEFT JOIN sales s ON u.id = s.user_id
            AND strftime('%m', s.timestamp) = ? AND strftime('%Y', s.timestamp) = ?
        WHERE t.month = ? AND t.year = ?
    """
    time_params = [f"{month:02}", str(year), month, year]

    # 2. Xử lý logic theo cấp bậc
    if level == 1: # ASM: Tính tổng toàn khu vực
        summary = db.execute("""
            SELECT
                SUM(t.amount) AS total_target,
                IFNULL(SUM(s.amount), 0) AS total_actual
            FROM users u
            JOIN targets t ON u.id = t.user_id
            LEFT JOIN sales s ON u.id = s.user_id
                AND strftime('%m', s.timestamp) = ? AND strftime('%Y', s.timestamp) = ?
            WHERE t.month = ? AND t.year = ?
        """, *time_params)[0]

        sales_data = db.execute(base_query_string + " GROUP BY u.id", *time_params)
        return render_template("index.html", sales=sales_data, summary=summary, level=level, month=month)

    elif level == 2: # Trưởng nhóm: Cá nhân + lính
        group_data = db.execute("""
            SELECT
                SUM(t.amount) AS target,
                IFNULL(SUM(s.amount), 0) AS actual
            FROM users u
            JOIN targets t ON u.id = t.user_id
            LEFT JOIN sales s ON u.id = s.user_id
                AND strftime('%m', s.timestamp) = ? AND strftime('%Y', s.timestamp) = ?
            WHERE t.month = ? AND t.year = ?
            AND (u.id = ? OR u.manager_id = ?)
        """, *time_params, user_id, user_id)[0]

        # Tính % hoàn thành của cả nhóm
        group_data["percentage"] = (group_data["actual"] * 100.0 / group_data["target"]) if group_data["target"] > 0 else 0

        sales_data = db.execute(base_query_string + " AND (u.id = ? OR u.manager_id = ?) GROUP BY u.id", *time_params, user_id, user_id)
        return render_template("index.html", sales=sales_data, group_data=group_data, level=level, month=month)

    else: # Agent: Chỉ thấy chính mình
        sales_data = db.execute(base_query_string + " AND u.id = ? GROUP BY u.id", *time_params, user_id)
        return render_template("index.html", sales=sales_data, level=level, month=month)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return apology("Phải cung cấp đủ tên đăng nhập và mật khẩu", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Sai tên đăng nhập hoặc mật khẩu", 403)

        session["user_id"] = rows[0]["id"]
        session["role_level"] = rows[0]["role_level"]
        session["full_name"] = rows[0]["full_name"]

        flash(f"Chào mừng trở lại, {rows[0]['full_name']}!")
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        full_name = request.form.get("full_name")
        role_level = request.form.get("role_level")

        # 1. Kiểm tra đầy đủ thông tin
        if not username or not password or not full_name or not role_level:
            return apology("Vui lòng nhập đầy đủ thông tin", 400)

        if password != confirmation:
            return apology("Mật khẩu không khớp", 400)

        # 2. Lưu vào Database
        try:
            # Ép kiểu an toàn
            level = int(role_level)
            hash = generate_password_hash(password)

            db.execute("INSERT INTO users (username, hash, full_name, role_level) VALUES (?, ?, ?, ?)",
                       username, hash, full_name, level)
        except ValueError:
            return apology("Cấp bậc không hợp lệ", 400)
        except Exception as e:
            # Nếu tên đăng nhập trùng, sqlite sẽ báo lỗi ở đây
            return apology("Tên đăng nhập đã tồn tại hoặc lỗi hệ thống", 400)

        flash("Đăng ký thành công!")
        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/team", methods=["GET", "POST"])
@login_required
def team():
    user_id = session["user_id"]
    if session.get("role_level") != 1:
        return apology("Chỉ ASM mới có quyền truy cập", 403)

    if request.method == "POST":
        staff_id = request.form.get("staff_id")
        new_manager_id = request.form.get("manager_id")

        if not staff_id or not new_manager_id:
            return apology("Thiếu thông tin cập nhật", 400)

        db.execute("UPDATE users SET manager_id = ? WHERE id = ?", new_manager_id, staff_id)
        flash("Cập nhật sơ đồ tổ chức thành công!")
        return redirect("/team")

    else:
        team_members = db.execute("""
            SELECT u1.*, u2.full_name AS manager_name
            FROM users u1
            LEFT JOIN users u2 ON u1.manager_id = u2.id
            ORDER BY u1.role_level ASC
        """)
        potential_managers = db.execute("SELECT id, full_name FROM users WHERE role_level IN (1, 2)")
        return render_template("team.html", team=team_members, managers=potential_managers)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """Nhân viên cập nhật doanh số mới đạt được"""
    if request.method == "POST":
        amount = request.form.get("amount")
        customer = request.form.get("customer_name")
        note = request.form.get("note")

        # 1. Kiểm tra đầu vào
        if not amount or float(amount) <= 0:
            return apology("Số tiền phải lớn hơn 0", 400)

        # 2. Lưu vào bảng sales
        user_id = session["user_id"]
        db.execute("""
            INSERT INTO sales (user_id, amount, customer_name, note)
            VALUES (?, ?, ?, ?)
        """, user_id, amount, customer, note)

        flash(f"Đã cập nhật đơn hàng {usd(float(amount))} thành công!")
        return redirect("/")

    else:
        return render_template("update.html")

@app.route("/set_targets", methods=["GET", "POST"])
@login_required
def set_targets():
    """ASM giao chỉ tiêu cho nhân viên"""
    # Chỉ Level 1 (ASM) mới có quyền vào đây
    if session.get("role_level") != 1:
        return apology("Chỉ ASM mới có quyền giao chỉ tiêu", 403)

    if request.method == "POST":
        staff_id = request.form.get("staff_id")
        amount = request.form.get("amount")
        month = datetime.now().month
        year = datetime.now().year

        if not staff_id or not amount or float(amount) <= 0:
            return apology("Thông tin không hợp lệ", 400)

        # Kiểm tra xem đã có chỉ tiêu cho tháng này chưa, nếu có thì UPDATE, chưa thì INSERT
        existing = db.execute("SELECT id FROM targets WHERE user_id = ? AND month = ? AND year = ?",
                              staff_id, month, year)

        if existing:
            db.execute("UPDATE targets SET amount = ? WHERE id = ?", amount, existing[0]["id"])
        else:
            db.execute("INSERT INTO targets (user_id, month, year, amount) VALUES (?, ?, ?, ?)",
                       staff_id, month, year, amount)

        flash("Đã giao chỉ tiêu thành công!")
        return redirect("/")

    else:
        # Lấy danh sách nhân viên để đổ vào dropdown
        staff_list = db.execute("SELECT id, full_name FROM users WHERE role_level > 1")
        return render_template("set_targets.html", staff_list=staff_list)

@app.route("/history")
@login_required
def history():
    """Hiển thị lịch sử các đơn hàng đã cập nhật"""
    user_id = session["user_id"]
    level = session.get("role_level")

    if level == 1: # ASM: Xem tất cả đơn hàng trong hệ thống
        sales = db.execute("""
            SELECT s.*, u.full_name
            FROM sales s
            JOIN users u ON s.user_id = u.id
            ORDER BY s.timestamp DESC
        """)
    else: # Nhân viên & Trưởng nhóm: Chỉ xem đơn của chính mình
        sales = db.execute("""
            SELECT s.*, u.full_name
            FROM sales s
            JOIN users u ON s.user_id = u.id
            WHERE s.user_id = ?
            ORDER BY s.timestamp DESC
        """, user_id)

    return render_template("history.html", sales=sales)

@app.route("/reset_target", methods=["POST"])
@login_required
def reset_target():
    if session.get("role_level") != 1:
        return apology("Bạn không có quyền này", 403)

    staff_id = request.form.get("staff_id")
    # Lấy thời gian thực tế để đồng bộ với Dashboard
    now = datetime.now()
    month = now.month
    year = now.year

    if staff_id:
        db.execute("""
            UPDATE targets
            SET amount = 0
            WHERE user_id = ? AND month = ? AND year = ?
        """, staff_id, month, year)

        flash(f"Đã đưa chỉ tiêu nhân viên về 0 thành công!")

    return redirect("/")

@app.route("/reset_all_targets", methods=["POST"])
@login_required
def reset_all_targets():
    """ASM đưa toàn bộ chỉ tiêu đội ngũ về 0 cho tháng hiện tại"""
    if session.get("role_level") != 1:
        return apology("Chỉ ASM mới có quyền reset toàn bộ", 403)

    now = datetime.now()
    month = now.month
    year = now.year

    # Cập nhật tất cả bản ghi của tháng/năm hiện tại về 0
    db.execute("""
        UPDATE targets
        SET amount = 0
        WHERE month = ? AND year = ?
    """, month, year)

    flash(f"Đã reset toàn bộ chỉ tiêu tháng {month}/{year} về 0!")
    return redirect("/")
@app.route("/delete_sale", methods=["POST"])
@login_required
def delete_sale():
    sale_id = request.form.get("sale_id")
    user_id = session["user_id"]
    role_level = session.get("role_level")

    if not sale_id:
        return apology("Thiếu mã đơn hàng", 400)

    # Nếu là ASM (Level 1) -> Cho phép xóa mọi đơn
    if role_level == 1:
        db.execute("DELETE FROM sales WHERE id = ?", sale_id)
    else:
        # Nếu là nhân viên -> Chỉ xóa đơn của chính mình
        db.execute("DELETE FROM sales WHERE id = ? AND user_id = ?", sale_id, user_id)

    flash("Đã xóa đơn hàng thành công!")
    return redirect("/history")
