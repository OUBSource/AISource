import tkinter as tk
from tkinter import scrolledtext
import requests
import json
import os

# 🔑 API ключ и настройки
API_KEY = "ВАШ_КЛЮЧ"
MODEL = "meta-llama/llama-3-70b-instruct"
HISTORY_FILE = "history.json"

# 🧠 Жёстко заданный system prompt (НЕ сохраняется в файл!)
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Ты — умный, дружелюбный и строго русскоязычный ассистент. "
        "Отвечай исключительно на русском языке, без вставок английских слов. "
        "Даже если пользователь пишет на другом языке — отвечай всё равно на русском. "
        "Ты создан компанией OUBStudios. Ты общаешься с пользователем в программе, созданной OUBStudios."
    )
}

# 📥 Загрузка истории (без system prompt)
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

# 💾 Сохранение истории (без system prompt)
def save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages_no_system, f, ensure_ascii=False, indent=2)

# 💬 Загрузка истории чата
messages_no_system = load_history()  # Только пользователь и ассистент
messages = [SYSTEM_PROMPT] + messages_no_system  # В оперативной памяти — с system

# 📤 Отправка сообщения
def send_message():
    user_input = entry.get()
    if not user_input.strip():
        return

    chat_history.config(state='normal')
    chat_history.insert(tk.END, "Вы: " + user_input + "\n")
    chat_history.config(state='disabled')
    entry.delete(0, tk.END)

    try:
        # Контрольная инструкция
        control_instruction = "❗Пожалуйста, отвечай только на русском языке, без английских слов."
        user_message = f"{user_input}\n\n{control_instruction}"

        # Обновление обеих историй
        messages.append({"role": "user", "content": user_message})
        messages_no_system.append({"role": "user", "content": user_message})

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://your-app.com",
                "X-Title": "RussianLlamaChat"
            },
            json={
                "model": MODEL,
                "messages": messages
            }
        )

        data = response.json()

        if "choices" in data:
            reply = data['choices'][0]['message']['content']
        else:
            reply = f"[Ошибка в ответе]: {data}"

        messages.append({"role": "assistant", "content": reply})
        messages_no_system.append({"role": "assistant", "content": reply})
        save_history()
    except Exception as e:
        reply = f"[Ошибка]: {str(e)}"

    chat_history.config(state='normal')
    chat_history.insert(tk.END, "Бот: " + reply + "\n\n")
    chat_history.config(state='disabled')
    chat_history.see(tk.END)

# 🖼️ Интерфейс Tkinter
root = tk.Tk()
root.title("Умный русскоязычный чат-бот")
root.geometry("600x500")

chat_history = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# 🔄 Отображение старой истории
chat_history.config(state='normal')
for msg in messages_no_system:
    if msg["role"] == "user":
        chat_history.insert(tk.END, "Вы: " + msg["content"].split('\n\n')[0] + "\n")
    elif msg["role"] == "assistant":
        chat_history.insert(tk.END, "Бот: " + msg["content"] + "\n\n")
chat_history.config(state='disabled')
chat_history.see(tk.END)

entry = tk.Entry(root, font=("Arial", 14))
entry.pack(padx=10, pady=(0, 10), fill=tk.X)
entry.bind("<Return>", lambda event: send_message())

root.mainloop()
