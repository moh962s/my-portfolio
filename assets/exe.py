import tkinter as tk           # مكتبة الواجهة الرسومية الأساسية
from tkinter import ttk, messagebox  # عناصر محسّنة ونوافذ تنبيه
import json, os, sys                # للتعامل مع الملفات والبيانات والنظام
import re                      # للتحقق من صحة الأسماء

# ═══ دوال التعامل مع مسار الملفات للـ EXE (جديد) ═══
def resource_path(relative_path):
    """ الحصول على المسار الصحيح سواء كان يعمل كـ .py عادي أو كـ EXE """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_data_file_path():
    """ تحديد مسار ملف data.json ليكون بجانب ملف الـ EXE """
    if getattr(sys, 'frozen', False):
        # يعمل كـ EXE
        base_dir = os.path.dirname(sys.executable)
    else:
        # يعمل كـ script بايثون عادي
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "data.json")

# ═══ ثوابت التطبيق ═══
DATA_FILE = get_data_file_path()
MAX_T, MAX_M, MAX_I, MAX_EV = 4, 5, 20, 5  # الحدود القصوى للفرق والأعضاء والأفراد والأحداث
DEFAULT_PTS = [8, 6, 4, 2, 1]  # النقاط الافتراضية للمراتب الخمس

# تصحيح الأخطاء الإملائية في قائمة الأحداث الافتراضية
DEFAULT_EVENTS = [
    {"name": n, "type": t, "category": c} for n, t, c in [
        ("Choir Performance", "Team", "Arts"), ("Painting Competition", "Individual", "Arts"),
        ("Hackathon", "Team", "Technology"), ("Robotics Challenge", "Team", "Technology"),
        ("FIFA Tournament", "Individual", "E-Sports"), ("Valorant Championship", "Team", "E-Sports"),
        ("Tree Planting", "Team", "Community Service"), ("Charity Drive", "Team", "Community Service"),
        ("Cooking Bake-off", "Individual", "Life Skills"), ("Woodworking", "Individual", "Life Skills"),
        ("Math Olympiad", "Individual", "Academic"),("Table Tennis", "Individual", "Athletic"),
    ]]

# ═══ لوحة ألوان أحمر وأبيض  ═══
RED_DARK    = "#8B1A1A"   # أحمر داكن — للعناوين والنصوص المهمة
RED_MAIN    = "#C62828"   # أحمر رئيسي — الأزرار ورؤوس الجداول
RED_BRIGHT  = "#E53935"   # أحمر  — تأثير الضغط على الأزرار
RED_LIGHT   = "#FFCDD2"   # أحمر فاتح — خطوط فاصلة وتمييز
RED_ACCENT  = "#FF5252"   # أحمر لامع — تأثيرات بصرية
WHITE       = "#FFFFFF"   # أبيض نقي
SNOW        = "#FFF8F8"   # أبيض مائل للوردي — الخلفية الرئيسية
CARD_BG     = "#FFFFFF"   # خلفية البطاقات
CARD_BD     = "#E0CCCC"   # حدود البطاقات
TXT_DARK    = "#2D2D2D"   # نص أساسي داكن
TXT_MED     = "#5A5A5A"   # نص متوسط
TXT_LIGHT   = "#999999"   # نص خافت
GOLD_LIGHT  = "#FFF3B0"   # ذهبي فاتح — تمييز المركز الأول
INPUT_BG    = "#FFF5F5"   # خلفية حقول الإدخال
INPUT_BD    = "#E0B0B0"   # حدود حقول الإدخال
TAB_BG      = "#8B1A1A"   # خلفية شريط التبويبات العلوي
TAB_ACTIVE  = "#C62828"   # لون التبويب النشط
TAB_HOVER   = "#A52222"   # لون التبويب عند مرور الماوس


# ═══ تحميل وحفظ البيانات من ملف جيسون ═══
def load():
    # تحميل البيانات المحفوظة أو إرجاع القيم الافتراضية — مع ضمان وجود جميع المفاتيح
    defaults = {"teams": {}, "individuals": [], "events": [dict(e) for e in DEFAULT_EVENTS],
                "scores": [], "points": DEFAULT_PTS[:]}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, val in defaults.items():
            if key not in data:
                data[key] = val
        return data
    return defaults


def save(d):
    # حفظ البيانات الحالية في ملف جيسون بتنسيق مرتب
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


# ═══ دوال مساعدة لبناء عناصر الواجهة وتقليل التكرار ═══
def _round_rect(cv, x1, y1, x2, y2, r, **kw):
    # رسم مستطيل بزوايا دائرية — يُستخدم لحقول الإدخال
    pts = [
        x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r,
        x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2,
        x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r,
        x1, y1+r, x1, y1
    ]
    return cv.create_polygon(pts, smooth=True, **kw)


