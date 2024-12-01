import re, requests as req, sqlite3 as sql3
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox, ttk

DB = "contacts.db"
DEFAULT_URL = ""   #測試用(景觀系)無法抓取人工智慧及資工，資工網頁好爛

"""建立資料庫及資料表"""
def database():
    conn = sql3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(

        """CREATE TABLE IF NOT EXISTS contacts (
            iid INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title TEXT NOT NULL,
            email TEXT NOT NULL
        )"""

    )
    conn.commit()
    conn.close()

"""資訊存入資料庫且避免重複記錄"""
def saves(name: str, title: str, email: str) -> None:
    conn = sql3.connect(DB)
    cursor = conn.cursor()

    """檢查資料存在 or 重複"""
    try:
        cursor.execute("""SELECT 1 FROM contacts WHERE name = ? AND email = ?""", (name, email))
        if cursor.fetchone():
            print(f"資料已經存在: {name}, {email}")
            return
        cursor.execute("""INSERT INTO contacts (name, title, email)VALUES (?, ?, ?)""", (name, title, email))   # 增加資料
        conn.commit()
    except sql3.Error:
        pass
    finally:
        conn.close()

"""用正規表示式獲取資訊"""
def parse_contacts(html: str) -> list[tuple[str, str, str]]:
    contact_pattern = re.compile(r'<a href=".*?"><img.*?alt="(.*?)".*?</a>.*?職　　稱：</td>\s*<td>(.*?)</td>.*?電子郵件 :.*?mailto:(.*?)"',re.DOTALL)

    matches = contact_pattern.findall(html)

    contacts = []
    for i in matches:
        name, title, email = i
        if name and title and email:
            contacts.append((name, title, email))
    return contacts

"""發送 HTTP 請求獲取資訊"""
def scrapes(url: str) -> list[tuple[str, str, str]]:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = req.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return parse_contacts(response.text)
    except req.exceptions.RequestException as e:
        messagebox.showerror("網路錯誤", f"無法連線至 {url}：{e}")
        return []

"""顯示聯絡資訊"""
def display(tree: ttk.Treeview, contacts: list[tuple[str, str, str]]) -> None:
    tree.delete(*tree.get_children())  # 清空表格
    for i in contacts:
        tree.insert('', 'end', values = i)

"""主程式，建立 Tkinter 界面並執行應用程式"""
def main():
    database()
    def on_scrape():
        url = url_var.get()
        contacts = scrapes(url)
        if contacts:
            tree.delete(*tree.get_children())
            for name, title, email in contacts:
                saves(name, title, email)
            display(tree, contacts)

    root = Tk()
    root.title("聯絡資訊擷取工具")
    root.geometry("800x600")

    # 輸入url
    url_var = StringVar(value=DEFAULT_URL)
    Label(root, text="URL：").grid(row=0, column=0, sticky='w', padx=10, pady=10)
    Entry(root, textvariable=url_var, width=50).grid(row=0, column=1, sticky='ew', padx=10, pady=10)
    Button(root, text="抓取", command=on_scrape).grid(row=0, column=2, padx=10, pady=10)

    # 顯示區域
    tree = ttk.Treeview(root, columns=("姓名", "職稱", "電子郵件"), show="headings")
    tree.heading("姓名", text="姓名")
    tree.heading("職稱", text="職稱")
    tree.heading("電子郵件", text="電子郵件")
    tree.column("姓名", width=150, anchor='w')
    tree.column("職稱", width=150, anchor='w')
    tree.column("電子郵件", width=200, anchor='w')
    tree.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)

    # 調整分布
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(1, weight=1)

    root.mainloop()

if __name__ == "__main__":
    main()
