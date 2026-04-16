from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = "cafe.db"


# -----------------------------
# ฟังก์ชันเชื่อมต่อฐานข้อมูล
# -----------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # ทำให้เรียกข้อมูลแบบ dictionary ได้
    conn.execute("PRAGMA foreign_keys = ON")  # เปิดการใช้ foreign key
    return conn


# -----------------------------
# หน้าแรก: แสดงรายการสินค้า
# JOIN กับ categories
# -----------------------------
@app.route("/")
def menu():
    conn = get_db_connection()

    items = conn.execute("""
        SELECT items.id, items.name, items.price, items.image, items.stock,
               items.category_id, categories.name AS category_name
        FROM items
        JOIN categories ON items.category_id = categories.id
        ORDER BY items.id DESC
    """).fetchall()

    conn.close()
    return render_template("menu.html", items=items)


# -----------------------------
# เพิ่มสินค้า
# GET  = แสดงฟอร์ม
# POST = บันทึกข้อมูลลง DB
# -----------------------------
@app.route("/add", methods=["GET", "POST"])
def add_item():
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        image = request.form["image"]
        stock = request.form["stock"]
        category_id = request.form["category_id"]

        conn.execute("""
            INSERT INTO items (name, price, image, stock, category_id)
            VALUES (?, ?, ?, ?, ?)
        """, (name, price, image, stock, category_id))
        conn.commit()
        conn.close()

        return redirect(url_for("menu"))

    categories = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()
    return render_template("append.html", categories=categories)


# -----------------------------
# แก้ไขสินค้า
# -----------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_item(id):
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        image = request.form["image"]
        stock = request.form["stock"]
        category_id = request.form["category_id"]

        conn.execute("""
            UPDATE items
            SET name = ?, price = ?, image = ?, stock = ?, category_id = ?
            WHERE id = ?
        """, (name, price, image, stock, category_id, id))
        conn.commit()
        conn.close()

        return redirect(url_for("menu"))

    item = conn.execute("SELECT * FROM items WHERE id = ?", (id,)).fetchone()
    categories = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()

    return render_template("edit.html", item=item, categories=categories)


# -----------------------------
# ลบสินค้า
# -----------------------------
@app.route("/delete/<int:id>")
def delete_item(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM items WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("menu"))


# -----------------------------
# รันโปรแกรม
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)