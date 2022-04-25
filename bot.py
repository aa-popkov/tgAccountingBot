import logging
import configparser
from random import randint
from sys import exit

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData

from googlesheets import gs_main
from custom_func import pars_user_data

config = configparser.ConfigParser()
config.read('config.ini')


token = config.get('tg_bot', 'token')
admin_chat_id = int(config.get('tg_bot', 'admin_id'))
admin_login = config.get('tg_bot', 'admin_login')
if not token or not admin_chat_id:
    exit("Error: no token or admin chat id provided")

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

cb = CallbackData("acoounting", "type")
account_type_btn = ['🛒Расходы', '💰Доходы']
exp_category_btn = ['🍜Продукты', '🏡Квартира', '🚗Транспорт',
                    '🌍Интернет/Связь', '🚬Табак', '🍺Алкоголь',
                    '⚒Обеды/Кофе', '🎁Подарки', '🎉Развлечения',
                    '👔Одежда/Обувь', '🚄Поездки']
inc_category_btn = ['💰Зарплата', '💸Аванс', '💳Кешбек', '🎁Подарки']


class OrderAccount(StatesGroup):
    waiting_type_account = State()
    waiting_category = State()
    waiting_sum = State()
    waiting_delete_row = State()


@dp.message_handler(commands=['start'], state="*")
async def start_dialog(message: types.Message, state: FSMContext):
    if not is_admin(message):
        await message.answer(f"Это личный бот, уходи!\nПо всем вопросам - {admin_login}")
        return
    await state.finish()
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(*account_type_btn)
    await message.answer('Привет!\nВыбери тип расходов, на панели', reply_markup=kb)
    await OrderAccount.waiting_type_account.set()


@dp.message_handler(commands=["delete"], state="*")
async def delete_last_row(message: types.Message, state: FSMContext):
    if not is_admin(message):
        await message.answer(f"Это личный бот, уходи!\nПо всем вопросам - {admin_login}")
        return
    await state.finish()
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add('⛔Удалить строку⛔')
    await message.answer("Действительно удалить последню строку?", reply_markup=kb)
    await OrderAccount.waiting_delete_row.set()


@dp.message_handler(state=OrderAccount.waiting_delete_row)
async def delete_last_row(message: types.Message, state: FSMContext):
    if not is_admin(message):
        await message.answer(f"Это личный бот, уходи!\nПо всем вопросам - {admin_login}")
        return
    if message.text != '⛔Удалить строку⛔':
        await message.answer("Используй кнопку на панели!")
        return
    await state.finish()
    num_row_for_update = len(gs_main.get_value(["Data!A1:A"]))
    sheet_range = f"Data!A{num_row_for_update}:E{num_row_for_update}"
    gs_main.set_value([['', '', '', '', '']], sheet_range)
    await message.answer("Последняя строка удалена!\n\n"
                         "Начать заново:\n"
                         "/start")


@dp.message_handler(state=OrderAccount.waiting_type_account)
async def choose_category(message: types.Message, state: FSMContext):
    if not is_admin(message):
        await message.answer(f"Это личный бот, уходи!\nПо всем вопросам - {admin_login}")
        return
    if message.text not in account_type_btn:
        await message.answer("Выбери тип используя панель ниже.")
        return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    if message.text == account_type_btn[0]:
        kb.add(*exp_category_btn)
    else:
        kb.add(*inc_category_btn)
    await message.answer(f"Выбраны {message.text}\nВыберите категорию", reply_markup=kb)
    await OrderAccount.next()
    await state.update_data(chosen_account=message.text)


@dp.message_handler(state=OrderAccount.waiting_category)
async def add_sum(message: types.Message, state: FSMContext):
    if not is_admin(message):
        await message.answer(f"Это личный бот, уходи!\nПо всем вопросам - {admin_login}")
        return
    user_data = await state.get_data()
    if message.text not in exp_category_btn and user_data['chosen_account'] == account_type_btn[0]:
        await message.answer("Выбери категорию используя панель ниже.")
        return
    if message.text not in inc_category_btn and user_data['chosen_account'] == account_type_btn[1]:
        await message.answer("Выбери категорию используя панель ниже.")
        return
    await OrderAccount.next()
    await state.update_data(chosen_category=message.text)
    await message.answer(f"Выбрана категория {message.text}\n\n"
                         f"Введите:\n"
                         f"СУММА ДАТА*\n\n* - Необзательные поля\nФормат 📆Даты - dd.mm.yyyy")


@dp.message_handler(state=OrderAccount.waiting_sum)
async def post_add_sum(message: types.Message, state: FSMContext):
    if not is_admin(message):
        await message.answer(f"Это личный бот, уходи!\nПо всем вопросам - {admin_login}")
        return
    pars_message = pars_user_data(message.text)
    if pars_message['sum'] is None:
        await message.answer('Введи сообщение по ШАБЛОНУ!')
        return

    user_data = await state.get_data()
    type_acc = "❌" if user_data['chosen_account'] == account_type_btn[0] else "✔"
    arr_to_put = [type_acc, pars_message['sum'], (user_data['chosen_category'])[1::], 'Общий', pars_message['date']]

    num_row_for_update = len(gs_main.get_value(["Data!A1:A"]))+1
    sheet_range = f"Data!A{num_row_for_update}:E{num_row_for_update}"
    gs_main.set_value([arr_to_put], sheet_range)

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    if user_data['chosen_account'] == account_type_btn[0]:
        kb.add(*exp_category_btn)
    else:
        kb.add(*inc_category_btn)
    await message.answer(f"Cумма {message.text}р добавлена в\n"
                         f"категорию {user_data['chosen_category']}", reply_markup=kb)
    await OrderAccount.previous()


@dp.message_handler(commands="random")
async def cmd_random(message: types.Message):
    if not is_admin(message):
        await message.answer(f"Это личный бот, уходи!\nПо всем вопросам - {admin_login}")
        return
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Нажми меня", callback_data="random_value"))
    await message.answer("Нажмите на кнопку, чтобы бот отправил число от 1 до 10", reply_markup=keyboard)


@dp.callback_query_handler(text="random_value")
async def send_random_value(call: types.CallbackQuery):
    await call.message.answer(str(randint(1, 10)))
    await call.answer()


@dp.message_handler()
async def empty_message(message: types.Message):
    if not is_admin(message):
        await message.answer(f"Это личный бот, уходи!\nПо всем вопросам - {admin_login}")
        return
    await message.answer("По такой команде ничего не нашел 😭\n"
                         "Воспользуйтесь одной из команд:\n"
                         "/start")


def is_admin(message: types.Message):
    if message.from_user.id != admin_chat_id:
        return False
    else:
        return True


async def on_startup(dp: Dispatcher):
    commands = [
        BotCommand(command="/start", description="Стартуем!"),
        # BotCommand(command="/help", description="Помогаем"),
        BotCommand(command="/delete", description="Удаляем!"),
    ]
    await bot.set_my_commands(commands)
    await dp.bot.send_message(admin_chat_id, 'Бот перезапущен\n🏁 - /start')


# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
