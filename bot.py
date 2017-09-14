import discord
import asyncio
import configparser
import os.path
import random
config = configparser.ConfigParser()
config.read('config.ini')
bot_token = config['settings']['bot_token']
moderator_role = config['settings']['moderator_role']
admin_role = config['settings']['admin_role']
team_captain = config['settings']['team_captain']
game_playing = config['settings']['game_playing']

vraag_titel = config['vraag']['titel']
thumbnail = config['vraag']['thumbnail']
naam = config['vraag']['naam']
server_icoon = config['vraag']['server_icoon']
voetnoot = config['vraag']['voetnoot']

server_id = config['settings']['server_id']

client = discord.Client()
@client.event
async def on_ready():
    print('LindaBot is gereed')
    await client.change_presence(game=discord.Game(name=game_playing,type=0))
@client.event
async def on_message(message):
    global discord_message
    discord_message = message
    server = client.get_server(server_id)
    author_id = message.author.id
    member = server.get_member(author_id)
    for role in member.roles:
        if message.content.startswith(';startvraag') and (str(role.id) == admin_role or str(role.id) == moderator_role):
            await vraag()
        if message.content.startswith(';addscore') and (str(role.id) == admin_role or str(role.id) == moderator_role):
            await add_score()
        if message.content.startswith(';removescore') and (str(role.id) == moderator_role or str(role.id) == admin_role):
            await remove_score()
        if message.content.startswith(';geefantwoorden') and (str(role.id) == moderator_role or str(role.id) == admin_role):
            await return_antwoorden()
        if message.content.startswith(';antwoord') and (str(role.id) == moderator_role or str(role.id) == team_captain):
            await antwoord()
        if message.content.startswith(';rad') and (str(role.id) == admin_role):
            await rad()
    if message.content.startswith(';uitleg'):
        user = await client.get_user_info(author_id)
        em = discord.Embed(title='Uitleg',description='**Start een vraag (Alleen voor admins):** ''\n;startvraag <kanaal_id> <vraag_id> <vraag>\n''Voorbeeld: ;startvraag 337674017399898113 vraag1 Is dit is een vraag?\n\n''**Beantwoord een vraag:**\n'';antwoord <vraag_id> <antwoord>\n''Voorbeeld: ;antwoord vraag1 Ja, dit is een vraag\n\n''**Verkrijg de antwoorden (Alleen voor admins):**\n'';geefantwoorden <vraag_id>\n''Voorbeeld: ;geefantwoorden vraag1\n\n''**Krijg deze uitleg:**\n'';uitleg\n\n**Voeg een score toe (Alleen voor admins):**\n;addscore <naam> <hoeveelheid>\nVoorbeeld: ;addscore auxim 10\n\n'"**Laat jouw of een ander z'n score zien:**\n;geefscore [naam]"'\n\n**Laat de top-3 zien:**\n;highscore' )
        await client.send_message(user, embed=em)
    if message.content.startswith(';geefscore'):
        await show_score()
    if message.content.startswith(';highscore'):
        await get_highscore()
async def vraag():
    global discord_message
    author_id = discord_message.author.id
    message_user = await client.get_user_info(str(author_id))
    split_bericht_raw = discord_message.content.split()
    try:kanaal = split_bericht_raw[1]
    except IndexError as e:
        await client.send_message(message_user,'Je hebt geen kanaal id ingevuld')
        return
    split_bericht_raw.remove(';startvraag')
    split_bericht_raw.remove(kanaal)
    try:vraag_id = split_bericht_raw[0]
    except IndexError as e:
        await client.send_message(message_user, 'Je hebt geen vraag id ingevuld.')
        return
    split_bericht_raw.remove(vraag_id)
    split_bericht = ' '.join(split_bericht_raw)
    if split_bericht == '':
        await client.send_message(message_user,'Vragen kunnen niet leeg zijn')
    else:
        antwoord_file = configparser.ConfigParser()
        antwoord_file.read(vraag_id + '.ini')
        if vraag_id == 'config':
            print('mgw iemand grappig probeert te doen')
            await client.send_message(message_user, 'Haha grappig leuk geprobeerd')
        elif '/' in vraag_id:
            with open('hackerman.png', 'rb') as f:
                print('mgw iemand grappig probeert te doen')
                await client.send_file(message_user, f, content='Ook nu was ik je te slim af meneer de')
        elif 'score' in vraag_id:
            print('mgw iemand grappig probeert te doen')
            with open('Hal9000.jpg', 'rb') as f:
                await client.send_file(message_user, f,
                                       content='Het spijt me ' + str(author_name) + ', ik ben bang dat ik dat niet kan doen')
        else:
            with open(vraag_id + '.ini', 'w') as antwoordfile:
                antwoord_file.write(antwoordfile)
            em = discord.Embed(title=vraag_titel, description=split_bericht, colour=0xff8100)
            em.set_thumbnail(url=thumbnail)
            em.set_author(name=naam,icon_url=client.user.avatar_url)
            em.add_field(name='Uitleg:',value='Beantwoordt mij met ;antwoord ' + vraag_id + " 'jouw antwoord'. Stuur dit in een direct bericht naar mij.")
            em.set_footer(text=voetnoot, icon_url=server_icoon)
            await client.send_message(client.get_channel(kanaal), embed=em)
