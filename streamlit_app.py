import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
import matplotlib.pyplot as plt

# ---------------- CONFIG ---------------- #
EXCEL_FILE = "data.xlsx"  # Lưu vĩnh viễn dữ liệu
COLUMNS = ["Tên", "Lớp", "Ngày", "Giáo viên"]

st.set_page_config(page_title="Student Homework Tracker", page_icon="📚", layout="wide")

# ---------------- HELPER FUNCTIONS ---------------- #
def load_data():
    """Load data từ file Excel nếu có, nếu không tạo DataFrame rỗng"""
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    # Ép kiểu ngày để tránh lỗi ArrowTypeError
    if "Ngày" in df.columns:
        df["Ngày"] = pd.to_datetime(df["Ngày"])

    with pd.ExcelWriter(EXCEL_FILE, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="NoHomework")
        worksheet = writer.sheets["NoHomework"]

        workbook  = writer.book
        border_fmt = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        rows, cols = df.shape
        worksheet.set_column(0, cols-1, 15, border_fmt)
        worksheet.conditional_format(0, 0, rows, cols-1, 
                                     {'type': 'no_blanks', 'format': border_fmt})

        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len, border_fmt)


def export_excel(df, filename):
    """Trả về file Excel dạng BytesIO để download"""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="NoHomework")
        worksheet = writer.sheets["NoHomework"]
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)
    return buffer

def export_csv(df):
    """Trả về file CSV encode UTF-8"""
    return df.to_csv(index=False).encode("utf-8")

def plot_stats(df, col, title):
    """Vẽ biểu đồ đếm theo cột"""
    fig, ax = plt.subplots()
    counts = df[col].value_counts()
    counts.plot(kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_ylabel("Số HS")
    st.pyplot(fig)

# ---------------- APP UI ---------------- #
st.title("📚 Student Assignment Tracker (SA-Track)")

df = load_data()

# --- FORM INPUT --- #
st.sidebar.header("➕ Add Student")
with st.sidebar.form("add_student"):
    name = st.text_input("Student Name")
    classroom = st.text_input("Class")
    date = st.date_input("Date")
    teacher = st.text_input("Teacher Name")  # phân biệt GV
    submitted = st.form_submit_button("Add Student ❄️")

    if submitted:
        if name.strip() == "" or classroom.strip() == "" or teacher.strip() == "":
            st.sidebar.error("⚠️ Please fill all fields!")
        else:
            new_row = {"Tên": name, "Lớp": classroom, "Ngày": date, "Giáo viên": teacher}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.sidebar.success(f"✅ Added: {name}")
            st.snow()   # hiệu ứng thêm HS

# --- MAIN DATAFRAME --- #
st.subheader("📋 Students not finished homework")
if df.empty:
    st.info("No data yet. Please add students from sidebar.")
else:
    st.dataframe(df, use_container_width=True)

    # --- REMOVE STUDENT --- #
    with st.expander("🗑️ Remove Student"):
        selected = st.selectbox("Select student to remove", df["Tên"].unique())
        if st.button("Remove Student 🎈"):
            df = df[df["Tên"] != selected]
            save_data(df)
            st.success(f"🗑️ Removed {selected}")
            st.balloons()  # hiệu ứng xoá HS

    # --- EXPORT SECTION --- #
    st.subheader("💾 Export Data")
    col1, col2 = st.columns(2)

    today_str = datetime.now().strftime("%d-%m-%Y")
    filename_base = f"Not Finish Homework {today_str}"

    with col1:
        buffer = export_excel(df, filename_base)
        st.download_button(
            label="⬇️ Download Excel",
            data=buffer,
            file_name=f"{filename_base}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col2:
        csv_data = export_csv(df)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name=f"{filename_base}.csv",
            mime="text/csv"
        )

    # --- DASHBOARD / STATS --- #
    st.subheader("📊 Dashboard & Statistics")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("👨‍🎓 Total Students", len(df))
    with c2:
        st.metric("🏫 Classes", df["Lớp"].nunique())
    with c3:
        st.metric("👩‍🏫 Teachers", df["Giáo viên"].nunique())

    st.markdown("---")
    colA, colB = st.columns(2)

    with colA:
        plot_stats(df, "Lớp", "Students per Class")
    with colB:
        plot_stats(df, "Giáo viên", "Students per Teacher")

# ---------------- END ---------------- #
