import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, CommandHandler, filters

# Замените на ваш токен и ваш admin chat ID
TOKEN = "7802613457:AAENf2DtfsBjObdp8xc7Ulg-yZ4jpqgYZVc"
ADMIN_CHAT_ID = 5374141902

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Глобальный словарь для хранения ID пользователя по ID пересланного сообщения
forwarded_messages = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text("Привет! Ваши сообщения будут пересылаться администратору.")


async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересылка сообщения от пользователя администратору."""
    user_id = update.message.from_user.id
    logging.info(f"Получено сообщение от чата: {user_id}")

    if user_id != ADMIN_CHAT_ID:
        # Пересылаем сообщение админу
        forwarded_msg = await update.message.forward(chat_id=ADMIN_CHAT_ID)

        # Сохраняем ID пользователя для ответа
        forwarded_messages[forwarded_msg.message_id] = user_id
        logging.info(f"Сообщение переслано админу. Соответствие ID: {forwarded_msg.message_id} -> {user_id}")


async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправка ответа от администратора пользователю."""
    logging.info("Получен ответ администратора")

    if update.message.reply_to_message:
        original_message_id = update.message.reply_to_message.message_id

        if original_message_id in forwarded_messages:
            user_id = forwarded_messages[original_message_id]
            try:
                await context.bot.send_message(chat_id=user_id, text=f"Ответ администратора: {update.message.text}")
                logging.info(f"Сообщение успешно отправлено пользователю с ID: {user_id}")
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения пользователю: {e}")
        else:
            logging.warning("ID пользователя не найден в forwarded_messages.")
    else:
        logging.warning("Ответ администратора не является ответом на пересланное сообщение.")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(~filters.Chat(ADMIN_CHAT_ID), forward_to_admin))
    app.add_handler(MessageHandler(filters.Chat(ADMIN_CHAT_ID) & filters.REPLY, reply_to_user))

    logging.info("Бот запущен...")
    app.run_polling()


if __name__ == '__main__':
    main()