async def antwoord():
    global discord_message
    author_id = discord_message.author.id
    message_user = await client.get_user_info(str(author_id))
    split_bericht_raw = discord_message.content.split()
    split_bericht_raw.remove(';antwoord')
    try:vraag_id = split_bericht_raw[0]
    except IndexError as e:
        await client.send_message(message_user, 'Je hebt geen vraag id ingevuld.')
        return
    split_bericht_raw.remove(vraag_id)
    split_bericht = ' '.join(split_bericht_raw)
    antwoord_file = configparser.ConfigParser()
    if os.path.isfile(vraag_id+'.ini') == False:
        await client.send_message(message_user,'Dit vraag id bestaat niet.')
        return
    antwoord_file.read(vraag_id + '.ini')
    timestamp = discord_message.timestamp
    author_name = discord_message.author
    try:
        antwoord_file.add_section(author_id)
        antwoord_file.set(str(author_id),'antwoord',str(split_bericht))
        antwoord_file.set(str(author_id),'timestamp',str(timestamp))
        antwoord_file.set(str(author_id),'username',str(author_name))
        if vraag_id == 'config':
            print('mgw iemand grappig probeert te doen')
            await client.send_message(message_user,'Haha grappig leuk geprobeerd')
        elif '/' in vraag_id:
            print('mgw iemand grappig probeert te doen')
            with open('hackerman.png', 'rb') as f:
                await client.send_file(message_user, f, content='Ook nu was ik je te slim af meneer de')
        elif 'score' in vraag_id:
            print('mgw iemand grappig probeert te doen')
            with open('Hal9000.jpg', 'rb') as f:
                await client.send_file(message_user, f, content='Het spijt me ' + str(author_name) + ', ik ben bang dat ik dat niet kan doen')
        else:
            with open(vraag_id + '.ini','w') as antwoordfile:
                antwoord_file.write(antwoordfile)
            await client.send_message(message_user,'Je antwoord is met succes ontvangen')
    except configparser.DuplicateSectionError:
        await client.send_message(message_user,'Het is niet toegestaan om je antwoord achteraf aan te passen')
async def return_antwoorden():
    global discord_message
    split_bericht_raw = discord_message.content.split()
    author_id = discord_message.author.id
    message_user = await client.get_user_info(str(author_id))
    try:
        if split_bericht_raw[1] == 'config':
            print('mgw iemand grappig probeert te doen')
            await client.send_message(message_user,'Haha grappig leuk geprobeerd')
        elif '/' in split_bericht_raw[1]:
            print('mgw iemand grappig probeert te doen')
            with open('hackerman.png', 'rb') as f:
                await client.send_file(message_user,f,content='Ook nu was ik je te slim af meneer de')
        else:
            with open(split_bericht_raw[1] + '.ini', 'rb') as f:
                await client.send_file(message_user, f)
    except IndexError as e:
        await client.send_message(message_user, 'Je hebt geen vraag id ingevuld.')
