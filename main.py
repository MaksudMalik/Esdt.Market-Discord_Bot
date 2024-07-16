import requests, json, discord, os, base64
from discord.ext import tasks
from discord import app_commands
my_secret = os.environ['TOKEN']  #Token is stored in .env file which is not public

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client) #tree holds all our application commands

def get_offer_id(json_response):  #gets offer ID from a json file
  data=json_response['data']
  decoded_data=base64.b64decode(data)
  splitted=str(decoded_data).split('@')
  if json_response['function']=='startSwapWithEgld':
    offerID=bytearray.fromhex(splitted[1]).decode()
  elif json_response['action']['arguments']['transfers'][0]['type']=='MetaESDT':
    offerID=bytearray.fromhex(splitted[6]).decode()
  else:
    offerID=bytearray.fromhex(splitted[4]).decode()
  return offerID

@client.event
async def on_ready(): 
  print_msg.start()  #started the print_msg function once the client is ready
  hash="null"
  await tree.sync()  #sync commands to discord once the client is ready
  
@tasks.loop(seconds=10) #print_msg function will run every 10sec
async def print_msg(): 
  channel = client.get_channel(1043944796890345555)
  response = requests.get('https://api.elrond.com/accounts/erd1qqqqqqqqqqqqqpgqr8z5hkwek0pmytcvla86qjusn4hkufjlrp8s7hhkjk/transactions?function=startSwapWithEsdt%20%2C%20startSwapWithEgld')
  response_info = json.loads(response.text)
  global hash
  if hash==response_info[0]['txHash']:
    msg=("No offers for now")
  else:
    offer_ID=get_offer_id(response_info[0])
    msg=("New offer created, Link : https://esdt.market/app/esdt/listing/{}".format(offer_ID))
    hash=response_info[0]['txHash']
    await channel.send(msg) #sends message on our desired channel

@tree.command(name = "sync_offer", description = "Sync an offer using the offer's transaction hash")
async def self(interaction:discord.Interaction, hash:str): #defining the sync_offer command, takes hash (string) as arguement
  try:  
    trx=requests.get(f'https://api.elrond.com/transactions/{hash}')
    trx_info=json.loads(trx.text)
    to_be_synced_offerid=get_offer_id(trx_info)
    synced_response=requests.get(f'https://public-api.esdt.market/offers/sync-offer/{to_be_synced_offerid}')
    await interaction.response.send_message(f'Offer synced, here you go https://esdt.market/app/esdt/listing/{to_be_synced_offerid}')
  except:
    await interaction.response.send_message("Enter a valid transaction hash")

@tree.command(name = "get_offer", description = "Get an offer's link from its transaction hash")
async def self(interaction:discord.Interaction, hash:str):
  try:  
    trxhash=requests.get(f'https://api.elrond.com/transactions/{hash}')
    trxInfo=json.loads(trxhash.text)
    getofferid=get_offer_id(trxInfo)
    await interaction.response.send_message(f'Here is your offer : https://esdt.market/app/esdt/listing/{getofferid}')
  except:
    await interaction.response.send_message("Enter a valid transaction hash")

client.run((my_secret))