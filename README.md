# ToTPZ - Time-Based One-Time Password Generator for Windows

A lightweight, one-file(no installation required) Windows application for easily generating Time-Based One-Time Password (TOTP) codes, using your secret keys.


## How it works

- When you start the app for the first time, a new db file will be created - `ToTPZ.db`
    - You will store your secret keys in this file - this is NOT an encrypted file, so keep it somewhere safe
- Now you can use the "Add Account" button to store a new account (name and secret key)
- Once you stored an account, you can select it from a list and click the "Generate Password" button
- Use the generated code for two-factor authentication
- To update a secret key associated with an account, you can either:
    1. Use the same name to store the new key (old one will be updated)
    2. Delete existing name and re-add it with new secret key


## Security

- `ToTPZ.exe` does not store any data
- `ToTPZ.exe` does not connect to the internet
- `ToTPZ.db`  stores your accounts and associated secret keys - keep this file safe - the app will read the file, only if it's located in the same folder as `ToTPZ.exe`


## The why

- There are no free apps dedicated to do this on Windows
- The apps that do exist (any OS) and are free, they exist to steal your data
- ToTPZ.exe is a free, clean and simple way to generate TOTP on a Windows machine. That is it. 


## Scenario exmaple:

- While Bitwarden(free) does not allow you to generate a password based on your secret key, it does allow storing it.
- Store your secret keys for safe-keeping in Bitwarden(free), and use this app to generate the codes you need.


## Acknowledgments

- TOTP algorithm from [pyotp](https://github.com/pyauth/pyotp)
- UI: [flet](https://github.com/flet-dev/flet)