async def add_score():
    global discord_message
    split_bericht_raw = discord_message.content.split()
    split_bericht_raw.remove(';addscore')
    try:person = split_bericht_raw[0]
    except IndexError:
        await client.send_message(await client.get_user_info(discord_message.author.id),'U heeft geen persoon ingevuld')
        return
    try:score_add = split_bericht_raw[1]
    except IndexError:
        await client.send_message(await client.get_user_info(discord_message.author.id),'U heeft geen score ingevuld')
        return
    score_ini = configparser.ConfigParser()
    score_ini.read('score.ini')
    member = discord.utils.find(lambda m: person.lower() in m.name.lower(), discord_message.channel.server.members)
    if member == None:
        await client.send_message(discord_message.channel,'De gebruiker kon niet worden gevonden, probeer het nogmaals.')
        return
    if str(member) not in score_ini:
        score_ini.add_section(str(member))
        score_ini.set(str(member),'score',"")
        score_ini.set(str(member), 'nick', str(member.nick))
    old_score = score_ini.get(str(member),'score')
    if old_score == "":
        score_ini.set(str(member),'score',str(score_add))
        score_ini.set(str(member), 'nick', str(member.nick))
        with open('score.ini', 'w') as scorefile:
            score_ini.write(scorefile)
        await client.send_message(await client.get_user_info(discord_message.author.id), 'De score is ontvangen')
        return
    else:
        new_score = int(old_score) + int(score_add)
        score_ini.set(str(member),'score',str(new_score))
        score_ini.set(str(member),'nick',str(member.nick))
        with open('score.ini', 'w') as scorefile:
            score_ini.write(scorefile)
        await client.send_message(await client.get_user_info(discord_message.author.id), 'De score is ontvangen')
        return
async def remove_score():
    global discord_message
    split_bericht_raw = discord_message.content.split()
    split_bericht_raw.remove(';addscore')
    try:
        person = split_bericht_raw[0]
    except IndexError:
        await client.send_message(await client.get_user_info(discord_message.author.id),
                                  'U heeft geen persoon ingevuld')
        return
    try:
        score_add = split_bericht_raw[1]
    except IndexError:
        await client.send_message(await client.get_user_info(discord_message.author.id), 'U heeft geen score ingevuld')
        return
    score_ini = configparser.ConfigParser()
    score_ini.read('score.ini')
    member = discord.utils.find(lambda m: person.lower() in m.name.lower(), discord_message.channel.server.members)
    if member == None:
        await client.send_message(discord_message.channel,
                                  'De gebruiker kon niet worden gevonden, probeer het nogmaals.')
        return
    old_score = score_ini.get(str(member), 'score')
    new_score = int(old_score) - int(score_add)
    score_ini.set(str(member), 'score', str(new_score))
    score_ini.set(str(member), 'nick', str(member.nick))
    with open('score.ini', 'w') as scorefile:
        score_ini.write(scorefile)
    await client.send_message(await client.get_user_info(discord_message.author.id), 'De score is ontvangen')
    return
async def show_score():
    global discord_message
    try:
        person = discord_message.content.split()[1]
        member = discord.utils.find(lambda m: person.lower() in m.name.lower(), discord_message.channel.server.members)
    except IndexError: member = discord_message.author
    willemsliefde_url = 'https://images-ext-1.discordapp.net/external/zHhFSN2tR8Tzf04n8ixC2ojx8F4wgduhwe8gA1xnidQ/https/discordapp.com/api/guilds/241646621283057665/icons/1e9d098418935865503213beee2d5023.jpg?'
    score_ini = configparser.ConfigParser()
    score_ini.read('score.ini')
    if member == None:
        await client.send_message(discord_message.channel,'De gebruiker kon niet worden gevonden, probeer het nogmaals.')
        return
    if str(member) not in score_ini:
        em = discord.Embed(title='Jouw score is: 0',colour=0xff8100)
        em.set_thumbnail(url='http://www.hulsbeekevents.nl/wp-content/uploads/2013/02/ihvh.png')
        em.set_author(name=str(member), icon_url=member.avatar_url)
        em.set_footer(text='Willemsliefde: Ik hou van Holland | Bot door Auxim#2994', icon_url=willemsliefde_url)
        await client.send_message(discord_message.channel, embed=em)
    else:
        score = score_ini.get(str(member),'score')
        em = discord.Embed(title='Jouw score is: ' + score,colour=0xff8100)
        em.set_thumbnail(url='http://www.hulsbeekevents.nl/wp-content/uploads/2013/02/ihvh.png')
        em.set_author(name=str(member), icon_url=member.avatar_url)
        em.set_footer(text='Willemsliefde: Ik hou van Holland | Bot door Auxim#2994', icon_url=willemsliefde_url)
        await client.send_message(discord_message.channel,embed=em)
