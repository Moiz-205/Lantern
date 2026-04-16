from textual.app import App, ComposeResult
from textual.widgets import Input, Button, Label, RichLog, Footer
from textual.screen import Screen

import threading
from core import server, client
from utils import broadcast, room_config


display_name = "guest01"
display_color = "green"

class HomeScreen(Screen):
    def compose(self) -> ComposeResult:
        # startup screen buttons
        yield Button("Host", id="host")
        yield Button("Join", id="join")
        yield Button("Settings", id="settings")
        yield Button("Exit", id="exit")

        # host or join screen input fields and buttons
        yield Label("", id="generated_code")
        yield Input(placeholder="Room Code", id="room_code")
        yield Input(placeholder="Host IP", id="host_ip")
        yield Button("Create", id="create_room")
        yield Button("Join", id="join_room")

        # settings screen fields and buttons
        yield Input(placeholder="change your name", id="display_name")
        yield Input(placeholder="change your color", id="display_color")
        yield Button("Update", id="update")

        # multi screen back button
        yield Button("Back", id="back")

        yield Footer()

    def auto_discover_host(self):
        host_ip, room_code, room_name = broadcast.listen_for_host()
        self.app.call_from_thread(self._fill_host_fields, host_ip, room_code)

    def _fill_host_fields(self, host_ip, room_code):
        self.query_one("#host_ip", Input).value = host_ip
        self.query_one("#room_code", Input).value = room_code

    def on_mount(self):
        self.query_one("#generated_code").display = False
        self.query_one("#room_code").display = False
        self.query_one("#host_ip").display = False
        self.query_one("#create_room").display = False
        self.query_one("#join_room").display = False

        self.query_one("#display_name").display = False
        self.query_one("#display_color").display = False
        self.query_one("#update").display = False

        self.query_one("#back").display = False
        # more settings fields and buttons here

    def on_screen_resume(self):
        self.query_one("#host").display = True
        self.query_one("#join").display = True
        self.query_one("#settings").display = True
        self.query_one("#exit").display = True

        self.query_one("#generated_code").display = False
        self.query_one("#room_code").display = False
        self.query_one("#host_ip").display = False
        self.query_one("#create_room").display = False
        self.query_one("#join_room").display = False
        self.query_one("#display_name").display = False
        self.query_one("#display_color").display = False
        self.query_one("#update").display = False
        self.query_one("#back").display = False

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "host":
            global ROOM_CODE, ROOM_NAME
            ROOM_CODE = room_config.generate_room_code()
            ROOM_NAME = room_config.generate_room_name()

            self.query_one("#host").display = False
            self.query_one("#join").display = False
            self.query_one("#settings").display = False
            self.query_one("#exit").display = False

            self.query_one("#generated_code").display = True
            self.query_one("#create_room").display = True
            self.query_one("#back").display = True

            self.query_one("#generated_code", Label).update(f"ROOM CODE: {ROOM_CODE}")

        elif event.button.id == "join":
            threading.Thread(target=self.auto_discover_host, daemon=True).start()

            self.query_one("#host").display = False
            self.query_one("#join").display = False
            self.query_one("#settings").display = False
            self.query_one("#exit").display = False

            self.query_one("#room_code").display = True
            self.query_one("#host_ip").display = True
            self.query_one("#join_room").display = True
            self.query_one("#back").display = True

        elif event.button.id == "settings":
            self.query_one("#host").display = False
            self.query_one("#join").display = False
            self.query_one("#settings").display = False
            self.query_one("#exit").display = False

            self.query_one("#display_name").display = True
            self.query_one("#display_color").display = True
            self.query_one("#update").display = True
            self.query_one("#back").display = True

        elif event.button.id == "update":
            global display_name, display_color
            display_name = self.query_one("#display_name", Input).value
            display_color = self.query_one("#display_color", Input).value

        elif event.button.id == "exit":
            self.app.exit()

        elif event.button.id == "back":
            self.query_one("#host").display = True
            self.query_one("#join").display = True
            self.query_one("#settings").display = True
            self.query_one("#exit").display = True

            self.query_one("#generated_code").display = False
            self.query_one("#room_code").display = False
            self.query_one("#host_ip").display = False
            self.query_one("#create_room").display = False
            self.query_one("#join_room").display = False
            self.query_one("#display_name").display = False
            self.query_one("#display_color").display = False
            self.query_one("#update").display = False
            self.query_one("#back").display = False

        elif event.button.id == "create_room":
            threading.Thread(target=server.start_server, args=(ROOM_CODE,), daemon=True).start()
            threading.Thread(target=broadcast.start_broadcasting, args=(ROOM_CODE, ROOM_NAME), daemon=True).start()
            client.connect(host="127.0.0.1", port=5000, username=display_name, color=display_color, room_code=ROOM_CODE)

            self.app.push_screen(ChatScreen(display_name, display_color))
            self.notify("room created.")

        elif event.button.id == "join_room":
            room_code = self.query_one("#room_code", Input).value
            host_ip = self.query_one("#host_ip", Input).value

            try:
                client.connect(host=host_ip, port=5000, username=display_name, color=display_color, room_code=room_code)

                self.app.push_screen(ChatScreen(display_name, display_color))
                self.notify("chat joined.")
            except Exception:
                self.notify("Failed to connect.")


class ChatScreen(Screen):
    def __init__(self, name, color):
        super().__init__()
        self.user = name
        self.color = color

    def compose(self) -> ComposeResult:
        yield RichLog(id="messages", markup=True)
        yield Input(placeholder="Type a message...", id="message_input")
        yield Button("Leave", id="leave")

    def on_mount(self):
        self.query_one("#message_input").focus()
        threading.Thread(target=client.receive_message, args=(self.display_message,), daemon=True).start()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "leave":
            client.send_leave(self.user, self.color)
            self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted):
        log = self.query_one("#messages", RichLog)
        log.write(f"[{self.color}]{self.user}[/{self.color}] > {event.value}")
        client.send_message(self.user, self.color, event.value)
        event.input.clear()

    def _write_message(self, message):
        log = self.query_one("#messages", RichLog)
        log.write(message)

    def display_message(self, message):
        self.app.call_from_thread(self._write_message, message)

class LaternApp(App):
    CSS_PATH = "lantern.tcss"
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("up", "focus_previous", "Up"),
        ("down", "focus_next", "Down"),
        # ("escape", "back", "Back"),
    ]

    def on_mount(self):
        self.push_screen(HomeScreen())
