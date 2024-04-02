import asyncio

from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from Test_2 import demo, get_balance, get_price, get_min_price
import Test_2

API_TOKEN = '7057397327:AAEhF8YpnrJTYPUo58RGTXDT3ZbHIaoj1J4'

form_router = Router()

builder_home = ReplyKeyboardBuilder()
builder_home.add(types.KeyboardButton(text='Домой'))
builder_home_ready = builder_home.as_markup(resize_keyboard=True)


class Form(StatesGroup):
    symbol = State()
    operation = State()
    sl = State()
    value = State()
    leverage = State()
    margin = State()
    balance = 0
    price = 0
    lev_data = []


class Api(StatesGroup):
    apikey = State()
    secretkey = State()


@form_router.message(Command('start'))
@form_router.message(F.text == 'Домой')
async def cmd_start(message: Message, state: FSMContext):
    data = await state.update_data()
    if (data.get('apikey') and data.get('secretkey')) or (Test_2.APIKEY and Test_2.SECRETKEY):
        await state.clear()
        balance = float(get_balance()['data']['balance']['balance'])
        if not balance:
            await message.answer('Ваш баланс равен 0, пополните баланс и попробуйте снова',
                                 reply_markup=builder_home_ready)
        else:
            Form.balance = balance
            builder = ReplyKeyboardBuilder()
            builder.add(types.KeyboardButton(text='BUY'))
            builder.add(types.KeyboardButton(text="SELL"))
            builder.add(types.KeyboardButton(text="Домой"))
            builder.adjust(2)
            await state.set_state(Form.operation)
            await message.answer('Выберите операцию', reply_markup=builder.as_markup(resize_keyboard=True))
    else:
        await message.answer('Введите Apikey')
        await state.set_state(Api.apikey)


@form_router.message(Api.apikey)
async def get_secret(message: Message, state: FSMContext):
    await state.update_data(apikey=message.text)
    await message.answer('Введите secretkey')
    await state.set_state(Api.secretkey)


@form_router.message(Api.secretkey)
async def check_keys(message: Message, state: FSMContext):
    data = await state.update_data(secretkey=message.text)

    try:
        Test_2.APIKEY = data['apikey']
        Test_2.SECRETKEY = data['secretkey']
        a = get_balance()
        if not a['msg']:
            await message.answer('Вы успешно зарегистрированы', reply_markup=builder_home_ready)
        else:
            await message.answer('Вы ввели неправильные ключи доступа')
            await message.answer('Введите apikey')
            await state.set_state(Api.apikey)
    except Exception:
        await message.answer('Вы ввели неправильные ключи доступа')
        await message.answer('Введите apikey')
        await state.set_state(Api.apikey)


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


# @form_router.message(Form.symbol)
# async def crypto_n(message: Message, state: FSMContext):
#     await state.update_data(symbol=f'{message.text.upper()}-USDT')
#     await state.set_state(Form.value)
#     await message.answer('Введите количество монет в формате 1.0 или 0.01', reply_markup=ReplyKeyboardRemove())

@form_router.message(Form.symbol)
async def lev(message: Message, state: FSMContext):
    do = False
    while True:
        if do:
            await state.set_state(Form.symbol)
            msg = Message.text.upper()
        else:
            msg = message.text.upper()
        try:
            need = msg + '-USDT'
            price = float(get_price(need)['data']['bidPrice'])
            if price:
                await state.update_data(symbol=need)
                break
            else:
                await message.answer('Цена монеты равна 0.0, введите другую монету',
                                     reply_markup=builder_home_ready)
                do = True
        except Exception:
            await message.answer('Монета не найдена, убедитесь в правильности названия монеты',
                                 reply_markup=builder_home_ready)
            do = True

    await state.set_state(Form.margin)

    balance = Form.balance
    Form.price = price
    value_second = 0
    value_symb = 0

    for i in get_min_price()['data']:
        if i['symbol'] == need:
            value_symb = i['tradeMinUSDT']
            value_second = i['tradeMinQuantity']
            Form.lev_data = [i['maxLongLeverage'], i['maxShortLeverage']]

    m_second = round(price / balance * value_second * 100, 2)
    m_first = round(value_symb / balance, 2) * 100
    # minn = min(m_first, m_second)
    maxx = max(m_first, m_second)
    await message.answer(
        f'На вашем счету доступно {balance}\nЦена монеты: {price}'
        f'\nМинимальная маржа: {maxx}%\nВведите маржу в процентах',
        reply_markup=ReplyKeyboardRemove())


@form_router.message(Form.margin)
async def value(message: Message, state: FSMContext):
    do = False
    while True:
        if do:
            a = Message.text
        else:
            a = message.text
        try:
            a = int(a)
            if 0 < a <= 100:
                await state.update_data(margin=a)
                break
            else:
                await message.answer('Введите маржу от 0% до 100%')
                do = True
        except Exception:
            await message.answer('Маржа должна быть числом')
            do = True

    await state.set_state(Form.leverage)
    # print(Form.lev_data)
    lev_max = Form.lev_data[0] if Form.operation == 'LONG' else Form.lev_data[1]
    await message.answer(f'Введите плечо от 0 до {lev_max}', reply_markup=ReplyKeyboardRemove())


@form_router.message(Form.leverage)
async def crypto_all(message: Message, state: FSMContext):
    lev_max = Form.lev_data[0] if Form.operation == 'LONG' else Form.lev_data[1]
    do = False
    while True:
        if do:
            lev_real = Message.text
        else:
            lev_real = message.text
        try:
            lev_real = int(lev_real)
            if 0 <= lev_real <= lev_max:
                data = await state.update_data(leverage=lev_real)
                break
            else:
                await message.answer(f'Введите плечо в диапазоне от 0 до {lev_max}')
                do = True
        except Exception:
            await message.answer('Плечо должно быть числом')
            do = True

    await state.clear()

    print(data)

    quantity = (Form.balance * (data['margin'] / 100)) / Form.price
    try:

        a = demo(data["symbol"], data["operation"], data["sl"], data["leverage"], quantity)
        msg = a['msg']
        # print(a)
        if not msg or not a['success'] == 'false':
            await message.answer('Операция выполнена успешно', reply_markup=builder_home_ready)

        else:
            await message.answer(f'Ошибка при выполнении операции\n{msg}\n{a["code"]}', reply_markup=builder_home_ready)

    except Exception as err:
        await message.answer(
            f'Ошибка при выполнении операции\n{err}\nВаши данные:\n{", ".join([str(i) for i in data.values()])}',
            reply_markup=builder_home_ready)

        # print(err)


async def main():
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
