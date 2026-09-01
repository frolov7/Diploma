import logging
import traceback
from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import json
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import fetch_company_data, predict_from_dict, explain_prediction
from utils import load_filtered_json 


# Логирование
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/credit_bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("credit_bot")
logger.setLevel(logging.INFO)

LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "predictions.jsonl"))
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# 📤 Логирование jsonl результатов

def log_company_prediction(company_data: dict, prediction: int):
    log_data = company_data.copy()
    log_data["prediction"] = prediction
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")

def get_main_keyboard(active: bool):
    if active:
        return ReplyKeyboardMarkup([[
            "Отправить ИНН"], ["Стоп"]], resize_keyboard=True)
    return ReplyKeyboardMarkup([ ["Старт"] ], resize_keyboard=True)

async def activate_user(update, context):
    context.user_data["active"] = True
    context.user_data["awaiting_inn"] = False

    keyboard = [["Старт", "Стоп"], ["Отправить ИНН"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Добро пожаловать в бота! Выберите действие.",
        reply_markup=markup,
        parse_mode=ParseMode.HTML
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await activate_user(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Здесь будет обработка inline-кнопок.")

async def handle_standard_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    is_active = context.user_data.get("active", False)

    if not is_active and text != "Старт":
        await update.message.reply_text("Бот остановлен. Нажмите /start, чтобы запустить снова.", reply_markup=get_main_keyboard(False))
        return

    if text == "Старт":
        if is_active:
            await update.message.reply_text("Бот уже запущен.", reply_markup=get_main_keyboard(True))
        else:
            await activate_user(update, context)

    elif text == "Стоп":
        context.user_data["active"] = False
        context.user_data["awaiting_inn"] = False
        await update.message.reply_text("Бот остановлен. Нажмите /start для перезапуска.", reply_markup=get_main_keyboard(False))

    elif text == "Отправить ИНН":
        context.user_data["awaiting_inn"] = True
        await update.message.reply_text("Пожалуйста, введите ИНН.", reply_markup=get_main_keyboard(True))

    elif context.user_data.get("awaiting_inn"):
        context.user_data["awaiting_inn"] = False
        await update.message.reply_text(f"🔍 Ищем компанию по ИНН: <code>{text}</code>", parse_mode=ParseMode.HTML)

        company_data = load_filtered_json(text)

        if not company_data:
            await update.message.reply_text(
                f"<b>ИНН:</b> <code>{text}</code>\n<b>Результат:</b> ❌ Не удалось получить данные с API ФНС",
                parse_mode=ParseMode.HTML,
                reply_markup=get_main_keyboard(True)
            )
            return

        try:
            pred = predict_from_dict(company_data)
            log_record = company_data.copy()
            log_record["prediction"] = pred
            logger.info(json.dumps(log_record, ensure_ascii=False))
            log_company_prediction(company_data, pred)

            result = "✅ Кредитоспособна" if pred else "⚠️ Не рекомендована к кредитованию"
            explanation = explain_prediction(company_data, pred)
            company_name = company_data.get("name", "—")
            ogrn = company_data.get("ogrn", "—")
            region = company_data.get("region", "—")
            reg_date = company_data.get("reg_date", "—")
            okved = company_data.get("okved", "—")

            name = company_data.get("name") or "—"
            ogrn = company_data.get("ogrn") or "—"
            reg_date = company_data.get("ogrn_date") or "—"
            region = company_data.get("address", "—").split(",")[0]
            okved_code = company_data.get("main_okved") or "—"
            okved_text = company_data.get("main_okved_text") or ""

            reason_text = explain_prediction(company_data, pred)

            await update.message.reply_text(
                f"<b>ИНН:</b> <code>{text}</code>\n"
                f"<b>Компания:</b> {name}\n"
                f"<b>ОГРН:</b> {ogrn}\n"
                f"<b>Дата регистрации:</b> {reg_date}\n"
                f"<b>Регион:</b> {region}\n"
                f"<b>ОКВЭД:</b> {okved_code} {okved_text}\n\n"
                f"<b>Результат:</b> {result}\n"
                f"<b>Причины:</b>\n{reason_text}",
                parse_mode=ParseMode.HTML,
                reply_markup=get_main_keyboard(True)
            )

        except Exception as e:
            await update.message.reply_text(
                f"Ошибка при анализе данных: <code>{str(e)}</code>",
                parse_mode=ParseMode.HTML,
                reply_markup=get_main_keyboard(True)
            )

    else:
        await update.message.reply_text("Неизвестная команда.", reply_markup=get_main_keyboard(is_active))

async def error_handler(update, context):
    tb = "".join(traceback.format_exception(None, context.error, context.error.__traceback__))
    logger.error(f"‼ Uncaught exception:\n{tb}")
    if update and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Ошибка:\n<code>{str(context.error)}</code>",
            parse_mode=ParseMode.HTML,
        )

def main():
    BOT_TOKEN = "8038925716:AAFVN9VPHztw7vJikCBFQZ_1IaEK7Je4WFE"
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_standard_buttons))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
