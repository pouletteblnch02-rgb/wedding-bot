import logging
import asyncio
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
from telegram.constants import ParseMode
from datetime import datetime

# ========== ВРЕМЕННЫЕ НАСТРОЙКИ (ПРЯМО В КОДЕ) ==========
# ЗАМЕНИТЕ НА СВОИ ЗНАЧЕНИЯ:
TOKEN = "8149864118:AAFdQuGmWMeoDV1682VD0UwvVKkHE8e0raI"  # Ваш токен
ADMIN_ID = "5871069441"  # Ваш ID цифрами
WEDDING_CHANNEL = "https://t.me/+5a-J5bILnKBmMjk6"  # Ваш канал

# Проверка
if not TOKEN or TOKEN == "ВАШ_ТОКЕН_ЗДЕСЬ":
    print("❌ ОШИБКА: Впишите свой токен в код!")
    exit()

# Включим логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем состояния для ConversationHandler
NAME, TRUST, DRINK, OTHER_DRINK, FACT = range(5)

# Список необходимых картинок
REQUIRED_IMAGES = [
    "пока.jpg",
    "МоскваТамбов1.jpg",
    "МоскваТамбов2.jpg",
    "МахачкалаТамбов.jpg",
    "Гдежить.jpg",
    "Программа.jpg",
    "ДресскодЦвета.jpg",
    "Дресскодрефы.jpg",
    "Подарки.jpg"
]

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
async def send_image(update: Update, image_path: str, caption: str = None):
    """Отправляет картинку с обработкой ошибок"""
    try:
        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                if caption:
                    await update.message.reply_photo(photo=photo, caption=caption, parse_mode=ParseMode.HTML)
                else:
                    await update.message.reply_photo(photo=photo)
            return True
        else:
            logger.warning(f"Картинка не найдена: {image_path}")
            if caption:
                await update.message.reply_text(caption, parse_mode=ParseMode.HTML)
            return False
    except Exception as e:
        logger.error(f"Ошибка отправки картинки {image_path}: {e}")
        if caption:
            await update.message.reply_text(caption, parse_mode=ParseMode.HTML)
        return False

