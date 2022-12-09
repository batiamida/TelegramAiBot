from pyrogram import Client, filters
import time
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,
                            InlineKeyboardButton)
import configparser
import psycopg2 as pg
import os

conf = configparser.ConfigParser()
conf.read('conf.ini')
app = Client(**conf['TELEGRAM'])
request_ls = []

@app.on_message(filters.command(['start']))
async def main(client, message):
    if message.chat.username in ['Always_chillingUP', 'Irynchuk', 'sonja_su', 'nightraypng']:
        await message.reply('in order to start click on the button', reply_markup=ReplyKeyboardMarkup([["Let's go!"]]))

@app.on_message(filters.command(['stat']))
async def get_stat(client, message):
    if message.chat.username in ['Always_chillingUP', 'Irynchuk', 'sonja_su', 'nightraypng']:
        conn = pg.connect(**conf['DATABASE'])
        cur = conn.cursor()
        cur.execute("SELECT count(*) AS pos_counter FROM dataset_u_new WHERE propaganda=FALSE")
        pos_counter = cur.fetchone()[0]
        cur.execute("SELECT count(*) AS neg_counter FROM dataset_u_new WHERE propaganda=TRUE")
        neg_counter = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM dataset_u_new WHERE propaganda IS NULL")

        unclf_counter = cur.fetchone()[0]
        cur.close()
        div = neg_counter+pos_counter
        await message.reply(f'russian messages: {int(neg_counter*100/div)}%\n'
                            f'normal messages: {int(pos_counter*100/div)}%\n'
                            f'messages counter: {div}\n'
                            f'unclassified messages: {unclf_counter}')

        conn.close()

@app.on_message(filters.text)
async def function(client, message):

    button_ls = ["Russian", "Cancel", "Ukrainian"]


    if message.chat.username in ['Always_chillingUP', 'Irynchuk', 'sonja_su', 'nightraypng']:
        conn = pg.connect(**conf['DATABASE'])
        cur = conn.cursor()
        # print(message.text)
        if message.text == "Let's go!":
            await message.reply('start...')

            cur.execute('SELECT * FROM dataset_u_new WHERE propaganda IS NULL LIMIT 1')
            fetch_ls = cur.fetchall()
            await message.reply(fetch_ls[0][1], reply_markup=ReplyKeyboardMarkup([button_ls]))

        elif message.text in button_ls:

            cur.execute('SELECT * FROM dataset_u_new WHERE propaganda IS NULL LIMIT 1')
            fetch_ls = cur.fetchall()
            if message.text == "Russian":
                cur.execute(f"UPDATE dataset_u_new SET propaganda=TRUE WHERE id={fetch_ls[0][0]}")
            elif message.text == 'Ukrainian':
                cur.execute(f"UPDATE dataset_u_new SET propaganda=FALSE WHERE id={fetch_ls[0][0]}")
            else:
                cur.execute(f"DELETE FROM dataset_u_new WHERE id={fetch_ls[0][0]}")

            conn.commit()
            cur.execute('SELECT * FROM dataset_u_new WHERE propaganda IS NULL LIMIT 1')
            fetch_ls = cur.fetchall()
            cur.close()
            await message.reply(fetch_ls[0][1])

        conn.close()



if __name__ == '__main__':
    if 'my_account.session' in os.listdir():
        os.remove('my_account.session')
    if 'my_account.session-journal' in os.listdir():
        os.remove('my_account.session-journal')
    app.run()