async def get_highscore():
    global discord_message
    score_ini = configparser.ConfigParser()
    score_ini.read('score.ini')
    nicks = []
    all_score = []
    members = []
    for member in score_ini.sections():
        scores = score_ini.get(member,'score')
        nick = score_ini.get(member,'nick')
        all_score.append(scores)
        members.append(member)
        nicks.append(nick)
    all_score_int = list(map(int, all_score))
    top_score = max(all_score_int)
    top_score_index = all_score_int.index(top_score)
    top_score_member = members[top_score_index]
    top_score_nick = nicks[top_score_index]
    members.remove(top_score_member)
    all_score_int.remove(top_score)
    nicks.remove(top_score_nick)
    second_place = max(all_score_int)
    second_place_index = all_score_int.index(second_place)
    second_place_member = members[second_place_index]
    second_place_nick = nicks[second_place_index]
    members.remove(second_place_member)
    all_score_int.remove(second_place)
    nicks.remove(second_place_nick)
    third_place = max(all_score_int)
    third_place_index = all_score_int.index(third_place)
    third_place_member = members[third_place_index]
    third_place_nick = nicks[third_place_index]
    members.remove(third_place_member)
    all_score_int.remove(third_place)
    nicks.remove(third_place_nick)
    fourth_place = max(all_score_int)
    fourth_place_index = all_score_int.index(fourth_place)
    fourth_place_member = members[fourth_place_index]
    fourth_place_nick = nicks[fourth_place_index]
    em = discord.Embed(title='Highscores:', colour=0xff8100)
    em.set_thumbnail(url=thumbnail)
    em.set_footer(text=voetnoot, icon_url=server_icoon)
    em.add_field(name=':first_place: ' + top_score_nick,value='Met een score van: ' + str(top_score))
    em.add_field(name=':second_place: ' + second_place_nick, value='Met een score van: ' + str(second_place))
    em.add_field(name=':third_place: ' + third_place_nick, value='Met een score van: ' + str(third_place))
    em.add_field(name=':poop: ' + fourth_place_nick, value='Met een score van: ' + str(fourth_place))
    await client.send_message(discord_message.channel,embed=em)
