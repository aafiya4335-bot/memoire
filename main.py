
import flet as ft
import json, os, shutil, datetime

DATA_FILE = "memories.json"
USER_FILE = "user.json"
ASSETS_DIR = "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

MOODS = ["😊 Happy", "❤️ Love", "😂 Funny", "🥺 Emotional", "🌟 Special", "😌 Calm"]

def load_memories():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_memories(memories):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, indent=2, ensure_ascii=False)

def load_user():
    if not os.path.exists(USER_FILE):
        return None
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def save_user(user):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(user, f, indent=2, ensure_ascii=False)

def main(page: ft.Page):
    page.title = "Memoire"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F0A1E"
    page.window_width = 400
    page.window_height = 800
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    memories = load_memories()
    user = load_user()
    state = {"photo_path": None, "filter_mood": "All", "search": "", "profile_photo": None}

    def on_this_day():
        today = datetime.date.today()
        result = []
        for m in memories:
            try:
                d = datetime.date.fromisoformat(m["date"])
                if d.day == today.day and d.month == today.month and d.year != today.year:
                    years = today.year - d.year
                    result.append((years, m))
            except: pass
        return result

    def delete_memory(idx):
        memories.pop(idx)
        save_memories(memories)
        refresh_home()

    # ---------- SETUP - FIRST TIME (Create Own PIN + Profile) ----------
    setup_name = ft.TextField(label="Your Name", hint_text="e.g. Afiya", bgcolor="#1E1B33", border_radius=12)
    setup_pin = ft.TextField(label="Create 4-digit PIN", hint_text="e.g. 2580", password=True, max_length=4, keyboard_type=ft.KeyboardType.NUMBER, bgcolor="#1E1B33", border_radius=12)
    setup_confirm = ft.TextField(label="Confirm PIN", hint_text="Type same PIN again", password=True, max_length=4, keyboard_type=ft.KeyboardType.NUMBER, bgcolor="#1E1B33", border_radius=12)
    setup_error = ft.Text("", color="red", size=12)

    def create_account(e):
        nonlocal user
        if not setup_name.value or len(setup_name.value.strip()) < 2:
            setup_error.value = "Please enter your name"; page.update(); return
        if not setup_pin.value or len(setup_pin.value) != 4 or not setup_pin.value.isdigit():
            setup_error.value = "PIN must be 4 numbers"; page.update(); return
        if setup_pin.value != setup_confirm.value:
            setup_error.value = "PINs don't match! Type same PIN twice"; page.update(); return
        user = {"name": setup_name.value.strip(), "pin": setup_pin.value, "photo": "", "created": datetime.date.today().isoformat()}
        save_user(user)
        show_lock()

    def show_setup():
        page.clean()
        page.floating_action_button = None
        page.add(ft.Container(content=ft.Column([
            ft.Container(height=30),
            ft.Text("🧠", size=55, text_align=ft.TextAlign.CENTER),
            ft.Text("Welcome to Memoire", size=26, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text("Create your private account", size=14, color="#C084FC", text_align=ft.TextAlign.CENTER),
            ft.Container(height=10),
            ft.Container(content=ft.Column([setup_name, setup_pin, setup_confirm, setup_error,
                ft.ElevatedButton("Create My Locker 🔒", on_click=create_account, bgcolor="#9333EA", color="white", height=48)],
                spacing=12), padding=20, bgcolor="#1E1B33", border_radius=20, margin=10),
            ft.Text("Your PIN is saved only on YOUR phone.\nNobody else can open your memories.", size=11, color="grey", text_align=ft.TextAlign.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=10))

    # ---------- LOCK SCREEN (Uses YOUR PIN) ----------
    pin_input = ft.TextField(password=True, can_reveal_password=False, hint_text="Enter YOUR PIN", text_align=ft.TextAlign.CENTER, width=200, max_length=4, keyboard_type=ft.KeyboardType.NUMBER, border_color="#C084FC")
    pin_error = ft.Text("", color="red", size=12)
    lock_name = ft.Text("", size=15, color="#C084FC", text_align=ft.TextAlign.CENTER)

    def check_pin(e):
        if user and pin_input.value == user["pin"]:
            show_home()
        else:
            pin_error.value = "Wrong PIN! This is your personal PIN."
            page.update()

    def show_lock():
        nonlocal pin_error, pin_input
        pin_input.value = ""
        pin_error.value = ""
        lock_name.value = f"Hi {user['name']} 👋" if user else ""
        page.clean()
        page.floating_action_button = None
        page.add(ft.Column([
            ft.Container(height=60),
            ft.Text("🧠", size=60, text_align=ft.TextAlign.CENTER),
            ft.Text("Memoire", size=38, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text("Your Memory Locker", size=15, color="#C084FC", text_align=ft.TextAlign.CENTER),
            lock_name,
            ft.Container(height=20),
            ft.Container(content=ft.Column([ft.Text("🔒 Private Vault", size=16, weight=ft.FontWeight.BOLD), pin_input, pin_error,
                ft.ElevatedButton("Unlock My Memories", on_click=check_pin, bgcolor="#9333EA", color="white", width=200, height=45)],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12), padding=20, bgcolor="#1E1B33", border_radius=20, margin=20),
            ft.Text("Your PIN is personal to you", size=11, color="grey", text_align=ft.TextAlign.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))

    # ---------- PROFILE SCREEN ----------
    profile_name_field = ft.TextField(label="Your Name", bgcolor="#1E1B33", border_radius=12)
    old_pin_field = ft.TextField(label="Old PIN", password=True, max_length=4, keyboard_type=ft.KeyboardType.NUMBER, bgcolor="#1E1B33", border_radius=12)
    new_pin_field = ft.TextField(label="New PIN", password=True, max_length=4, keyboard_type=ft.KeyboardType.NUMBER, bgcolor="#1E1B33", border_radius=12)
    profile_msg = ft.Text("", size=12, color="#FDE68A")

    def save_profile(e):
        nonlocal user
        if profile_name_field.value.strip():
            user["name"] = profile_name_field.value.strip()
        if old_pin_field.value or new_pin_field.value:
            if old_pin_field.value != user["pin"]:
                profile_msg.value = "Old PIN is wrong!"; profile_msg.color = "red"; page.update(); return
            if len(new_pin_field.value) != 4 or not new_pin_field.value.isdigit():
                profile_msg.value = "New PIN must be 4 numbers"; profile_msg.color = "red"; page.update(); return
            user["pin"] = new_pin_field.value
            profile_msg.value = "PIN changed successfully ✅"; profile_msg.color = "#4ADE80"
        else:
            profile_msg.value = "Profile saved ✅"; profile_msg.color = "#4ADE80"
        save_user(user)
        page.update()

    def show_profile():
        profile_name_field.value = user["name"] if user else ""
        old_pin_field.value = ""; new_pin_field.value = ""; profile_msg.value = ""
        total = len(memories)
        page.clean()
        page.floating_action_button = None
        page.add(ft.Container(content=ft.Column([
            ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_home()), ft.Text("My Account", size=22, weight=ft.FontWeight.BOLD)]),
            ft.Container(content=ft.Column([
                ft.Text("👤", size=50, text_align=ft.TextAlign.CENTER),
                ft.Text(user["name"] if user else "", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text(f"Member since {user.get('created','')}", color="grey", size=12, text_align=ft.TextAlign.CENTER),
                ft.Row([ft.Container(content=ft.Column([ft.Text(str(total), size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER), ft.Text("Memories", size=11, color="grey", text_align=ft.TextAlign.CENTER)]), bgcolor="#0F0A1E", padding=12, border_radius=12, expand=True),
                        ft.Container(content=ft.Column([ft.Text(str(len(on_this_day())), size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER), ft.Text("On This Day", size=11, color="grey", text_align=ft.TextAlign.CENTER)]), bgcolor="#0F0A1E", padding=12, border_radius=12, expand=True)]),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8), padding=18, bgcolor="#1E1B33", border_radius=18),
            ft.Text("Edit Profile", size=16, weight=ft.FontWeight.BOLD),
            profile_name_field,
            ft.Text("Change PIN", size=16, weight=ft.FontWeight.BOLD),
            old_pin_field, new_pin_field, profile_msg,
            ft.ElevatedButton("💾 Save Changes", on_click=save_profile, bgcolor="#9333EA", color="white", height=48),
            ft.Text("Your account is saved only on this phone in user.json. No one else can see it.", size=11, color="grey"),
        ], spacing=14), padding=18))

    # ---------- HOME ----------
    search_field = ft.TextField(hint_text="Search memories...", prefix_icon=ft.Icons.SEARCH, bgcolor="#1E1B33", border_radius=15, border_color="transparent", height=45, on_change=lambda e: (state.update(search=e.control.value), refresh_home()))
    mood_chips = ft.Row(scroll=ft.ScrollMode.AUTO)
    home_list = ft.Column(spacing=12)

    def refresh_home():
        otd = on_this_day()
        cards = []
        if otd:
            for years, m in otd:
                cards.append(ft.Container(content=ft.Column([
                    ft.Text(f"✨ On This Day • {years} year{'s' if years>1 else ''} ago", color="#FDE68A", weight=ft.FontWeight.BOLD, size=13),
                    ft.Text(m["title"], size=18, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text(m.get("note","")[:80], color="#D1D5DB", size=13),
                ]), padding=16, bgcolor="#3B2A00", border_radius=18, border=ft.border.all(1, "#F59E0B")))
        filtered = []
        for idx, m in enumerate(reversed(memories)):
            real_idx = len(memories)-1-idx
            if state["filter_mood"] != "All" and state["filter_mood"] not in m.get("mood",""):
                continue
            if state["search"] and state["search"].lower() not in (m["title"]+m.get("note","")).lower():
                continue
            filtered.append((real_idx, m))
        if not filtered and not cards:
            cards.append(ft.Container(content=ft.Column([ft.Text("📸", size=40), ft.Text("No memories yet", size=18, weight=ft.FontWeight.BOLD), ft.Text("Tap + Add Memory to save your first moment.", color="grey")], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=30, bgcolor="#1E1B33", border_radius=18))
        for real_idx, m in filtered:
            img = ft.Image(src=m["photo"], width=340, height=180, fit=ft.ImageFit.COVER, border_radius=12) if m.get("photo") and os.path.exists(m["photo"]) else ft.Container(height=0)
            cards.append(ft.Container(content=ft.Column([
                img,
                ft.Row([ft.Text(m["title"], size=18, weight=ft.FontWeight.BOLD, color="white", expand=True),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="#F87171", on_click=lambda e, i=real_idx: delete_memory(i))]),
                ft.Text(f"{m.get('mood','')}  •  {m.get('date','')}", color="#A78BFA", size=12),
                ft.Text(m.get("note",""), color="#E5E7EB", size=13),
                ft.Text(f"🎙️ Voice Note: {m.get('voice','')}" if m.get("voice") else "", color="#FDE68A", size=12) if m.get("voice") else ft.Container(),
            ], spacing=6), padding=14, bgcolor="#1E1B33", border_radius=18))
        home_list.controls = cards
        chips = []
        for mood in ["All"] + MOODS:
            selected = state["filter_mood"] == mood
            chips.append(ft.Chip(label=ft.Text(mood), selected=selected, on_select=lambda e, mo=mood: (state.update(filter_mood=mo), refresh_home()), bgcolor="#9333EA" if selected else "#1E1B33", label_style=ft.TextStyle(color="white")))
        mood_chips.controls = chips
        page.update()

    def show_home():
        page.clean()
        page.add(ft.Container(content=ft.Column([
            ft.Row([ft.Column([ft.Text(f"Hello 👋", size=14, color="#A78BFA"), ft.Text("Memoire", size=28, weight=ft.FontWeight.BOLD, color="white")]),
                    ft.Row([ft.Container(content=ft.Text(f"👤 {user['name']}" if user else "👤", size=13), bgcolor="#1E1B33", padding=10, border_radius=20, on_click=lambda e: show_profile()),
                            ft.Container(content=ft.Text("🔒", size=18), bgcolor="#1E1B33", padding=10, border_radius=50, on_click=lambda e: show_lock())])]),
            search_field, mood_chips, home_list, ft.Container(height=80),
        ], spacing=14), padding=18))
        page.floating_action_button = ft.FloatingActionButton(icon=ft.Icons.ADD, text="Add Memory", bgcolor="#9333EA", on_click=lambda e: show_add())
        refresh_home()

    # --- ADD MEMORY ---
    title_field = ft.TextField(label="Memory Title", hint_text="e.g. College Fest 2026", bgcolor="#1E1B33", border_radius=12)
    note_field = ft.TextField(label="Write your memory...", multiline=True, min_lines=3, bgcolor="#1E1B33", border_radius=12)
    voice_field = ft.TextField(label="Voice Note (type what you said)", hint_text="e.g. Best day ever!", bgcolor="#1E1B33", border_radius=12)
    date_field = ft.TextField(label="Date", value=datetime.date.today().isoformat(), bgcolor="#1E1B33", border_radius=12)
    mood_dropdown = ft.Dropdown(label="Mood", options=[ft.dropdown.Option(m) for m in MOODS], value=MOODS[0], bgcolor="#1E1B33", border_radius=12)
    photo_label = ft.Text("No photo selected", color="grey", size=13)
    photo_preview = ft.Image(width=340, height=180, fit=ft.ImageFit.COVER, border_radius=12, visible=False)

    def pick_photo_result(e: ft.FilePickerResultEvent):
        if e.files:
            src = e.files[0].path
            fname = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(src)}"
            dest = os.path.join(ASSETS_DIR, fname)
            try: shutil.copy(src, dest)
            except: dest = src
            state["photo_path"] = dest
            photo_preview.src = dest
            photo_preview.visible = True
            photo_label.value = "Photo added ✅"
            page.update()

    file_picker = ft.FilePicker(on_result=pick_photo_result)
    page.overlay.append(file_picker)

    def save_memory(e):
        if not title_field.value:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter a title!")); page.snack_bar.open = True; page.update(); return
        new_mem = {"title": title_field.value, "note": note_field.value, "voice": voice_field.value, "date": date_field.value, "mood": mood_dropdown.value, "photo": state["photo_path"] or ""}
        memories.append(new_mem)
        save_memories(memories)
        title_field.value=""; note_field.value=""; voice_field.value=""; state["photo_path"]=None; photo_preview.visible=False; photo_label.value="No photo selected"
        page.snack_bar = ft.SnackBar(ft.Text("Memory saved to your Locker! ✨")); page.snack_bar.open = True
        show_home()

    def show_add():
        page.clean(); page.floating_action_button = None
        page.add(ft.Container(content=ft.Column([
            ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_home()), ft.Text("New Memory", size=22, weight=ft.FontWeight.BOLD)]),
            ft.Container(content=ft.Column([photo_preview, photo_label, ft.ElevatedButton("📸 Choose Photo", on_click=lambda e: file_picker.pick_files(allow_multiple=False, allowed_extensions=["png","jpg","jpeg"]), bgcolor="#2D2A4A", color="white")], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=14, bgcolor="#1E1B33", border_radius=16),
            title_field, date_field, mood_dropdown, note_field, voice_field,
            ft.ElevatedButton("💾 Save to Locker", on_click=save_memory, bgcolor="#9333EA", color="white", height=50),
        ], spacing=14), padding=18))

    # Start: if no user yet -> setup, else lock
    if user is None:
        show_setup()
    else:
        show_lock()

ft.app(target=main)
