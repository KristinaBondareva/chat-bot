from telegram import ChatAction, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from mongodb import MongodbHelper
from os import getenv
from dotenv import load_dotenv
import utils
import generator

load_dotenv(override=True)

tok, model = utils.load_tokenizer_and_model(
    "sberbank-ai/rugpt3large_based_on_gpt2")

updater = Updater(token=getenv('TG_TOKEN'), use_context=True)

mongo_helper = MongodbHelper()

dispatcher = updater.dispatcher


def start(update, context):
    mongo_helper.initialize_collection_for_chat(id=update.effective_chat.id)
    main_message = context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=utils.load_string("start_string").format(
            update.message.from_user.first_name),
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(utils.load_string("restart"))]])).message_id

    context.bot.pin_chat_message(
        chat_id=update.effective_chat.id,
        message_id=main_message)


def restart(update, context):
    mongo_helper.initialize_collection_for_chat(update.effective_chat.id)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=utils.load_string("erase"))


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(
    Filters.text & Filters.regex(utils.load_string("restart")), restart))


def generate(update, context):
    if len(update.message.text) >= 400:
        context.bot.send_message(update.effective_chat.id,
                                 text=utils.load_string("long_text_hint"))
    else:
        if "\n" in update.message.text:
            update.message.text = update.message.text.replace("\n", " ")
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id,
            action=ChatAction.TYPING)

        try:
            mongo_helper.insert_message(
                update.effective_chat.id, 
                update.message.text, 
                True)
            bot_message_list, user_message_list = (
                mongo_helper.get_all_messages_for_chat(
                    update.effective_message.chat_id))
            response = generator.generate_response(
                tok,
                model,
                utils.load_string("prompt_beginning"),
                bot_message_list,
                user_message_list,
                utils.load_string("bot_name"),
                utils.load_string("user_name"),
                utils.load_string("no_response_text"))
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=response)
            mongo_helper.insert_message(
                update.effective_chat.id,
                response,
                False)
        except MemoryError:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=utils.load_string("memory_error"))
            restart(update, context)


dispatcher.add_handler(MessageHandler(
    (Filters.text ^ Filters.regex(utils.load_string("restart")))
    & ~Filters.command, generate))

updater.start_polling()
