# pomodoro-telegram-python-bot
Telegram bot based on aiogram library

Uses Redis as timer backend: sets user's timer as value, alerts when key is EXPIRED

Feel free to open issues or contact me in DM (telegram in profile)

TODO List:
* [x] Menu's transitions and buttons
* [x] Show timer button
* [x] Configure user's storage
* [ ] Track user's work cycle
* [x] Timers
* [x] Timer callback
* [ ] Custom message on timer end (?)
* [x] Save user's states and timers
* [ ] Pass redis connection to middleware
* [ ] Optimize coroutines for concurrent operations if needed
* [ ] Settings