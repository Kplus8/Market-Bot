# main.py
import os
import random
import sys

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
        if ctx.author.name == "Kplus8":
            if int(gained[1]) + int(gained[3]) + int(gained[4]) < 2:
                total_gains = 0

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
        await ctx.send("Current leading bid is from " + current_bidder[x] + " for " + x + " at: " + str(current_bid[x]) + "g")

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
                "Current leading bid is from " + current_bidder[item_bid] + " for " + item_bid + " at: " + str(current_bid[item_bid]))
        else:
            await ctx.send(
                "That is not a high enough bid for that item.\nIt is currently held by: " + current_bidder[item_bid] + " for " + item_bid + " at: " + str(current_bid[item_bid]) + ". You must outbid by "+ str(over_amount) + " in order to take the lead.")
    else:
        await ctx.send(item_bid + " is not currently in auction. Make sure you are spelling it correctly & try again. (Tips:\n1. case matters, make sure to capitalize it\n2. Enclose the item in \"\" if it contains more than one word. EG: \"Silver Sword\")")


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
            price = int(inventory[key])*reg_discount
        else:
            key = item
            price = int(type_price[key])*price_mod
        current_bidder[key] = ""
        current_bid[key] = int(price)
        await ctx.send("The starting bid for "+ key + " is: " + str(current_bid[key]) + " g")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(
            'You did not provide all the required parameters. use !help {command} to confirm what is required')
    #else:
        #await ctx.send('unspecified error has occurred')


bot.run(TOKEN)
