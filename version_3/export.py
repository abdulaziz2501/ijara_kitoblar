import pandas as pd
import datetime
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from database import get_db


# ===============================
#   1) EXCEL EXPORT
# ===============================
def export_excel():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT username, total_count FROM stats_total")
    total = cursor.fetchall()

    cursor.execute("SELECT username, count, date FROM stats_daily")
    daily = cursor.fetchall()

    db.close()

    df_total = pd.DataFrame(total, columns=["Username", "Total Audio"])
    df_daily = pd.DataFrame(daily, columns=["Username", "Count", "Date"])

    # Save to excel
    with pd.ExcelWriter("stats.xlsx") as writer:
        df_total.to_excel(writer, sheet_name="Total Stats", index=False)
        df_daily.to_excel(writer, sheet_name="Daily Stats", index=False)

    return "stats.xlsx"



# ===============================
#   2) PDF EXPORT
# ===============================
def export_pdf():
    file_name = "stats.pdf"
    c = canvas.Canvas(file_name, pagesize=A4)

    width, height = A4
    x = 50
    y = height - 50

    c.setFont("Helvetica-Bold", 18)
    c.drawString(x, y, "Audio Statistikasi (PDF)")

    y -= 30
    c.setFont("Helvetica", 12)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT username, total_count FROM stats_total")
    data = cursor.fetchall()

    db.close()

    for username, total in data:
        line = f"{username}: {total} ta audio"
        c.drawString(x, y, line)
        y -= 20

        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    return file_name



# ===============================
#   3) GRAPH EXPORT (PNG)
# ===============================
def export_graph():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT username, date, count FROM stats_daily")
    rows = cursor.fetchall()

    db.close()

    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=["Username", "Date", "Count"])
    df["Date"] = pd.to_datetime(df["Date"])

    plt.figure(figsize=(10, 5))

    for username in df["Username"].unique():
        user_data = df[df["Username"] == username]
        plt.plot(
            user_data["Date"],
            user_data["Count"],
            label=username
        )

    plt.title("Kunlik audio statistikasi")
    plt.xlabel("Sana")
    plt.ylabel("Audio soni")
    plt.legend()
    plt.grid(True)

    graph_file = "stats.png"
    plt.savefig(graph_file)
    plt.close()

    return graph_file
