# gangstalker
A Python bot to stalk a Steam group(/gangs) (or individuals) for their gaming activity.

# How to use
Replace the Steam WebAPI token by [making one](https://steamcommunity.com/dev/apikey), replace the Discord Bot token by [making one](https://discord.com/developers/applications) and replace the Discord Channel ID by doing 'Copy Link' on a channel, and retrieving the number after the last `/` character.

# How to modify
You can also append individual users to the group aggregator result, and you may also combine groups. You're also able to delay the messages further.

# What to do if it fails early
Verify if the status code has been printed, Google it, and figure it out.

# What to do if it fails late
Open a GitHub issue in which you detail what and when you've encountered an issue.

# Is this fast?
We batch requests, we don't issue individual requests per SteamID. This should make this pretty quick.

# Features
Writes to Discord channel, and if possible, will generate a Steam bootstrap join (aka: ```steam://{lobbysteamid}/{steamid}```). Also a `CSGO_ONLY` flag which only notifies you if the player is playing the `Beta Dev` (appid: `710`) branch of CS:GO, or the `Live` branch (appid: `730`).

# License
I don't care.
