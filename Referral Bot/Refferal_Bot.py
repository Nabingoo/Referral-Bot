#from asyncio.windows_events import NULL
import os
import discord
from discord.ext import commands
from discord import Embed
import time
import sqlite3
from typing import Optional
conn = sqlite3.connect('referral.db')
print ("Opened database successfully");


intents = discord.Intents.default()

bot = commands.Bot(command_prefix = "?", intents = intents)


@bot.command()
#async def invites(ctx, member: discord.Member=None):
async def invites(ctx, member: Optional[discord.User]):  
 # v_ref_count_mem_ID = member.id
 # if v_ref_count_mem_ID is None:
  if member is None:
    v_ref_count_mem_ID = ctx.author.id
    v_surname = ctx.author.display_name
    v_avatar_url = ctx.author.avatar_url
  else :
    v_ref_count_mem_ID = member.id
    v_surname = member.display_name
    v_avatar_url = member.avatar_url
  cursor = conn.execute('select Ref_Count , Discord_ID from referral_log where Discord_ID=? limit 1',[v_ref_count_mem_ID])
  v_ref_mem_ID_invite = ''
  for row in cursor:
        v_ref_Tot_count = row[0] 
        v_ref_mem_ID_invite = row[1]
  if v_ref_mem_ID_invite == '':
    embed=discord.Embed(title="The User Does not have Referral Code, Use ?generate to generate code!", description= 'Use - ?generate', color=discord.Color.dark_grey())
    await ctx.send(embed=embed)
  else:
   embed=discord.Embed(title="Current Invites Redeemed:", description= v_ref_Tot_count, color=discord.Color.dark_grey())
   embed.set_author(name=v_surname, icon_url=v_avatar_url)
   await ctx.send(embed=embed)
#    await ctx.send(v_ref_Tot_count)

@bot.command()
async def generate(ctx):
    v_discord_ID = ctx.author.id
    v_ref_dup = ''
    cursor = conn.execute('select Ref_Count , Discord_ID from referral_log where Discord_ID=? limit 1',[v_discord_ID])
    for row in cursor:
          v_ref_dup = row[0] 
    if v_ref_dup != '':
      embed=discord.Embed(title="User can not generate more than one code!", description= 'Use - ?mycode to get your previously generated code', color=discord.Color.dark_grey())
      await ctx.send(embed=embed)
    else:
      cursor = conn.execute("select Referral_ID, Discord_ID, Ref_Count from Referral_Log where Discord_ID IS NULL LIMIT 1")
      for row in cursor:

          v_referral_key = row[0] 
      
    # await print ("Operation done successfully")
      embed=discord.Embed(title="Referral code:", description= row[0], color=discord.Color.dark_grey())
      embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
      await ctx.send(ctx.author.mention,embed=embed)
    

    # v_referral_key = row[2]
      cursor = conn.execute('''update Referral_Log set Discord_ID=? , Ref_Count = 0 where Referral_ID=?''',(v_discord_ID,v_referral_key))
      conn.commit()


@bot.command()
async def redeem(ctx, *, content:str):
  v_content = content
  v_dark_greylist = ctx.author.id
  v_Discord_dark_greylist = ''
  if time.time() - ctx.author.created_at.timestamp() < 1209600:
    embed=discord.Embed(title="The User is younger than 2 weeks.", description= 'You cannot redeem a code', color=discord.Color.dark_grey())
    await ctx.send(embed=embed)
  else:
   # User can not redeem their own Code
    v_own_user_redeem = ''
    cursor = conn.execute('select Referral_ID from referral_log where Discord_ID=? limit 1',[v_dark_greylist])
    for row in cursor:
        v_own_user_redeem = row[0] 
    if v_own_user_redeem == v_content: 
        embed=discord.Embed(title="Use cannot use your own Code!", description= v_own_user_redeem, color=discord.Color.dark_grey())
        await ctx.send(embed=embed)        
    else:       
      cursor = conn.execute('select Discord_ID from referral_used_id where Discord_ID=? limit 1',[v_dark_greylist])
      for row in cursor:
          v_Discord_dark_greylist = row[0] 
      if v_Discord_dark_greylist != '':
        
        #ctx.author.id in dark_greylist:
          embed=discord.Embed(title="User has already used a code!", description= 'Youve already used a code and cannot use another.', color=discord.Color.dark_grey())
          await ctx.send(embed=embed)
      else:
          v_referral_key = ''

          cursor = conn.execute('select Referral_ID from Referral_Log where Referral_ID=?',[v_content])
          for row in cursor:
              v_referral_key = row[0] 
          if v_referral_key != '':
      
        #  v_referral_key = content
        # v_referral_key = row[2]
            cursor = conn.execute('''update Referral_Log set Ref_Count = Ref_Count + 1 where Referral_ID=?''',[v_referral_key])
            conn.commit()   
        #Insert in Used List Table (dark_grey List) 
            cursor = conn.execute('''INSERT INTO Referral_Used_ID (Discord_ID) VALUES (?)''',[v_dark_greylist])
            conn.commit()        
            embed=discord.Embed(title="Code Accepted!", description= 'The code has been accepted', color=discord.Color.green())
            await ctx.send(embed=embed)

          else:
            embed=discord.Embed(title="Code Rejected!", description= 'The code is invalid/doesnt work.', color=discord.Color.red())
            await ctx.send(embed=embed)

@bot.command()
async def checkage(ctx):
  if time.time() - ctx.author.created_at.timestamp() < 1209600:
    await ctx.send("Younger than 2 weeks")
  else:
    await ctx.send("Good to go! Older than 2 weeks")

   
@bot.command()
async def userid(ctx, member: discord.User): 
  await ctx.send(member.id)

@bot.command()
async def commandlist(ctx):
  embed=discord.Embed(title="Command List", description="All Commands must be in lowercase \n \n ?mycode - shows your code. \n ?generate - generates code that you can share with friends. \n ?redeem (code) - This command followed by a code gives the codes owner an invite point. \n ?invites - shows how many invites you have \n", color=discord.Color.dark_grey())
  embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
  await ctx.send(embed=embed) 

@bot.command()
async def mycode(ctx):
    v_req_user_id = ctx.author.id
    v_own_user_Code = ''
    cursor = conn.execute('select Referral_ID from referral_log where Discord_ID=? limit 1',[v_req_user_id])
    for row in cursor:
        v_own_user_Code = row[0] 
    if v_own_user_Code == '':
      embed=discord.Embed(description="You don't have a code.\n \n Use "'"?generate"'"  \n", color=discord.Color.dark_grey())
      embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
      await ctx.send(embed=embed) 
    else:
      embed=discord.Embed(title="Referral code:", description= v_own_user_Code, color=discord.Color.dark_grey())
      embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
      await ctx.send(ctx.author.mention,embed=embed)


@bot.command()
async def test(ctx):
  await ctx.send("test")


#bot.run(os.getenv('TOKEN'))
bot.run("OTM2ODAwMzk1MjExMTkwMzQy.YfSdWw.2hl7UptgeV7RMLaZctZDnwGPLVA")