def lbl(p, txt, r, c, bg=CARD_BG, **k):  # إنشاء تسمية نصية في الشبكة
    w = tk.Label(p, text=txt, bg=bg, fg=TXT_DARK, font=("Segoe UI", 10), **k)
    w.grid(row=r, column=c, sticky="w", padx=8, pady=3)
    return w


def ent(p, var, r, c, width=22):  # إنشاء حقل إدخال بزوايا دائرية أنيقة
    px_w = width * 9 + 24
    h = 34
    rad = 17
    parent_bg = CARD_BG
    try: parent_bg = p.cget("bg")
    except: pass

    cv = tk.Canvas(p, width=px_w, height=h, bg=parent_bg, highlightthickness=0, bd=0)
    cv.grid(row=r, column=c, padx=8, pady=3)
    _round_rect(cv, 1, 1, px_w-1, h-1, rad, fill=INPUT_BG, outline=INPUT_BD, width=1)

    w = tk.Entry(cv, textvariable=var, width=width,
                 bg=INPUT_BG, fg=TXT_DARK, insertbackground=RED_MAIN,
                 font=("Segoe UI", 10), bd=0, relief="flat", highlightthickness=0)
    cv.create_window(px_w//2, h//2, window=w, width=px_w - rad*2 + 10, height=h-12)
    return w


def cmb(p, r, c, w=22, vals=(), cmd=None):  # إنشاء قائمة منسدلة للقراءة فقط
    cb = ttk.Combobox(p, state="readonly", width=w, values=vals)
    cb.grid(row=r, column=c, padx=8, pady=3)
    if cmd: cb.bind("<<ComboboxSelected>>", cmd)
    return cb


def tree(p, cols, widths, h=8):  # إنشاء جدول عرض بيانات مع شريط تمرير
    frame = tk.Frame(p, bg=CARD_BG)
    frame.pack(fill="both", expand=True, padx=8, pady=4)
    t = ttk.Treeview(frame, columns=cols, show="headings", height=h)
    sb = ttk.Scrollbar(frame, orient="vertical", command=t.yview)
    t.configure(yscrollcommand=sb.set)
    for col, w in zip(cols, widths):
        t.heading(col, text=col)
        t.column(col, width=w, anchor="center")
    t.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return t


def warn(m):
    messagebox.showwarning("⚠️ Warning", m)


def _is_valid_name(name):
    """التحقق من أن الاسم يحتوي فقط على حروف (عربية/إنجليزية) ومسافات — بدون أرقام أو رموز"""
    return bool(re.match(r'^[a-zA-Z\u0600-\u06FF\s]+$', name))


# ══════════════════════════════════════════
#   التطبيق الرئيسي — تبويبات علوية مركزية
# ══════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🫅ChampionTrack")
        self.geometry("980x760")   # حجم النافذة الابتدائي
        self.minsize(920, 700)     # الحد الأدنى لحجم النافذة
        self.configure(bg=SNOW)    # لون الخلفية الأساسي
        self.d = load()            # تحميل جميع البيانات عند بدء التشغيل
        self._theme()
        self._build_layout()
        self._tab_val()
        self._upd_val()

    # ─── تطبيق السمة الاحترافية الأحمر والأبيض على جميع العناصر ───
    def _theme(self):
        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure(".", background=CARD_BG, foreground=TXT_DARK, fieldbackground=INPUT_BG,
                     borderwidth=0, font=("Segoe UI", 10))
        s.configure("TFrame", background=CARD_BG)
        s.configure("TLabel", background=CARD_BG, foreground=TXT_DARK)
        s.configure("TLabelframe", background=CARD_BG, foreground=RED_MAIN,
                     bordercolor=CARD_BD, relief="groove", borderwidth=2)
        s.configure("TLabelframe.Label", background=CARD_BG, foreground=RED_MAIN,
                     font=("Segoe UI", 11, "bold"))

        # زر رئيسي أحمر
        s.configure("TButton", background=RED_MAIN, foreground="#FFF",
                     padding=[12, 6], font=("Segoe UI", 10, "bold"))
        s.map("TButton", background=[("active", RED_BRIGHT)])

        # زر ثانوي رمادي
        s.configure("Alt.TButton", background="#607D8B", foreground="#FFF",
                     padding=[12, 6], font=("Segoe UI", 10, "bold"))
        s.map("Alt.TButton", background=[("active", "#455A64")])

        # زر حذف
        s.configure("Danger.TButton", background="#D32F2F", foreground="#FFF",
                     padding=[12, 6], font=("Segoe UI", 10, "bold"))
        s.map("Danger.TButton", background=[("active", "#B71C1C")])

        s.configure("TEntry", fieldbackground=INPUT_BG, foreground=TXT_DARK,
                     insertcolor=RED_MAIN, bordercolor=INPUT_BD)

        # إصلاح القوائم المنسدلة
        s.configure("TCombobox", fieldbackground=INPUT_BG, foreground=TXT_DARK,
                     selectbackground=RED_MAIN, selectforeground="#fff",
                     background=INPUT_BG, bordercolor=INPUT_BD, arrowcolor=RED_MAIN)
        s.map("TCombobox",
              fieldbackground=[("readonly", INPUT_BG), ("readonly", "focus", INPUT_BG),
                               ("readonly", "active", INPUT_BG), ("disabled", CARD_BD)],
              foreground=[("readonly", TXT_DARK), ("readonly", "focus", TXT_DARK),
                          ("readonly", "active", TXT_DARK), ("disabled", TXT_LIGHT)],
              selectbackground=[("readonly", RED_MAIN), ("readonly", "focus", RED_MAIN)],
              selectforeground=[("readonly", "#fff"), ("readonly", "focus", "#fff")],
              background=[("readonly", INPUT_BG), ("readonly", "focus", INPUT_BG)])
        self.option_add("*TCombobox*Listbox.background", INPUT_BG)
        self.option_add("*TCombobox*Listbox.foreground", TXT_DARK)
        self.option_add("*TCombobox*Listbox.selectBackground", RED_MAIN)
        self.option_add("*TCombobox*Listbox.selectForeground", "#fff")

        # جدول العرض
        s.configure("Treeview", background="#FFFFFF", foreground=TXT_DARK,
                     fieldbackground="#FFFFFF", rowheight=30, borderwidth=0,
                     font=("Segoe UI", 10))
        s.configure("Treeview.Heading", background=RED_MAIN, foreground="#FFF",
                     font=("Segoe UI", 10, "bold"), relief="flat")
        s.map("Treeview", background=[("selected", RED_LIGHT)],
              foreground=[("selected", RED_DARK)])

        s.configure("Vertical.TScrollbar", background=CARD_BD, troughcolor=INPUT_BG,
                     arrowcolor=RED_MAIN)

    # ─── بناء التخطيط الرئيسي: شريط علوي بالتبويبات + منطقة محتوى قابلة للتمرير ───
    def _build_layout(self):
        # ══ الشريط العلوي: يحتوي على عنوان التطبيق + أزرار التبويبات في المنتصف ══
        top_bar = tk.Frame(self, bg=TAB_BG, height=100)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        # صف العنوان
        title_row = tk.Frame(top_bar, bg=TAB_BG)
        title_row.pack(fill="x", pady=(8, 0))
        tk.Label(title_row, text="🧑‍🎓", font=("Segoe UI Emoji", 20),
                 bg=TAB_BG, fg="#FFD700").pack(side="left", padx=(20, 6))
        tk.Label(title_row, text="Campus Event Ranking System",
                 font=("Segoe UI", 15, "bold"), bg=TAB_BG, fg="#FFFFFF").pack(side="left")

        # صف التبويبات — في المنتصف
        tabs_row = tk.Frame(top_bar, bg=TAB_BG)
        tabs_row.pack(expand=True)

        self.tab_buttons = []
        tabs = [("📜", "Registration"), ("📅", "Events"),
                ("🎯", "Scoring"), ("🥇", "Leaderboard")]

        for i, (icon, name) in enumerate(tabs):
            btn = tk.Frame(tabs_row, bg=TAB_BG, cursor="hand2", padx=2, pady=2)
            btn.pack(side="left", padx=6)

            inner = tk.Frame(btn, bg=TAB_BG, padx=14, pady=5)
            inner.pack()

            ic = tk.Label(inner, text=icon, font=("Segoe UI Emoji", 12),
                          bg=TAB_BG, fg="#FFD5D5")
            ic.pack(side="left", padx=(0, 5))

            tx = tk.Label(inner, text=name, font=("Segoe UI", 11),
                          bg=TAB_BG, fg="#FFD5D5")
            tx.pack(side="left")

            # مؤشر سفلي — شريط أحمر مشرق تحت التبويب النشط
            indicator = tk.Frame(btn, bg=TAB_BG, height=3)
            indicator.pack(fill="x", side="bottom")

            for widget in [btn, inner, ic, tx]:
                widget.bind("<Button-1>", lambda e, idx=i: self._switch_tab(idx))
                widget.bind("<Enter>", lambda e, b=btn, inn=inner, _ic=ic, _tx=tx:
                            self._tab_hover(b, inn, _ic, _tx, True))
                widget.bind("<Leave>", lambda e, b=btn, inn=inner, _ic=ic, _tx=tx, idx=i:
                            self._tab_hover(b, inn, _ic, _tx, False, idx))

            self.tab_buttons.append((btn, inner, ic, tx, indicator))

        # ══ منطقة المحتوى الرئيسية — كانفاس قابل للتمرير يحتوي صفحات التبويبات ══
        content_wrapper = tk.Frame(self, bg=SNOW)
        content_wrapper.pack(fill="both", expand=True)

        self.cv_scroll = tk.Canvas(content_wrapper, bg=SNOW, highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(content_wrapper, orient="vertical",
                                        command=self.cv_scroll.yview)
        self.cv_scroll.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.cv_scroll.pack(side="left", fill="both", expand=True)

        self.scroll_frame = tk.Frame(self.cv_scroll, bg=SNOW)
        self.cv_scroll.create_window((0, 0), window=self.scroll_frame, anchor="nw", tags="sw")
        self.scroll_frame.bind("<Configure>",
                               lambda e: self.cv_scroll.configure(scrollregion=self.cv_scroll.bbox("all")))
        self.cv_scroll.bind("<Configure>",
                            lambda e: self.cv_scroll.itemconfig("sw", width=e.width))
        self.cv_scroll.bind_all("<MouseWheel>",
                                lambda e: self.cv_scroll.yview_scroll(-1*(e.delta//120), "units"))

        # بناء صفحات التبويبات الأربع
        self.pages = []
        self._tab_reg()
        self._tab_ev()
        self._tab_sc()
        self._tab_lb()

        self.current_tab = -1
        self._switch_tab(0)

    def _tab_hover(self, btn, inner, ic, tx, entering, idx=None):  # تأثير hover عند مرور الماوس
        if entering:
            c = TAB_HOVER
        elif idx is not None and idx == self.current_tab:
            c = TAB_ACTIVE
        else:
            c = TAB_BG
        for w in [btn, inner, ic, tx]:
            w.configure(bg=c)

    def _switch_tab(self, idx):  # تبديل التبويب النشط وتحديث المظهر
        if idx == self.current_tab:
            return
        self.current_tab = idx

        for i, (btn, inner, ic, tx, indicator) in enumerate(self.tab_buttons):
            if i == idx:
                for w in [btn, inner, ic, tx]:
                    w.configure(bg=TAB_ACTIVE)
                tx.configure(font=("Segoe UI", 11, "bold"), fg="#FFFFFF")
                ic.configure(fg="#FFFFFF")
                indicator.configure(bg="#FFD700")  # شريط ذهبي تحت التبويب النشط
            else:
                for w in [btn, inner, ic, tx]:
                    w.configure(bg=TAB_BG)
                tx.configure(font=("Segoe UI", 11), fg="#FFD5D5")
                ic.configure(fg="#FFD5D5")
                indicator.configure(bg=TAB_BG)

        for page in self.pages:
            page.pack_forget()
        self.pages[idx].pack(fill="both", expand=True, padx=24, pady=16)
        self.cv_scroll.yview_moveto(0)

    # ─── إنشاء بطاقة (كارد) بإطار وعنوان — تُستخدم لتجميع عناصر كل قسم ───
    def _card(self, parent, title="", icon=""):
        outer = tk.Frame(parent, bg=CARD_BD, bd=0)
        outer.pack(fill="x", padx=4, pady=6)
        card = tk.Frame(outer, bg=CARD_BG, bd=0, padx=16, pady=12)
        card.pack(fill="x", padx=1, pady=1)
        if title:
            hdr = tk.Frame(card, bg=CARD_BG)
            hdr.pack(fill="x", pady=(0, 8))
            if icon:
                tk.Label(hdr, text=icon, font=("Segoe UI Emoji", 13),
                         bg=CARD_BG, fg=RED_MAIN).pack(side="left", padx=(0, 6))
            tk.Label(hdr, text=title, font=("Segoe UI", 12, "bold"),
                     bg=CARD_BG, fg=RED_DARK).pack(side="left")
            tk.Frame(card, bg=RED_LIGHT, height=2).pack(fill="x", pady=(0, 8))
        return card

    # ─── دوال مساعدة مشتركة بين كل الصفحات ───
    def _sv(self):
        save(self.d); self._upd_val()  # حفظ البيانات + تحديث لوحة التحقق

    def _ec(self, n):  # حساب عدد الأحداث التي شارك فيها المشارك
        return sum(1 for s in self.d["scores"] if s["participant"] == n)

    def _rename(self, o, n):  # تحديث اسم المشارك في كل النتائج
        for s in self.d["scores"]:
            if s["participant"] == o: s["participant"] = n

    def _drop(self, n):  # حذف كل نتائج المشارك عند حذفه
        self.d["scores"] = [s for s in self.d["scores"] if s["participant"] != n]

    # ══════════ صفحة 1: التسجيل ══════════
    def _tab_reg(self):
        # إنشاء صفحة التسجيل وإضافتها لقائمة الصفحات
        page = tk.Frame(self.scroll_frame, bg=SNOW)
        self.pages.append(page)

        # بطاقة تسجيل الفرق مع عداد يعرض العدد الحالي
        tf = self._card(page, "Team Registration", "🏅")
        self.t_cnt = tk.StringVar()
        tk.Label(tf, textvariable=self.t_cnt, font=("Segoe UI", 10, "bold"),
                 bg=CARD_BG, fg=RED_MAIN).pack(anchor="w")

        grid = tk.Frame(tf, bg=CARD_BG)
        grid.pack(fill="x", pady=4)
        lbl(grid, "Team Name:", 0, 0)
        self.t_nm = tk.StringVar()
        ent(grid, self.t_nm, 0, 1)
        self.t_cb = cmb(grid, 0, 2, cmd=self._ld_team)

        # إنشاء 5 حقول أعضاء بحلقة تكرار لتقليل الكود
        self.mvs = []
        for i in range(MAX_M):
            lbl(grid, f"Member {i+1}:", 1+i, 0)
            v = tk.StringVar(); ent(grid, v, 1+i, 1); self.mvs.append(v)

        bf = tk.Frame(tf, bg=CARD_BG); bf.pack(pady=8)
        ttk.Button(bf, text="➕ Add", command=self._add_t).pack(side="left", padx=4)
        ttk.Button(bf, text="✏️ Update", command=self._upd_t, style="Alt.TButton").pack(side="left", padx=4)
        ttk.Button(bf, text="🗑️ Delete", command=self._del_t, style="Danger.TButton").pack(side="left", padx=4)

        # بطاقة تسجيل الأفراد مع عداد مباشر
        nf = self._card(page, "Individual Registration", "👤")
        self.i_cnt = tk.StringVar()
        tk.Label(nf, textvariable=self.i_cnt, font=("Segoe UI", 10, "bold"),
                 bg=CARD_BG, fg=RED_MAIN).pack(anchor="w")

        g2 = tk.Frame(nf, bg=CARD_BG); g2.pack(fill="x", pady=4)
        lbl(g2, "Name:", 0, 0)
        self.i_nm = tk.StringVar(); ent(g2, self.i_nm, 0, 1)
        self.i_cb = cmb(g2, 0, 2, cmd=lambda e: self.i_nm.set(self.i_cb.get()))

        bf2 = tk.Frame(nf, bg=CARD_BG); bf2.pack(pady=8)
        ttk.Button(bf2, text="➕ Add", command=self._add_i).pack(side="left", padx=4)
        ttk.Button(bf2, text="✏️ Update", command=self._upd_i, style="Alt.TButton").pack(side="left", padx=4)
        ttk.Button(bf2, text="🗑️ Delete", command=self._del_i, style="Danger.TButton").pack(side="left", padx=4)

        # منطقة نصية للقراءة فقط تعرض جميع المسجلين
        ic = self._card(page, "Registered Participants", "📄")
        self.rtx = tk.Text(ic, height=6, state="disabled", wrap="word",
                           bg=INPUT_BG, fg=TXT_DARK, font=("Consolas", 10),
                           relief="flat", bd=0, padx=10, pady=8)
        self.rtx.pack(fill="both", expand=True)
        self._rfr()  # تحديث العرض مباشرة عند بناء الصفحة

    def _rfr(self):
        # تحديث العدادات والقوائم المنسدلة ومنطقة العرض النصية
        ts, ins = self.d["teams"], self.d["individuals"]
        self.t_cnt.set(f"Teams: {len(ts)}/{MAX_T}")
        self.i_cnt.set(f"Individuals: {len(ins)}/{MAX_I}")
        self.t_cb["values"] = list(ts.keys())
        self.i_cb["values"] = ins[:]
        self.rtx.config(state="normal"); self.rtx.delete("1.0", "end")
        for t, m in ts.items(): self.rtx.insert("end", f"👯‍♂️ [Team] {t}:  {', '.join(m)}\n")
        for i in ins: self.rtx.insert("end", f"🧑 [Individual] {i}\n")
        self.rtx.config(state="disabled")

    def _clr_t(self):
        # مسح جميع حقول الفريق بعد كل عملية إضافة/تعديل/حذف
        self.t_nm.set("")
        for v in self.mvs: v.set("")
        self.t_cb.set("")

    def _ld_team(self, _e=None):
        # عند اختيار فريق من القائمة المنسدلة، تحميل بياناته في الحقول
        n = self.t_cb.get()
        if n in self.d["teams"]:
            self.t_nm.set(n)
            for i, v in enumerate(self.mvs):
                v.set(self.d["teams"][n][i] if i < len(self.d["teams"][n]) else "")

    def _get_mems(self): return [v.get().strip() for v in self.mvs]

    def _add_t(self):
        # إضافة فريق جديد بعد التحقق من الحقول والحدود والتكرار
        nm, ms = self.t_nm.get().strip(), self._get_mems()
        if not nm or any(not m for m in ms): return warn("Fill team name and all 5 members.")
        if len(self.d["teams"]) >= MAX_T: return warn("Maximum 4 teams reached.")
        if nm in self.d["teams"]: return warn("Team name already exists.")
        if len(set(ms)) != MAX_M: return warn("Duplicate member names.")
        # التحقق من أن أسماء الأعضاء لا تحتوي على أرقام أو رموز
        invalid = [m for m in ms if not _is_valid_name(m)]
        if invalid: return warn(f"Member names must contain only letters and spaces.\nInvalid: {', '.join(invalid)}")
        self.d["teams"][nm] = ms; self._sv(); self._clr_t(); self._rfr()

    def _upd_t(self):
        # تعديل بيانات الفريق المحدد، مع تحديث الاسم في النتائج إذا تغيّر
        sel, nm, ms = self.t_cb.get(), self.t_nm.get().strip(), self._get_mems()
        if not sel or not nm or any(not m for m in ms): return warn("Select a team and fill all fields.")
        if nm != sel and nm in self.d["teams"]: return warn("Team name already exists.")
        if len(set(ms)) != MAX_M: return warn("Duplicate member names.")
        # التحقق من أن أسماء الأعضاء لا تحتوي على أرقام أو رموز
        invalid = [m for m in ms if not _is_valid_name(m)]
        if invalid: return warn(f"Member names must contain only letters and spaces.\nInvalid: {', '.join(invalid)}")
        if nm != sel: self._rename(sel, nm); del self.d["teams"][sel]
        self.d["teams"][nm] = ms; self._sv(); self._clr_t(); self._rfr()

    def _del_t(self):
        # حذف الفريق المحدد مع إزالة كل نتائجه من السجل
        sel = self.t_cb.get()
        if sel: self.d["teams"].pop(sel, None); self._drop(sel); self._sv(); self._clr_t(); self._rfr()

    def _add_i(self):
        # إضافة فرد جديد بعد التأكد من عدم تجاوز الحد وعدم التكرار
        nm = self.i_nm.get().strip()
        if not nm: return warn("Enter a name.")
        # التحقق من أن اسم الفرد لا يحتوي على أرقام أو رموز
        if not _is_valid_name(nm): return warn("Name must contain only letters and spaces.\nNumbers and symbols are not allowed.")
        if len(self.d["individuals"]) >= MAX_I: return warn("Maximum 20 individuals reached.")
        if nm in self.d["individuals"]: return warn("Name already exists.")
        self.d["individuals"].append(nm); self._sv(); self.i_nm.set(""); self._rfr()

    def _upd_i(self):
        # تعديل اسم الفرد المحدد مع تحديث الاسم في جميع النتائج المرتبطة
        sel, nw = self.i_cb.get(), self.i_nm.get().strip()
        if not sel or not nw: return warn("Select an individual and enter a name.")
        # التحقق من أن اسم الفرد لا يحتوي على أرقام أو رموز
        if not _is_valid_name(nw): return warn("Name must contain only letters and spaces.\nNumbers and symbols are not allowed.")
        if nw != sel and nw in self.d["individuals"]: return warn("Name already exists.")
        self.d["individuals"][self.d["individuals"].index(sel)] = nw
        self._rename(sel, nw); self._sv(); self.i_nm.set(""); self.i_cb.set(""); self._rfr()

    def _del_i(self):
        # حذف الفرد المحدد مع إزالة كل نتائجه
        sel = self.i_cb.get()
        if sel and sel in self.d["individuals"]:
            self.d["individuals"].remove(sel); self._drop(sel)
            self._sv(); self.i_nm.set(""); self.i_cb.set(""); self._rfr()

    # ══════════ صفحة 2: الأحداث ══════════
    def _tab_ev(self):
        page = tk.Frame(self.scroll_frame, bg=SNOW)
        self.pages.append(page)

        # جدول عرض جميع الأحداث المحمّلة
        tc = self._card(page, "Event List", "📋")
        self.ev_tr = tree(tc, ("Name", "Type", "Category"), (260, 160, 160), 10)

        # بطاقة تعديل الحدث: اختيار حدث ثم تعديل اسمه ونوعه وتصنيفه
        ec = self._card(page, "Edit Event", "✏️")
        grid = tk.Frame(ec, bg=CARD_BG); grid.pack(fill="x", pady=4)
        lbl(grid, "Select:", 0, 0); self.ev_s = cmb(grid, 0, 1, 22, cmd=self._ld_ev)
        lbl(grid, "Name:", 0, 2); self.ev_n = tk.StringVar(); ent(grid, self.ev_n, 0, 3, 18)
        lbl(grid, "Type:", 1, 0); self.ev_t = tk.StringVar()
        c1 = cmb(grid, 1, 1, 14, ["Team", "Individual"]); c1.configure(textvariable=self.ev_t)
        lbl(grid, "Category:", 1, 2); self.ev_c = tk.StringVar()
        # تصحيح القائمة المنسدلة للفئات
        c2 = cmb(grid, 1, 3, 14, ["Academic", "Athletic", "E-Sports", "Arts", "Technology", "Community Service", "Life Skills"])
        c2.configure(textvariable=self.ev_c)
        ttk.Button(ec, text="💾 Save Changes", command=self._sv_ev).pack(pady=8)
        self._rfr_ev()

    def _rfr_ev(self):
        # مسح الجدول وإعادة تعبئته بكل الأحداث + تحديث القائمة المنسدلة
        for r in self.ev_tr.get_children(): self.ev_tr.delete(r)
        ns = [ev["name"] for ev in self.d["events"]]
        for ev in self.d["events"]:
            self.ev_tr.insert("", "end", values=(ev["name"], ev["type"], ev["category"]))
        self.ev_s["values"] = ns

    def _ld_ev(self, _e=None):
        # عند اختيار حدث، تحميل بياناته في حقول التعديل
        ev = next((e for e in self.d["events"] if e["name"] == self.ev_s.get()), None)
        if ev: self.ev_n.set(ev["name"]); self.ev_t.set(ev["type"]); self.ev_c.set(ev["category"])

    def _sv_ev(self):
        # حفظ التعديلات على الحدث مع تحديث اسمه في النتائج إذا تغيّر
        sel, nn, nt, nc = self.ev_s.get(), self.ev_n.get().strip(), self.ev_t.get(), self.ev_c.get()
        if not all([sel, nn, nt, nc]): return warn("Select an event and fill all fields.")
        for ev in self.d["events"]:
            if ev["name"] == sel:
                if nn != sel:
                    for s in self.d["scores"]:
                        if s["event"] == sel: s["event"] = nn
                ev.update(name=nn, type=nt, category=nc); break
        self._sv(); self._rfr_ev()

    # ══════════ صفحة 3: النقاط ══════════
    def _tab_sc(self):
        page = tk.Frame(self.scroll_frame, bg=SNOW)
        self.pages.append(page)

        # بطاقة إعداد النقاط: 5 حقول لنقاط المراتب الخمس
        pc = self._card(page, "Points Configuration (Rank 1–5)", "⚙️")
        pgrid = tk.Frame(pc, bg=CARD_BG); pgrid.pack(fill="x", pady=4)
        self.pvs = []
        for i in range(MAX_M):
            lbl(pgrid, f"Rank {i+1}:", 0, i*2)
            v = tk.StringVar(value=str(self.d["points"][i]))
            ent(pgrid, v, 0, i*2+1, 5); self.pvs.append(v)
        ttk.Button(pc, text="💾 Save Points", command=self._sv_pts).pack(pady=8)

        sc = self._card(page, "Submit Score", "🎯")
        sgrid = tk.Frame(sc, bg=CARD_BG); sgrid.pack(fill="x", pady=4)
        lbl(sgrid, "Event:", 0, 0); self.s_ev = cmb(sgrid, 0, 1, 22, cmd=self._on_sev)
        lbl(sgrid, "Participant:", 1, 0); self.s_pt = cmb(sgrid, 1, 1, 22, cmd=self._on_spt)
        self.cmp = tk.StringVar(value="Completed: —/5")
        tk.Label(sgrid, textvariable=self.cmp, font=("Segoe UI", 10, "italic"),
                 bg=CARD_BG, fg=RED_ACCENT).grid(row=1, column=2, padx=8)
        lbl(sgrid, "Rank:", 2, 0); self.s_rk = cmb(sgrid, 2, 1, 6, [str(i) for i in range(1, 6)])
        ttk.Button(sc, text="📝 Submit Score", command=self._submit).pack(pady=8)
        self._rfr_sc()

    def _rfr_sc(self):
        self.s_ev["values"] = [e["name"] for e in self.d["events"]]

    def _on_sev(self, _e=None):
        # عند اختيار حدث، فلترة قائمة المشاركين حسب نوعه (فريق/فرد)
        ev = next((e for e in self.d["events"] if e["name"] == self.s_ev.get()), None)
        if not ev: return
        self.s_pt["values"] = list(self.d["teams"].keys()) if ev["type"] == "Team" else self.d["individuals"][:]
        self.s_pt.set(""); self.cmp.set("Completed: —/5")

    def _on_spt(self, _e=None):
        # عرض عدد الأحداث المكتملة للمشارك المحدد
        p = self.s_pt.get()
        if p: self.cmp.set(f"Completed: {self._ec(p)}/{MAX_EV}")

    def _sv_pts(self):
        # حفظ نقاط المراتب بعد التأكد أنها أرقام صحيحة
        try: self.d["points"] = [int(v.get()) for v in self.pvs]
        except ValueError: return warn("Points must be integers.")
        self._sv(); messagebox.showinfo("✅ Info", "Points saved.")

    def _submit(self):
        # تسجيل نتيجة جديدة بعد التحقق من عدم التكرار وعدم تجاوز الحد
        ev, pt, rk = self.s_ev.get(), self.s_pt.get(), self.s_rk.get()
        if not all([ev, pt, rk]): return warn("Select event, participant and rank.")
        if self._ec(pt) >= MAX_EV: return warn(f"{pt} already completed {MAX_EV} events.")
        if any(s["event"] == ev and s["participant"] == pt for s in self.d["scores"]):
            return warn(f"{pt} already scored in {ev}.")
        ps = self.d["points"][int(rk)-1]  # جلب النقاط حسب المرتبة
        self.d["scores"].append({"event": ev, "participant": pt, "rank": int(rk), "points": ps})
        self._sv(); self._on_spt()
        messagebox.showinfo("🥇 Score", f"{pt} → Rank {rk} ({ps} pts)")

    # ══════════ صفحة 4: المتصدرون ══════════
    def _tab_lb(self):
        page = tk.Frame(self.scroll_frame, bg=SNOW)
        self.pages.append(page)
        cols, ws = ("#", "Name", "Events", "Points"), (50, 240, 100, 100)

        # جدول ترتيب الفرق مع تمييز المركز الأول بلون ذهبي
        tc1 = self._card(page, "Teams Ranking", "🏆")
        self.t_lb = tree(tc1, cols, ws, 5)
        self.t_lb.tag_configure("gold", background=GOLD_LIGHT, foreground=RED_DARK)

        # جدول ترتيب الأفراد بنفس التنسيق
        tc2 = self._card(page, "Individuals Ranking", "🏅")
        self.i_lb = tree(tc2, cols, ws, 7)
        self.i_lb.tag_configure("gold", background=GOLD_LIGHT, foreground=RED_DARK)

        ttk.Button(page, text="🔄 Refresh", command=self._rfr_lb).pack(pady=8)

    def _rfr_lb(self):
        # حساب مجموع النقاط لكل مشارك وترتيبهم تنازلياً مع تمييز الأول
        def fill(tr, names):
            for r in tr.get_children(): tr.delete(r)
            st = sorted([(n, self._ec(n),
                          sum(s["points"] for s in self.d["scores"] if s["participant"] == n))
                         for n in names], key=lambda x: x[2], reverse=True)
            for i, (n, c, t) in enumerate(st, 1):
                tr.insert("", "end", values=(i, n, c, t), tags=("gold",) if i == 1 else ())
        fill(self.t_lb, self.d["teams"].keys())
        fill(self.i_lb, self.d["individuals"])

    # ══════════ لوحة التحقق السفلية ══════════
    def _tab_val(self):
        # إنشاء لوحة التحقق السفلية: 6 تسميات موزعة على صفين (3 في كل صف)
        vf_out = tk.Frame(self, bg=CARD_BD)
        vf_out.pack(fill="x", padx=10, pady=(0, 8), side="bottom")
        vf = tk.Frame(vf_out, bg=CARD_BG, padx=12, pady=8)
        vf.pack(fill="x", padx=1, pady=1)
        tk.Label(vf, text="✅ Validation Status", font=("Segoe UI", 11, "bold"),
                 bg=CARD_BG, fg=RED_DARK).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 4))
        self.vvs = [tk.StringVar() for _ in range(6)]
        for i, v in enumerate(self.vvs):
            tk.Label(vf, textvariable=v, font=("Consolas", 10),
                     bg=CARD_BG, fg=TXT_DARK).grid(row=1+i//3, column=i%3, sticky="w", padx=14, pady=2)

    def _upd_val(self):
        """التحقق — فحص 6 قيود وعرض حالة كل منها"""
        ts, ins = self.d["teams"], self.d["individuals"]
        # القيد 1: هل توجد أسماء أفراد مكررة في القائمة؟
        if len(set(ins)) != len(ins):
            self.vvs[0].set("❌  Duplicate individual names detected!")
        else:
            self.vvs[0].set("✅  No duplicate individual names")
        # القيد 2: هل تجاوز عدد الفرق الحد الأقصى المسموح؟
        if len(ts) > MAX_T:
            self.vvs[1].set(f"❌  Teams exceed limit ({len(ts)}/{MAX_T})")
        else:
            self.vvs[1].set(f"✅  Teams within limit ({len(ts)}/{MAX_T})")
        # القيد 3: هل يوجد مشارك سجل في أكثر من 5 أحداث؟
        over = [p for p in list(ts.keys()) + ins if self._ec(p) > MAX_EV]
        if over:
            self.vvs[2].set(f"❌  Exceeding 5 events: {', '.join(over)}")
        else:
            self.vvs[2].set("✅  No participant exceeds 5 events")
        # القيد 4: هل عدد الأفراد المسجلين تخطى الحد المسموح 20؟
        if len(ins) > MAX_I:
            self.vvs[3].set(f"❌  Individuals exceed limit ({len(ins)}/{MAX_I})")
        else:
            self.vvs[3].set(f"✅  Individuals within limit ({len(ins)}/{MAX_I})")
        # القيد 5: هل يوجد فريق لا يحتوي على 5 أعضاء بالضبط؟
        bad = [t for t, m in ts.items() if len(m) != MAX_M]
        if bad:
            self.vvs[4].set(f"❌  Teams without {MAX_M} members: {', '.join(bad)}")
        else:
            self.vvs[4].set(f"✅  All teams have exactly {MAX_M} members")
        # القيد 6: هل توجد أسماء فرق مكررة في السجل؟
        if len(set(ts.keys())) != len(ts):
            self.vvs[5].set("❌  Duplicate team names found!")
        else:
            self.vvs[5].set("✅  No duplicate team names")


# ─── نقطة الدخول ───
if __name__ == "__main__":
    App().mainloop()