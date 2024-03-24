import asyncio

from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from Test_2 import demo

API_TOKEN = '7057397327:AAEhF8YpnrJTYPUo58RGTXDT3ZbHIaoj1J4'

form_router = Router()


class Form(StatesGroup):
    symbol = State()
    operation = State()
    sl = State()
    value = State()
    leverage = State()
    margin = State()


@form_router.message(Command('start'))
@form_router.message(F.text == 'Домой')
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='BUY'))
    builder.add(types.KeyboardButton(text="SELL"))
    builder.add(types.KeyboardButton(text="Домой"))
    builder.adjust(2)
    await state.set_state(Form.operation)
    await message.answer('Выберите операцию', reply_markup=builder.as_markup(resize_keyboard=True))


@form_router.message(Form.operation)
async def sl(message: Message, state: FSMContext):
    await state.update_data(operation=message.text)
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='LONG'))
    builder.add(types.KeyboardButton(text="SHORT"))
    builder.add(types.KeyboardButton(text="Домой"))
    builder.adjust(2)
    await state.set_state(Form.sl)
    await message.answer('Выберите вид торговли', reply_markup=builder.as_markup(resize_keyboard=True))


@form_router.message(Form.sl)
async def crypto_s(message: Message, state: FSMContext):
    await state.update_data(sl=message.text)
    await state.set_state(Form.symbol)
    await message.answer('Введите название валюты', reply_markup=ReplyKeyboardRemove())


@form_router.message(Form.symbol)
async def crypto_n(message: Message, state: FSMContext):
    await state.update_data(symbol=f'{message.text.upper()}-USDT')
    await state.set_state(Form.value)
    await message.answer('Введите количество монет в формате 1.0 или 0.01', reply_markup=ReplyKeyboardRemove())


@form_router.message(Form.value)
async def value(message: Message, state: FSMContext):
    await state.update_data(value=float(message.text))
    await state.set_state(Form.leverage)
    await message.answer('Введите плечо или 0', reply_markup=ReplyKeyboardRemove())


@form_router.message(Form.leverage)
async def lev(message: Message, state: FSMContext):
    await state.update_data(leverage=int(message.text))
    await state.set_state(Form.margin)
    await message.answer('Введите маржу в процентах', reply_markup=ReplyKeyboardRemove())


@form_router.message(Form.margin)
async def crypto_all(message: Message, state: FSMContext):
    data = await state.update_data(margin=int(message.text))
    await state.clear()
    print(data)

    try:

        demo(data["symbol"], data["operation"], data["sl"], data["value"], data["leverage"], data["margin"])
        await message.answer('Операция выполнена успешно')
    except Exception as err:
        await message.answer(f'Ошибка при выполнении операции\n{err}')
        print(err)


async def main():
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
