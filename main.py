# main.py
import os
import random
import sys
import gspread

import discord
from discord.ext import commands
from dotenv import load_dotenv


def gen_item(inven, amount):
    items = []
    for x in range(0, amount):
        items.append(random.choice(list(inven)))
    return items


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='$')

file = "Inven_chance.csv"
file2 = "inven_price.csv"
hold = []
hold2 = []
try:
    with open(file) as f:
        hold = [line.rstrip('\n') for line in f]
        f.close()
except:
    sys.stderr.write("FileError\n")
    sys.exit(1)

try:
    with open(file2) as f:
        hold2 = [line.rstrip('\n') for line in f]
        f.close()
except:
    sys.stderr.write("FileError\n")
    sys.exit(1)
global current_bid
current_bid = {}
global current_bidder
current_bidder = {}

inven_chance = {}
type_price = {}
inventory = {}
sum = 0
for x in hold:
    holder = x.split(',')
    sum += int(holder[1])
    inven_chance[sum] = holder[0]
    type_price[holder[0]] = holder[2]
for x in hold2:
    holder2 = x.split(',')
    inventory[holder2[0]] = holder2[1]

##Sheets Stuff##

gc = gspread.service_account(filename='gsheets.json')

sh = gc.open('turn actions')

ev = gc.open('Event Table')

players = {
    "Norm": 1,
    "Chibi": 2,
    "Sarki Soliloquy": 3,
    "Husky": 4,
    "Kplus8": 5,
    "Shiny": 6
}

@bot.command(name='refresh_events', help='For shuffling event order on a new turn')
@commands.has_role('GM')
async def shuffle(ctx):
    worksheet = ev.get_worksheet(0)

    for x in range(4, 7):
        store = []
        for y in range(2, 8):
            store.append(worksheet.cell(y, x).value)
        random.shuffle(store)
        for y in range(2, 8):
            worksheet.update_cell(y, x, store.pop())


@bot.command(name='submit_event_roll', help='Sending event rolls to table')
@commands.has_role('Season 4 Player')
async def sub_event(ctx, turn: int, event_desc: str):
    # determine sheet_num based on user
    name = ctx.author.name

    sheet_num = players[name]

    worksheet = sh.get_worksheet(sheet_num)

    if worksheet.cell(turn + 1, 9).value is None:
        worksheet.update_cell(turn + 1, 2, event_desc)
        await ctx.send("Recorded event for turn: " + str(turn))


@bot.command(name='submit_single_action', help='Sending one character action to table')
@commands.has_role('Season 4 Player')
async def sub_action_single(ctx, turn: int, char_name: str, action: str):
    # determine sheet_num based on user
    name = ctx.author.name

    sheet_num = players[name]

    worksheet = sh.get_worksheet(sheet_num)
    char_cell = worksheet.find(char_name)
    if char_cell is None:
        await ctx.send(
            "Error, incorrect character name. Use `$chars` to check what the bot is looking for with the names")
    if worksheet.cell(turn + 1, 9).value is None:
        worksheet.update_cell(turn + 1, char_cell.col, action)
        await ctx.send("Recorded action for " + char_name + " on turn: " + str(turn))


@bot.command(name='submit_actions', help='Sending all character actions to table. Format for action_input is "Unit1 - Action1, Unit2 - Action2"')
@commands.has_role('Season 4 Player')
async def sub_actions(ctx, turn: int, action_input: str):
    # determine sheet_num based on user
    name = ctx.author.name

    sheet_num = players[name]

    worksheet = sh.get_worksheet(sheet_num)

    action_list = action_input.split(", ")

    for action in action_list:
        action_parts = action.split(" - ")
        char_name = action_parts[0]
        action_desc = action_parts[1]

        char_cell = worksheet.find(char_name)
        if char_cell is None:
            await ctx.send(
                "Error, incorrect character name. Use `$chars` to check what the bot is looking for with the names")

        if worksheet.cell(turn + 1, 9).value is None:
            worksheet.update_cell(turn + 1, char_cell.col, action_desc)
            await ctx.send("Recorded action for " + char_name + " on turn: " + str(turn))
        else:
            await ctx.send("This turn is not valid to be submitted to, if this is wrong, contact a GM")
            break


@bot.command(name='lock', help='Locking in actions for the turn')
@commands.has_role('Season 4 Player')
async def sub_actions(ctx, turn: int):
    # determine sheet_num based on user
    name = ctx.author.name
    sheet_num = players[name]
    worksheet = sh.get_worksheet(sheet_num)
    worksheet.update_cell(turn + 1, 9, "Y")
    await ctx.send("Locked in turn " + str(turn))

@bot.command(name='chars', help='Showing a player what names the bot is expecting')
@commands.has_role('Season 4 Player')
async def show_chars(ctx):
    # determine sheet_num based on user
    name = ctx.author.name

    sheet_num = players[name]

    worksheet = sh.get_worksheet(sheet_num)

    loc_list = [3, 4, 5, 6, 7]
    char_list = ""
    for i in loc_list:
        char_list += worksheet.cell(1, i).value + ", "
    char_list = char_list.removeprefix(", ")
    await ctx.send(char_list)


##Sheets Stuff##

##generic die roller, for reference not use
# @bot.command(name='roll_dice', help='Simulates rolling dice.')
# async def roll(ctx, number_of_dice: int, number_of_sides: int):
#     dice = [
#         str(random.choice(range(1, number_of_sides + 1)))
#         for _ in range(number_of_dice)
#     ]
#     await ctx.send(', '.join(dice))

# level up system.
@bot.command(name='roll_levels',
             help='For doing level ups more quickly than with AVARE.')
