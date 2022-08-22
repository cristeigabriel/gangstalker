import requests
from requests.exceptions import Timeout, RequestException
import xml.etree.ElementTree as ElementTree
from steam.webapi import WebAPI
import asyncio
import discord

# Constants
STEAM_API_KEY = '<YOUR STEAM API KEY>'
DISCORD_TOKEN = '<YOUR DISCORD TOKEN>'
DISCORD_CHANNEL = 0
STALK_PERIOD_SECONDS = 15
CSGO_ONLY = False

# Wrapper for issuing requests and retrieving the results
steam_web = WebAPI(STEAM_API_KEY)

class GroupAggregator:
    groupname = ''
    page = 1
    ids = []

    def __init__(self, groupname):
        self.groupname = groupname 
        self.ids.clear()
        pass

    def get_url(self):
        return 'http://steamcommunity.com/groups/' + self.groupname + '/memberslistxml?xml=1'

    def fetch_response(self, page):
        url = self.get_url() + '&p=%s' % page

        response = None
        try:
            response = requests.get(url, timeout=3)
            if response.status_code != 200:
                print(f'Uh-oh! Status code: {response.status_code}')
                return None
        except Timeout as e:
            print(e)
        except RequestException as e:
            print(e)

        if response is None:
            return None

        return response.text

    def get_steam_ids(self, page=page):
        response = self.fetch_response(page)
        if response is None:
            return None

        root = ElementTree.fromstring(response)
        members = root.find('members')
        if members is None:
            return None

        for steamid in members.findall('steamID64'):
            self.ids.append(int(steamid.text))

        if root.findall('nextPageLink'):
            page += 1
            return self.get_steam_ids(page)

        return self.ids

# List of people
gang = GroupAggregator('valve').get_steam_ids()
print(f'Gang has {len(gang)} entries')

# Computes a list of response dicts, count of remainders of 100
def get_results(new_list=gang, results=[]):
    def work(list, length, into):
        pushing = steam_web.ISteamUser.GetPlayerSummaries(steamids=','.join(map(lambda x: str(x), list[:length])))
        # print(len(pushing['response']['players']), len(list[:length]))
        into.append(pushing)

    print(f'Result getter has a remainder of {len(new_list)} elements to process')

    if len(new_list) < 100:
        work(new_list, len(new_list), results)
        copy = results
        results.clear()
        return copy

    work(new_list, 100, results)
    return get_results(new_list[100:], results)

class Bot(discord.Client):
    async def on_ready(self):
        async def stalk():
            await self.wait_until_ready()

            channel = self.get_channel(DISCORD_CHANNEL)
            while not self.is_closed():
                # Whether there's any gamer processed
                any_gamer = False

                for response in get_results():
                    if 'response' in response:
                        response = response['response']
                    else:
                        continue

                    if 'players' in response:
                        response = response['players']
                    else:
                        continue

                    for response in response:
                        if 'gameid' in response and 'gameextrainfo' in response:
                            id = response['gameid']
                          
                            if CSGO_ONLY:
                                live = (id == '730')
                                beta = (id == '710')
                                if not (live or beta):
                                    continue

                            # We've got at least one gamer of interest, so don't override final message
                            any_gamer = True

                            game_name = response['gameextrainfo']

                            name = response['personaname']
                            if 'lobbysteamid' in response:
                                steamid = response['steamid']
                                lobbysteamid = response['lobbysteamid']
                                await channel.send(f'{name} playing gameid {id} ({game_name}).\nTo join their session run this in browser/Windows Run:\n```steam://joinlobby/{id}/{lobbysteamid}/{steamid}```')
                            else:
                                  await channel.send(f'{name} playing gameid {id} ({game_name}). Session is private!')

                if not any_gamer:
                    await channel.send('No gamer matching specified criteria has been met!')

                await asyncio.sleep(STALK_PERIOD_SECONDS)

        print(f'Logged on as {self.user}')
        self.loop.create_task(stalk())

intents = discord.Intents.default()
bot = Bot(intents=intents)
bot.run(DISCORD_TOKEN)