import random
import json
import logging
from datetime import datetime
from pyrogram import Client, filters, enums

api_id = "no"
api_hash = "no"
bot_token = "no"
app = Client("emoji", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

logging.basicConfig(filename="bot_log.txt", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# дохуя функций пиздец

def load_data(): # загружает из файла дб
    try:
        with open("data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"users": {}}

def save_data(data): # сохраняет дб
    with open("data.json", "w") as file:
        json.dump(data, file)

def get_casino_emojis(): # казино АХАХХА лень
    casino_emojis = ["🍒", "🍋", "7️⃣", "🎲", "🎰", "💰"]
    return random.choices(casino_emojis, k=3)

def is_admin(user_id): # без коментов
    user_data = data["users"].get(str(user_id), {})
    return user_data.get("admin", False)

def is_blocked(user_id): # без коментов
    user_data = data["users"].get(str(user_id), {})
    return user_data.get("blocked", False)

def get_credits(user_id): # без коментов
    user_data = data["users"].get(str(user_id), {})
    return user_data.get("credits", 0)

def set_credits(user_id, credits): # добавить кредиты
    data["users"].setdefault(str(user_id), {})
    data["users"][str(user_id)]["credits"] = credits
    save_data(data)

def add_credits(user_id, amount): # без коментов
    credits = get_credits(user_id)
    credits += amount
    set_credits(user_id, credits)

def deduct_credits(user_id, amount): # удалить кредиты
    credits = get_credits(user_id)
    credits -= amount
    set_credits(user_id, credits)

def register_user(user_id): # регистрация
    set_credits(user_id, 30)
    data["users"][str(user_id)]["blocked"] = False
    data["users"][str(user_id)]["admin"] = False
    save_data(data)

def determine_prize(emojis, user_id): # приз
    spins = data["users"][str(user_id)].get("spins", 0) + 1
    data["users"][str(user_id)]["spins"] = spins
    save_data(data)
    if emojis[0] == emojis[1] == emojis[2]:
        if emojis[0] == "7️⃣":
            return "Джекпот", 77
        else:
            return "Выигрыш", 25
    else:
        return "Попробуйте еще раз", 0

data = load_data()

# порядок: start spin addcredits blockuser info buycredits commands

@app.on_message(filters.command("id", prefixes="/"))
def id_command_handler(client, message):
    user_id = message.from_user.id
    response = f"Ваш пользовательский ID: {user_id}"
    message.reply_text(response)

@app.on_message(filters.command("start", prefixes="/"))
def start_command_handler(client, message):
    user_id = message.from_user.id

    if user_id in data["users"]:
        credits = get_credits(user_id)
        spins = data["users"][str(user_id)].get("spins", 0)
        response = (
            f"Добро пожаловать обратно! Ваши кредиты: {credits}\n"
            f"Всего кручений: {spins} 🔄🎰"
        )
    else:
        register_user(user_id)
        response = (
            "Добро пожаловать в Emoji Casino Bot! 🎰🎉\n"
            "Этот бот — всего лишь смешная шутка, но мы относимся к победам серьезно! 💯\n"
            "Вы зарегистрированы с 30 кредитами. Удачи и хорошего временипровождения! 🍀😄"
        )

    message.reply_text(response, parse_mode=enums.ParseMode.MARKDOWN)

@app.on_message(filters.command("spin", prefixes="/"))
def spin_command_handler(client, message):
    user_id = message.from_user.id
    if is_blocked(user_id):
        message.reply_text("Вы заблокированы и не можете использовать бота. 🚫😢")
        return
    if not is_admin(user_id):
        credits = get_credits(user_id)
        price_per_spin = 10
        if credits < price_per_spin:
            message.reply_text("У вас недостаточно кредитов для кручения. 💔")
            return
        deduct_credits(user_id, price_per_spin)
    emojis_result = get_casino_emojis()
    result_text = " ".join(emojis_result)
    prize, prize_credits = determine_prize(emojis_result, user_id)
    if prize_credits > 0:
        add_credits(user_id, prize_credits)
    response = f"Результат: {result_text}\n{prize}! Выиграно кредитов: {prize_credits} 💰🎉"
    message.reply_text(response)
    logging.info(f"User {message.from_user.first_name} spun the slot machine at {datetime.now()}. Result: {result_text}, Prize: {prize} ({prize_credits} credits)")

@app.on_message(filters.command("addcredits", prefixes="/"))
def add_credits_command_handler(client, message):
    user_id = message.from_user.id
    args = message.command[1:]
    if not args or len(args) != 2:
        message.reply_text("Неправильное использование. Используйте /addcredits [user_id] [количество].")
        return
    if not is_admin(user_id):
        message.reply_text("У вас нет прав на выполнение этого действия. 🔒🚫")
        return
    target_user_id, amount = args
    try:
        target_user_id = int(target_user_id)
        amount = int(amount)
    except ValueError:
        message.reply_text("Неправильный идентификатор пользователя или количество.")
        return
    if amount <= 0:
        message.reply_text("Количество должно быть положительным числом.")
        return
    add_credits(target_user_id, amount)
    message.reply_text(f"{amount} кредитов добавлено пользователю с ID {target_user_id}. ✅💰")
    logging.info(f"User {message.from_user.first_name} added {amount} credits to user {target_user_id} at {datetime.now()}")


@app.on_message(filters.command("blockuser", prefixes="/"))
def block_user_command_handler(client, message):
    user_id = message.from_user.id
    args = message.command[1:]
    if not args or len(args) != 1:
        message.reply_text("Неправильное использование. Используйте /blockuser [user_id].")
        return
    if not is_admin(user_id):
        message.reply_text("У вас нет прав на выполнение этого действия. 🔒🚫")
        return
    target_user_id = args[0]
    try:
        target_user_id = int(target_user_id)
    except ValueError:
        message.reply_text("Неправильный идентификатор пользователя.")
        return

    data["users"].setdefault(str(target_user_id), {})
    data["users"][str(target_user_id)]["blocked"] = True
    save_data(data)
    message.reply_text(f"Пользователь с ID {target_user_id} заблокирован. 🔒🚫")
    logging.info(f"User {message.from_user.first_name} blocked user {target_user_id} at {datetime.now()}")

@app.on_message(filters.command("info", prefixes="/"))
def info_command_handler(client, message):
    user_id = message.from_user.id
    if is_blocked(user_id): 
        message.reply_text("Вы заблокированы и не можете использовать бота. 🚫😢")
        return
    credits = get_credits(user_id)
    spins = data["users"][str(user_id)].get("spins", 0)
    response = f"Ваши кредиты: {credits}\nВсего кручений: {spins} 🔄🎰" # добавить больше текста 
    message.reply_text(response)
    logging.info(f"User {message.from_user.first_name} checked their info at {datetime.now()}")


@app.on_message(filters.command("buycredits", prefixes="/"))
def buy_credits_command_handler(client, message):
    buy_credits_text = (
        "Хотите получить больше кредитов? Конечно! Просто отправьте личное сообщение "
        "[@nwsynx](https://t.me/nwsynx) и получите свои новенькие кредиты! 💬📨\n\n"
        "Сообщите @nwsynx, сколько кредитов вам нужно, и следуйте инструкциям. Как только сделка завершена, "
        "кредиты — все ваши! 💰💳\n\n"
        "Спасибо, что поддерживаете Emoji Casino Bot! 🎉🎰" # кринж
    )
    message.reply_text(
        buy_credits_text,
        parse_mode=enums.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )
    logging.info(f"User {message.from_user.first_name} asked for information about buying credits at {datetime.now()}")

@app.on_message(filters.command("commands", prefixes="/"))
def commands_command_handler(client, message):
    commands_text = (
        "Доступные команды:\n"
        "/start - Начать игру и получить приветственное сообщение.\n"
        "/spin - Крутить барабаны казино.\n"
        "/addcredits [user_id] [количество] - Добавить кредиты пользователю (только для админов).\n"
        "/blockuser [user_id] - Заблокировать пользователя (только для админов).\n"
        "/info - Показать информацию о вашем счете и числе кручений.\n"
        "/buycredits - Купить дополнительные кредиты."
    )
    message.reply_text(commands_text, parse_mode=enums.ParseMode.MARKDOWN)

app.run()