async def level(ctx, hp_growth: int, str_growth: int, mag_growth: int, skl_growth: int, spd_growth: int,
                lck_growth: int, def_growth: int, res_growth: int):
    growths = [hp_growth, str_growth, mag_growth, skl_growth, spd_growth, lck_growth, def_growth, res_growth]

    total_gains = 0
    while total_gains < 2:
        rolls = [
            random.choice(range(1, 101))
            for _ in range(0, 8)
        ]
        gained = [
            False
            for _ in range(0, 8)
        ]
        for x in range(0, 8):
            if rolls[x] <= growths[x]:
                gained[x] = True
                total_gains += 1

    out1 = "HP: " + str(rolls[0]) + ', ' + "Str: " + str(rolls[1]) + ', ' + "Mag: " + str(
        rolls[2]) + ', ' + "Skl: " + str(rolls[3]) + ', ' + "Spd: " + str(rolls[4]) + ', ' + "Lck: " + str(
        rolls[5]) + ', ' + "Def: " + str(rolls[6]) + ', ' + "Res: " + str(rolls[7])

    out = "HP: " + str(gained[0]) + '\n' + "Str: " + str(gained[1]) + '\n' + "Mag: " + str(
        gained[2]) + '\n' + "Skl: " + str(gained[3]) + '\n' + "Spd: " + str(gained[4]) + '\n' + "Lck: " + str(
        gained[5]) + '\n' + "Def: " + str(gained[6]) + '\n' + "Res: " + str(gained[7])

    await ctx.send(out1)
    await ctx.send(out)


@bot.command(name='bid_check', help='To see what the current bids are')
@commands.has_role('Season 4 Player')
async def bid_check(ctx):
    for x in current_bid:
        await ctx.send(
            "Current leading bid is from " + current_bidder[x] + " for " + x + " at: " + str(current_bid[x]) + "g")


@bot.command(name='event_roll', help='Randomizing event rolls')
@commands.has_role('Season 4 Player')
async def event(ctx):
    severity = random.choice(range(1, 21))
    option = random.choice(range(1, 7))

    sev_loc = 0
    if severity < 9:
        sev_loc = 4
    elif severity < 13:
        sev_loc = 5
    elif severity < 19:
        sev_loc = 6
    else:
        sev_loc = 7

    worksheet = ev.get_worksheet(0)
    outcome = worksheet.cell(option + 1, sev_loc).value

    await ctx.send("type roll was: " + str(severity) + ". Option roll was: " + str(option) + ". Event was: " + outcome)


@bot.command(name='bid', help='To put in money into the item bidding')
@commands.has_role('Season 4 Player')
async def bid(ctx, bid_amount: int, item_bid):
    global current_bid
    global current_bidder
    name = ctx.author.name
    over_amount = 50

    if item_bid in current_bid:
        if current_bid[item_bid] + over_amount <= bid_amount:
            current_bidder[item_bid] = ctx.author.name
            current_bid[item_bid] = bid_amount
            await ctx.send(
                "Current leading bid is from " + current_bidder[item_bid] + " for " + item_bid + " at: " + str(
                    current_bid[item_bid]))
        else:
            await ctx.send(
                "That is not a high enough bid for that item.\nIt is currently held by: " + current_bidder[
                    item_bid] + " for " + item_bid + " at: " + str(
                    current_bid[item_bid]) + ". You must outbid by " + str(over_amount) + " in order to take the lead.")
    else:
        await ctx.send(
            item_bid + " is not currently in auction. Make sure you are spelling it correctly & try again. (Tips:\n1. case matters, make sure to capitalize it\n2. Enclose the item in \"\" if it contains more than one word. EG: \"Silver Sword\")")


@bot.command(name='redo_mid_bid', help='For repopulating when the bot drops the current bid')
@commands.has_role('GM')
async def restock(ctx, items):
    global current_bid
    global current_bidder
    current_bidder = {}
    current_bid = {}
    new_stock = []
    new_stock = items.split("; ")
    for count in range(0, len(new_stock)):
        new_stock[count] = new_stock[count].split(", ")

    for count in range(0, len(new_stock)):
        new_bid = new_stock[count]
        current_bidder[new_bid[1]] = new_bid[0]
        current_bid[new_bid[1]] = int(new_bid[2])
    await ctx.send("Redone")


@bot.command(name='decide_stock', help='For generating the items to be in stock this turn')
@commands.has_role('GM')
async def stock(ctx, number_generated: int):
    global current_bid
    global current_bidder
    current_bidder = {}
    current_bid = {}
    price_mod = 0.7
    reg_discount = 0.6
    items = [
        random.choice(range(1, 101))
        for _ in range(0, number_generated)
    ]
    stock = []
    normal_count = 0
    for x in items:
        while x not in inven_chance.keys():
            x += 1
        stock.append(inven_chance[x])
        if inven_chance[x] == "Discounted Normal Item":
            normal_count += 1
    reg_items = gen_item(inventory, normal_count)
    reg_item_count = 0
    for item in stock:
        key = ""
        price = 0
        if item == "Discounted Normal Item":
            key = reg_items[reg_item_count]
            reg_item_count += 1
            price = int(inventory[key]) * reg_discount
        else:
            key = item
            price = int(type_price[key]) * price_mod
        current_bidder[key] = ""
        current_bid[key] = int(price)
        await ctx.send("The starting bid for " + key + " is: " + str(current_bid[key]) + " g")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(
            'You did not provide all the required parameters. use !help {command} to confirm what is required')
    # else:
    # await ctx.send('unspecified error has occurred')


bot.run(TOKEN)
