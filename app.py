import re, requests as req, sqlite3 as sql3
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox, ttk

DB = "contacts.db"

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

"""資訊存入資料庫及資料表，且避免重複存入"""
def saves(name: str, title: str, email: str) -> None:
    conn = sql3.connect(DB)
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT 1 FROM contacts WHERE name = ? AND email = ?""", (name, email))
        if cursor.fetchone():
            print(f"資料已存在: {name}, {email}")
            return
        cursor.execute("""INSERT INTO contacts (name, title, email) VALUES (?, ?, ?)""", (name, title, email))
        conn.commit()
    finally:
        conn.close()

"""正規表示法"""
def parses(html: str) -> list[tuple[str, str, str]]:
    contact_pattern = re.compile(r'alt="(.*?)".*?職　*稱[:：]?</td>\s*<td.*?>(.*?)</td>.*?mailto:(.*?)["\']', re.DOTALL)
    matches = contact_pattern.findall(html)
    return [(name.strip(), title.strip(), email.strip()) for name, title, email in matches if name and title and email]

def scrapes(url: str) -> list[tuple[str, str, str]]:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = req.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return parses(response.text)
    except req.exceptions.RequestException as e:
        messagebox.showerror("網路錯誤", f"無法連接網站 {url}：{e}")
        return []

def display(tree: ttk.Treeview, contacts: list[tuple[str, str, str]]) -> None:
    tree.delete(*tree.get_children())
    for contact in contacts:
        tree.insert('', 'end', values=contact)

#主程式
def main():
    database()

    def on_scrape():
        url = url_var.get()
        if not url:
            messagebox.showerror("警告", "無法取得網頁 : 404")
            return
        contacts = scrapes(url)
        if contacts:
            for name, title, email in contacts:
                saves(name, title, email)
            display(tree, contacts)

    root = Tk()
    root.title("聯絡資訊擷取工具")
    root.geometry("800x600")

    url_var = StringVar()
    Label(root, text="URL：").grid(row=0, column=0, sticky='w', padx=10, pady=10)
    Entry(root, textvariable=url_var, width=50).grid(row=0, column=1, sticky='ew', padx=10, pady=10)
    Button(root, text="抓取", command=on_scrape).grid(row=0, column=2, padx=10, pady=10)

    tree = ttk.Treeview(root, columns=("姓名", "職稱", "電子郵件"), show="headings")
    tree.heading("姓名", text="姓名")
    tree.heading("職稱", text="職稱")
    tree.heading("電子郵件", text="電子郵件")
    tree.column("姓名", width=150, anchor='w')
    tree.column("職稱", width=150, anchor='w')
    tree.column("電子郵件", width=200, anchor='w')
    tree.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)

    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.mainloop()

if __name__ == "__main__":
    main()