async def send_admin_anketa(context: ContextTypes.DEFAULT_TYPE, user_data: dict, user_id: int, username: str, full_name: str):
    """Отправляет анкету админу"""
    anketa_text = (
        f"🎊 <b>НОВЫЙ ГОСТЬ ЗАПОЛНИЛ АНКЕТУ!</b>\n\n"
        f"👤 <b>Имя:</b> {user_data.get('name', 'Не указано')}\n"
        f"✅ <b>Придет?:</b> {user_data.get('trust', 'Не ответил')}\n"
        f"🍸 <b>Напиток:</b> {user_data.get('drink', 'Не выбрано')}\n"
        f"🤫 <b>Факт о себе:</b> {user_data.get('fact', 'Не рассказал')}\n"
        f"🆔 <b>ID:</b> {user_id}\n"
        f"📱 <b>Username:</b> @{username if username else 'нет'}\n"
        f"📝 <b>Полное имя в TG:</b> {full_name}\n"
        f"🕒 <b>Время регистрации:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    
    try:
        await context.bot.send_message(
            chat_id=int(ADMIN_ID),
            text=anketa_text,
            parse_mode=ParseMode.HTML
        )
        logger.info(f"✅ Анкета отправлена админу для пользователя {user_id}")
    except Exception as e:
        logger.error(f"❌ Не удалось отправить анкету админу: {e}")

# ========== КЛАВИАТУРЫ ==========
def get_trust_kb():
    keyboard = [
        [KeyboardButton("✅ Да, точно приду!"), KeyboardButton("❌ Нет, не смогу")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_drink_kb():
    keyboard = [
        [KeyboardButton("🍷 Вино"), KeyboardButton("🥂 Шампанское")],
        [KeyboardButton("🥃 Виски"), KeyboardButton("🚫 Не пью")],
        [KeyboardButton("✍️ Другое"), KeyboardButton("⬅️ Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_city_kb():
    keyboard = [
        [KeyboardButton("🏙️ Москва"), KeyboardButton("🏔️ Махачкала")],
        [KeyboardButton("⬅️ Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_main_kb():
    keyboard = [
        [KeyboardButton("🚗 Как доехать?"), KeyboardButton("🏨 Где жить?")],
        [KeyboardButton("🎭 Программа"), KeyboardButton("👔 Дресс-код")],
        [KeyboardButton("🎁 Подарочкиии"), KeyboardButton("🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ========== ОБРАБОТЧИКИ РЕГИСТРАЦИИ ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 <b>Привет! Один здесь отдыхаешь?</b>\n\n"
        "Не надо одному, приезжай отдыхать к нам в Тамбов на мероприятие <b>04.07.2026</b>!\n\n"
        "Но сначала нам надо поближе познакомиться...\n\n"
        "✍️ <b>Напиши фамилию и имя:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    context.user_data['name'] = name
    
    await update.message.reply_text(
        f"👤 Отлично, <b>{name}</b>! Так это хорошо...\n\n"
        "❓ <b>Но можно ли тебе доверять? Точно придёшь?</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=get_trust_kb()
    )
    return TRUST

async def get_trust(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    
    if answer == "❌ Нет, не смогу":
        await update.message.reply_text(
            "😔 <b>Нам очень жаль...</b>\n\n"
            "У всех бывают трудности, ты справишься!\n"
            "А как справишься - перезапусти бота и нажми <b>«Да»</b>!\n\n"
            "🤞 <i>Надеюсь встретимся!</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    elif answer == "✅ Да, точно приду!":
        context.user_data['trust'] = "Да"
        await update.message.reply_text(
            "🎉 <b>Ура! Будем ждать тебя в Тамбове!</b>\n\n"
            "🍸 <b>А теперь важный вопрос:</b>\n\n"
            "<i>Что же я буду пить?</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_drink_kb()
        )
        return DRINK
    
    return TRUST

async def get_drink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    
    if answer == "⬅️ Назад":
        await update.message.reply_text(
            "🔙 Возвращаемся...",
            reply_markup=get_trust_kb()
        )
        return TRUST
    
    elif answer == "✍️ Другое":
        await update.message.reply_text(
            "✍️ <b>Напиши свой вариант напитка:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
        return OTHER_DRINK
    
    context.user_data['drink'] = answer
    
    await update.message.reply_text(
        "✨ <b>Я уже говорил что нам нужно ближе познакомиться?</b>\n\n"
        "🤫 Напиши <b>один малоизвестный факт о себе:</b>\n\n"
        "<i>Что-то такое, что знают только самые близкие...</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )
    return FACT

async def get_other_drink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    custom_drink = update.message.text.strip()
    context.user_data['drink'] = f"✍️ Другое: {custom_drink}"
    
    await update.message.reply_text(
        "✨ <b>Я уже говорил что нам нужно ближе познакомиться?</b>\n\n"
        "🤫 Напиши <b>один малоизвестный факт о себе:</b>\n\n"
        "<i>Что-то такое, что знают только самые близкие...</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )
    return FACT

async def get_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fact = update.message.text.strip()
    context.user_data['fact'] = fact
    
    await send_admin_anketa(
        context,
        context.user_data,
        update.message.from_user.id,
        update.message.from_user.username,
        update.message.from_user.full_name
    )
    
    caption = (
        "🎉 <b>Ждём тебя на нашей свадьбе!</b>\n\n"
        "📢 <b>Не пропусти важные новости!</b>\n"
        f"Присоединяйся к нашему Telegram-каналу:\n<b>{WEDDING_CHANNEL}</b>\n\n"
        "✨ Там мы будем публиковать:\n"
        "• Актуальные обновления по подготовке\n"
        "• Фото и видео с мероприятий\n"
        "• Важную информацию для гостей\n"
        "• И многое другое!"
    )
    await send_image(update, "пока.jpg", caption)
    
    await asyncio.sleep(0.5)
    
    await update.message.reply_text(
        "👇 <b>А пока выбери пункт меню который тебя интересует:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_kb()
    )
    
    return ConversationHandler.END

# ========== ГЛАВНОЕ МЕНЮ ==========

async def how_to_get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🗺️ <b>Откуда ты странник?</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=get_city_kb()
    )
    return DRINK

async def process_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    
    if city == "⬅️ Назад":
        await update.message.reply_text(
            "🔙 Возвращаемся в главное меню:",
            reply_markup=get_main_kb()
        )
        return ConversationHandler.END
    
    elif city == "🏙️ Москва":
        await send_image(update, "МоскваТамбов1.jpg")
        await asyncio.sleep(0.5)
        await send_image(
            update,
            "МоскваТамбов2.jpg",
            "🚗 <b>Ты любишь путешествия?</b> Вот статья чтобы было чуточку легче:\n"
            "🔗 https://travel.yandex.ru/journal/skolko-ehat-ot-moskvy-do-tambova/"
        )
        await asyncio.sleep(0.5)
    
    elif city == "🏔️ Махачкала":
        await send_image(
            update,
            "МахачкалаТамбов.jpg",
            "✈️ <b>Из Махачкалы в Тамбов</b>\n\n"
            "<i>Рекомендуем рассмотреть авиаперелет или поезд</i>"
        )
        await asyncio.sleep(0.5)
    
    await update.message.reply_text(
        "⬇️ <b>Что еще интересует?</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_kb()
    )
    
    return ConversationHandler.END

async def where_to_live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(
        update,
        "Гдежить.jpg",
        "🏨 <b>Вот несколько приличных мест в центре города:</b>\n\n"
        "1. <b>Азимут</b>\n"
        "🔗 https://azimuthotels.com/ru/tl/availability?hotel=97&checkIn=2026-07-03&checkOut=2026-07-04&nights=1&rooms=1&adults=2&children=0&promo=\n\n"
        "2. <b>Театральная</b>\n"
        "🔗 https://sutochno.ru/front/searchapp/hotels/82821?referrer=reattribution=1&utm_source=yandex&utm_medium=cpc&utm_campaign=dsa-feed-geomskmobl-hotels-russia&utm_term=---autotargeting&utm_content=hotels-russia%7C%7C53063620676&etext=2202.5MK16s4h65-n5qdWxkZ44WIvDrLbyjs67pH5DcuIT2c8BK5LhsYtq9WvwKGkq-XwZ3BmcWJ4ZHRzbWJ3c2JkZA.b3bc3025efdf62d84e5dd4c81c98cfc5e5d1546e&yclid=6238323435726962687&wp_processed=1\n\n"
        "3. <b>Белгравия</b>\n"
        "🔗 https://travel.yandex.ru/hotels/tambov/belgraviia/?adults=2&checkinDate=2026-07-03&checkoutDate=2026-07-04&childrenAges=&roomCount=1&searchPagePollingId=3d63ad984a764ee649dc9cb85f1b309e-0-newsearch&seed=portal-hotels-search\n\n"
        "4. <b>Парк-отель «Плес»</b>\n"
        "🔗 https://plestambov.ru/\n\n"
        "⭐ <i>Бронируйте заранее!</i>"
    )
    return ConversationHandler.END

async def program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(
        update,
        "Программа.jpg",
        "🎪 <b>Скучно не будет, не стесняйтесь участвовать в интерактивах и конкурсах.</b>"
    )
    return ConversationHandler.END

async def dress_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(
        update,
        "ДресскодЦвета.jpg",
        "👗 <b>Для тебя представлена палитра цветов и референсы.</b>"
    )
    await asyncio.sleep(0.5)
    await send_image(update, "Дресскодрефы.jpg")
    return ConversationHandler.END

async def gifts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(
        update,
        "Подарки.jpg",
        "🎁 <b>Для нас каждый подарок важен.</b>"
    )
    return ConversationHandler.END

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🏠 <b>Главное меню</b>\n\n"
        "👇 Выбери что тебя интересует:",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_kb()
    )
    return ConversationHandler.END

async def back_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 <b>Главное меню</b>\n\n"
        "👇 Выбери что тебя интересует:",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_kb()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Действие отменено.",
        reply_markup=get_main_kb()
    )
    return ConversationHandler.END

# ========== ОСНОВНАЯ ФУНКЦИЯ ==========
def main():
    print("=" * 60)
    print("🎊 ЗАПУСК СВАДЕБНОГО БОТА")
    print("=" * 60)
    
    # Проверяем картинки
    missing_images = []
    for image in REQUIRED_IMAGES:
        if not os.path.exists(image):
            missing_images.append(image)
    
    if missing_images:
        print(f"⚠️ Внимание! Не найдены картинки: {missing_images}")
    else:
        print("✅ Все картинки найдены!")
    
    # Создаем Application
    application = Application.builder().token(TOKEN).build()
    
    registration_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            TRUST: [MessageHandler(filters.Regex('^(✅ Да, точно приду!|❌ Нет, не смогу)$'), get_trust)],
            DRINK: [MessageHandler(filters.Regex('^(🍷 Вино|🥂 Шампанское|🥃 Виски|🚫 Не пью|✍️ Другое|⬅️ Назад)$'), get_drink)],
            OTHER_DRINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_other_drink)],
            FACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fact)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(registration_handler)
    application.add_handler(MessageHandler(filters.Regex('^🚗 Как доехать\\?$'), how_to_get))
    application.add_handler(MessageHandler(filters.Regex('^(🏙️ Москва|🏔️ Махачкала|⬅️ Назад)$'), process_city))
    application.add_handler(MessageHandler(filters.Regex('^🏨 Где жить\\?$'), where_to_live))
    application.add_handler(MessageHandler(filters.Regex('^🎭 Программа$'), program))
    application.add_handler(MessageHandler(filters.Regex('^👔 Дресс-код$'), dress_code))
    application.add_handler(MessageHandler(filters.Regex('^🎁 Подарочкиии$'), gifts))
    application.add_handler(MessageHandler(filters.Regex('^🏠 Главное меню$'), main_menu))
    application.add_handler(MessageHandler(filters.Regex('^⬅️ Назад$'), back_button))
    
    print("🔄 Бот запускается...")
    print("=" * 60)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Бот остановлен")
    except Exception as e:
        print(f"💥 Ошибка: {e}")