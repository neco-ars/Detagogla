import json
import customtkinter as ctk
import os
import sys

# Цвета (те же, что в прямом переводчике)
BG = "#0b0f19"
PANEL = "#111827"
TEXT = "#e5f7ff"
NEON_CYAN = "#00e5ff"
NEON_MAGENTA = "#ff2bd6"
NEON_GREEN = "#39ff14"


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


ICON_PATH = get_resource_path("lt.ico")
TRANSLATE_PATH = get_resource_path("translate.json")

with open(TRANSLATE_PATH, "r", encoding="utf-8") as f:
    ALPHABET = json.load(f)

# Обратный словарь: сортируем по убыванию длины тагоглица-токена,
# чтобы при разборе сначала проверять более длинные (и более специфичные)
# последовательности символов ("Ո๐•" раньше "Ո๐" и т.д.)
REVERSE_PAIRS = sorted(ALPHABET.items(), key=lambda kv: -len(kv[1]))


def to_tagoglica(text: str) -> str:
    text = text.lower()
    return "".join(ALPHABET.get(char, char) for char in text)


def to_russian(text: str) -> str:
    """
    Жадный разбор слева направо: на каждой позиции ищем самый длинный
    известный токен тагоглицы и заменяем его на соответствующую букву.
    Если совпадений нет — символ переносится как есть (числа, пробелы,
    пунктуация и т.п.).

    ВНИМАНИЕ: таблица содержит встроенную неоднозначность — "щ" ("u„")
    посимвольно совпадает с последовательностью "ш"+"ъ". Она всегда
    будет раскодирована как "щ".
    """
    result = []
    i = 0
    n = len(text)
    while i < n:
        matched = False
        for cyr, tag in REVERSE_PAIRS:
            if text.startswith(tag, i):
                result.append(cyr)
                i += len(tag)
                matched = True
                break
        if not matched:
            result.append(text[i])
            i += 1
    return "".join(result)


TAGOG_NAME = to_tagoglica("тагоглица")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title(f"{TAGOG_NAME} → кириллица")
root.geometry("500x300")
root.minsize(500, 200)
root.wm_aspect(1, 1, 1, 1)
try:
    root.iconbitmap(ICON_PATH)
except Exception:
    pass

root.configure(fg_color=BG)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)

header_font = ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
text_font = ctk.CTkFont(family="Segoe UI", size=15)

ctk.CTkLabel(
    root,
    text=TAGOG_NAME,
    font=header_font,
    text_color=NEON_MAGENTA,
    anchor="w"
).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 6))

ctk.CTkLabel(
    root,
    text="кириллица",
    font=header_font,
    text_color=NEON_CYAN,
    anchor="w"
).grid(row=0, column=1, sticky="w", padx=16, pady=(16, 6))

source_text = ctk.CTkTextbox(
    root,
    wrap="word",
    corner_radius=14,
    border_width=2,
    fg_color=PANEL,
    text_color=TEXT,
    border_color=NEON_MAGENTA,
    font=text_font
)
source_text.grid(
    row=1,
    column=0,
    sticky="nsew",
    padx=(16, 8),
    pady=(0, 8)
)

output_text = ctk.CTkTextbox(
    root,
    wrap="word",
    state="disabled",
    corner_radius=14,
    border_width=2,
    fg_color=PANEL,
    text_color="#ffffff",
    border_color=NEON_CYAN,
    font=text_font
)
output_text.grid(
    row=1,
    column=1,
    sticky="nsew",
    padx=(8, 16),
    pady=(0, 8)
)


def update_translation():
    text = source_text.get("1.0", "end-1c")
    translated = to_russian(text)

    output_text.configure(state="normal")
    output_text.delete("1.0", "end")
    output_text.insert("1.0", translated)
    output_text.configure(state="disabled")


last_text = ""


def poll_changes():
    global last_text

    current = source_text.get("1.0", "end-1c")

    if current != last_text:
        last_text = current
        update_translation()

    root.after(120, poll_changes)


copy_job = None


def copy_result():
    global copy_job

    result = output_text.get("1.0", "end-1c")

    root.clipboard_clear()
    root.clipboard_append(result)

    copy_btn.configure(
        text="скопировано!",
        border_color=NEON_GREEN,
        text_color=NEON_GREEN
    )

    if copy_job is not None:
        root.after_cancel(copy_job)

    copy_job = root.after(
        1000,
        lambda: copy_btn.configure(
            text="копировать результат",
            border_color=NEON_CYAN,
            text_color=NEON_CYAN
        )
    )


copy_btn = ctk.CTkButton(
    root,
    text="копировать результат",
    command=copy_result,
    height=44,
    corner_radius=12,
    border_width=2,
    fg_color="transparent",
    hover_color="#1e293b",
    border_color=NEON_CYAN,
    text_color=NEON_CYAN,
    font=ctk.CTkFont(size=16, weight="bold")
)
copy_btn.grid(
    row=2,
    column=0,
    columnspan=2,
    sticky="ew",
    padx=16,
    pady=(0, 16)
)

try:
    source_text.focus_set()
except Exception:
    pass

update_translation()
last_text = source_text.get("1.0", "end-1c")
root.after(120, poll_changes)

root.mainloop()