#Rad is een functie die later werd gedaan door wheel decide, deze functie is dus nooit uitgewerkt, en is dus verder onaangeraakt, maar hij werkt wel. Je moet alleen wel zelf in de code de juiste emote id's aangeven,
#wat best een kuttaak kan zijn oetz.
async def rad():
    global discord_message
    split_bericht_raw = discord_message.content.split()
    split_bericht_raw.remove(';rad')
    try:
        person = split_bericht_raw[0]
    except IndexError:
        await client.send_message(await client.get_user_info(discord_message.author.id),
                                  'U heeft geen persoon ingevuld')
        return
    member = discord.utils.find(lambda m: person.lower() in m.name.lower(), discord_message.channel.server.members)
    if member == None:
        await client.send_message(discord_message.channel,
                                  'De gebruiker kon niet worden gevonden, probeer het nogmaals.')
        return
    em = discord.Embed(title='Het Rad',colour=0xff8100,description='‌‌ ‌‌ ‌‌ ‌‌ ‌‌‌  ‌‌ ‌‌ 🔽\n<:grinnik:355763575215620107><:Alleskwijt:355763574162849793><:zelfgenoegzaam:355763575916331038>\n'
                                                                           '<:Noot:355763576134303744><:rad:355763575886708747><:oplinda:355763576520310794>\n'
                                                                        '<:Lust:355763576494882816><:handelmethet:355763575970856960><:Goedkeuring:355763575534387200>')
    willemsliefde_url = 'https://images-ext-1.discordapp.net/external/zHhFSN2tR8Tzf04n8ixC2ojx8F4wgduhwe8gA1xnidQ/https/discordapp.com/api/guilds/241646621283057665/icons/1e9d098418935865503213beee2d5023.jpg?'
    em.set_footer(text='Willemsliefde: Ik hou van Holland | Bot door Auxim#2994', icon_url=willemsliefde_url)
    em.set_author(name='Linda de Mol', icon_url=client.user.avatar_url)
    old_message = await client.send_message(client.get_channel('241934226721603584'),embed=em)
    await asyncio.sleep(2)
    em2 = discord.Embed(title='Het Rad',colour=0xff8100,description='‌‌ ‌‌ ‌‌ ‌‌ ‌‌‌  ‌‌ ‌‌ 🔽\n<:Noot:355763576134303744><:grinnik:355763575215620107><:Alleskwijt:355763574162849793>\n'
                                                  '<:Lust:355763576494882816><:rad:355763575886708747><:zelfgenoegzaam:355763575916331038>\n'
                                                  '<:handelmethet:355763575970856960><:Goedkeuring:355763575534387200><:oplinda:355763576520310794>')
    em2.set_footer(text='Willemsliefde: Ik hou van Holland | Bot door Auxim#2994', icon_url=willemsliefde_url)
    em2.set_author(name='Linda de Mol', icon_url=client.user.avatar_url)
    await client.edit_message(old_message, embed=em2)
    await asyncio.sleep(2)
    em3 = discord.Embed(title='Het Rad', colour=0xff8100,
                            description='‌‌ ‌‌ ‌‌ ‌‌ ‌‌‌  ‌‌ ‌‌ 🔽\n<:Lust:355763576494882816><:Noot:355763576134303744><:grinnik:355763575215620107>\n'
                                        '<:handelmethet:355763575970856960><:rad:355763575886708747><:Alleskwijt:355763574162849793>\n'
                                        '<:Goedkeuring:355763575534387200><:oplinda:355763576520310794><:zelfgenoegzaam:355763575916331038>')
    em3.set_footer(text='Willemsliefde: Ik hou van Holland | Bot door Auxim#2994', icon_url=willemsliefde_url)
    em3.set_author(name='Linda de Mol', icon_url=client.user.avatar_url)
    await client.edit_message(old_message, embed=em3)
    await asyncio.sleep(2)
    em4 = discord.Embed(title='Het Rad', colour=0xff8100,
                        description='‌‌ ‌‌ ‌‌ ‌‌ ‌‌‌  ‌‌ ‌‌ 🔽\n<:handelmethet:355763575970856960><:Lust:355763576494882816><:Noot:355763576134303744>\n'
                                    '<:Goedkeuring:355763575534387200><:rad:355763575886708747><:grinnik:355763575215620107>\n'
                                    '<:oplinda:355763576520310794><:zelfgenoegzaam:355763575916331038><:Alleskwijt:355763574162849793>')
    em4.set_footer(text='Willemsliefde: Ik hou van Holland | Bot door Auxim#2994', icon_url=willemsliefde_url)
    em4.set_author(name='Linda de Mol', icon_url=client.user.avatar_url)
    await client.edit_message(old_message, embed=em4)
    await asyncio.sleep(2)
    em5 = discord.Embed(title='Het Rad', colour=0xff8100,
                        description='‌‌ ‌‌ ‌‌ ‌‌ ‌‌‌  ‌‌ ‌‌ 🔽\n<:Goedkeuring:355763575534387200><:handelmethet:355763575970856960><:Lust:355763576494882816>\n'
                                    '<:oplinda:355763576520310794><:rad:355763575886708747><:Noot:355763576134303744>\n'
                                    '<:zelfgenoegzaam:355763575916331038><:Alleskwijt:355763574162849793><:grinnik:355763575215620107>')
    em5.set_footer(text='Willemsliefde: Ik hou van Holland | Bot door Auxim#2994', icon_url=willemsliefde_url)
    em5.set_author(name='Linda de Mol', icon_url=client.user.avatar_url)
    await client.edit_message(old_message, embed=em5)
    await asyncio.sleep(2)
    em6 = discord.Embed(title='Het Rad', colour=0xff8100,
                        description='‌‌ ‌‌ ‌‌ ‌‌ ‌‌‌  ‌‌ ‌‌ 🔽\n<:oplinda:355763576520310794><:Goedkeuring:355763575534387200><:handelmethet:355763575970856960>\n'
                                    '<:zelfgenoegzaam:355763575916331038><:rad:355763575886708747><:Lust:355763576494882816>\n'
                                    '<:Alleskwijt:355763574162849793><:grinnik:355763575215620107><:Noot:355763576134303744>')
    em6.set_footer(text='Willemsliefde: Ik hou van Holland | Bot door Auxim#2994', icon_url=willemsliefde_url)
    em6.set_author(name='Linda de Mol', icon_url=client.user.avatar_url)
    await client.edit_message(old_message, embed=em6)
    await asyncio.sleep(2)
    em7 = discord.Embed(title='Het Rad', colour=0xff8100,
                        description='‌‌ ‌‌ ‌‌ ‌‌ ‌‌‌  ‌‌ ‌‌ 🔽\n<:zelfgenoegzaam:355763575916331038><:oplinda:355763576520310794><:Goedkeuring:355763575534387200>\n'
                                    '<:Alleskwijt:355763574162849793><:rad:355763575886708747><:handelmethet:355763575970856960>\n'
                                    '<:grinnik:355763575215620107><:Noot:355763576134303744><:Lust:355763576494882816>')
    em7.set_footer(text='Willemsliefde: Ik hou van Holland | Bot door Auxim#2994', icon_url=willemsliefde_url)
    em7.set_author(name='Linda de Mol', icon_url=client.user.avatar_url)
    await client.edit_message(old_message, embed=em7)
    await asyncio.sleep(2)
    em8 = discord.Embed(title='Het Rad', colour=0xff8100,
                        description='‌‌ ‌‌ ‌‌ ‌‌ ‌‌‌  ‌‌ ‌‌ 🔽\n<:Alleskwijt:355763574162849793><:zelfgenoegzaam:355763575916331038><:oplinda:355763576520310794>\n'
                                    '<:grinnik:355763575215620107><:rad:355763575886708747><:Goedkeuring:355763575534387200>\n'
                                    '<:Noot:355763576134303744><:Lust:355763576494882816><:handelmethet:355763575970856960>')
    em8.set_footer(text='Willemsliefde: Ik hou van Holland | Bot door Auxim#2994', icon_url=willemsliefde_url)
    em8.set_author(name='Linda de Mol', icon_url=client.user.avatar_url)
    await client.edit_message(old_message, embed=em8)
    await asyncio.sleep(1)
    await client.edit_message(old_message, embed=em)
    await asyncio.sleep(1)
    await client.edit_message(old_message, embed=em2)
    await asyncio.sleep(1)
    await client.edit_message(old_message, embed=em3)
    await asyncio.sleep(1)
    await client.edit_message(old_message, embed=em4)
    await asyncio.sleep(1)
    await client.edit_message(old_message, embed=em5)
    await asyncio.sleep(1)
    await client.edit_message(old_message, embed=em6)
    await asyncio.sleep(1)
    await client.edit_message(old_message, embed=em7)
    await asyncio.sleep(1)
    await client.edit_message(old_message, embed=em8)
    randomness = 80
    if random.randint(0,100) >=randomness:
        await client.send_message(client.get_channel('241934226721603584'),str(member.nick) + ' heeft <:zelfgenoegzaam:355763575916331038> en raakt nu 50 punten kwijt. OEIOEIOEI.')
        return
    else:
        await asyncio.sleep(1)
        await client.edit_message(old_message, embed=em)
    if random.randint(0,100) >=randomness:
        await client.send_message(client.get_channel('241934226721603584'),str(member.nick) + ' heeft <:Alleskwijt:355763574162849793> en raakt nu 50 punten kwijt. OEIOEIOEI.')
        return
    else:
        await asyncio.sleep(1)
        await client.edit_message(old_message, embed=em2)
    if random.randint(0,100) >=randomness:
        await client.send_message(client.get_channel('241934226721603584'),str(member.nick) + ' heeft <:grinnik:355763575215620107> en raakt nu 50 punten kwijt. OEIOEIOEI.')
        return
    else:
        await asyncio.sleep(1)
        await client.edit_message(old_message, embed=em3)
    if random.randint(0,100) >=randomness:
        await client.send_message(client.get_channel('241934226721603584'),str(member.nick) + ' heeft <:Noot:355763576134303744> en raakt nu 50 punten kwijt. OEIOEIOEI.')
        return
    else:
        await asyncio.sleep(1)
        await client.edit_message(old_message, embed=em4)
    if random.randint(0,100) >=randomness:
        await client.send_message(client.get_channel('241934226721603584'),str(member.nick) + ' heeft <:Lust:355763576494882816> en raakt nu 50 punten kwijt. OEIOEIOEI.')
        return
    else:
        await asyncio.sleep(1)
        await client.edit_message(old_message, embed=em5)
    if random.randint(0,100) >=randomness:
        await client.send_message(client.get_channel('241934226721603584'),str(member.nick) + ' heeft <:handelmethet:355763575970856960> en raakt nu 50 punten kwijt. OEIOEIOEI.')
        return
    else:
        await asyncio.sleep(1)
        await client.edit_message(old_message, embed=em6)
    if random.randint(0,100) >=randomness:
        await client.send_message(client.get_channel('241934226721603584'),str(member.nick) + ' heeft <:Goedkeuring:355763575534387200> en raakt nu 50 punten kwijt. OEIOEIOEI.')
        return
    else:
        await asyncio.sleep(1)
        await client.edit_message(old_message, embed=em7)
    if random.randint(0,100) >=randomness:
        await client.send_message(client.get_channel('241934226721603584'),str(member.nick) + ' heeft <:oplinda:355763576520310794> en raakt nu 50 punten kwijt. OEIOEIOEI.')
        return
    else:
        await asyncio.sleep(1)
        await client.edit_message(old_message, embed=em8)

client.run(bot_token)