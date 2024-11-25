# KISS Controller: Telegram-based Remote Access Tool &middot; ![Python Version](https://img.shields.io/badge/python-3.7%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

KISS Controller is a sophisticated but simple Telegram-based Remote Access Tool designed for educational purposes and ethical penetration testing. It leverages the Telegram Bot API to provide a seamless and secure remote access experience.

## :rocket: Features

- :satellite: **Multi-Client Management**: Effortlessly manage and switch between multiple connected clients.
- :computer: **System Information Retrieval**: Gather detailed system information from target machines.
- :globe_with_meridians: **Network Reconnaissance**: Obtain comprehensive network details, including public and local IP addresses.
- :camera: **Screenshot Capture**: Take and receive screenshots from connected clients.
- :microphone: **Audio Recording**: Remotely record audio from target devices.
- :file_folder: **Filesystem Exploration**: Navigate through the target's filesystem, list directories, and view file contents.
- :open_file_folder: **File Exfiltration**: Securely transfer files from connected clients to the operator.
- :lock: **Secure Communication**: Utilizes Telegram's encrypted platform for all communications.

## :warning: Disclaimer

KISS Controller is intended for **educational and ethical testing purposes only**. Users are solely responsible for complying with applicable laws and regulations in their jurisdiction.

**DO NOT** use this software for illegal activities. Unauthorized access to computer systems is illegal and punishable by law.

## :wrench: Installation

1. Clone the repository:
git clone https://github.com/serverket/kisscontroller.git

2. Navigate to the project directory:
cd kisscontroller

3. Install the required packages:
pip install -r requirements.txt

4. Create a `.env` file in the project root directory with your Telegram Bot token:
```
TOKENY=your_actual_bot_token_here
PASSY=your_actual_password_here
```

5. Make sure to replace any instances of TOKENY (Telegram Bot Token) and PASSY (In-bot password) in your script with the corresponding variables to access your credentials.

## :rocket: Usage

1. Run the script:
```python kisscontroller.py```
2. Start interacting with the bot via Telegram using the available commands:
- `/start`: Initialize the bot and display the command menu
- `/clients`: Manage and select connected clients
- `/info`: Retrieve system information
- `/network`: Obtain network details
- `/screenshot`: Capture and receive a screenshot
- `/record`: Record audio from the target device
- `/explore`: Explore the filesystem
  - `cd <path>`: Change directory
  - `ls <path>`: List contents of a directory
  - `cat <file>`: View contents of a file
- `/getfile`: Transfer files from the target device

## :seedling: Support the Project  

I have many ideas for this, it can be better, faster, stronger, with your support:

### BTC
```
1N2knp6D5egiDnaJEixiqGhPESECEmEfUp
```

## :handshake: Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/yourusername/kisscontroller/issues).

## :scroll: License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## :brain: Acknowledgements

"Whoever loves discipline loves knowledge, but whoever hates correction is stupid."