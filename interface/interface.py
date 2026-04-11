from textual.app import App, ComposeResult
from textual.widgets import Input, Button, RichLog, Footer
from textual.screen import Screen


ROOM = "lamp"    # room-code
HOST = "000"    # host-ip

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

    def on_mount(self):
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
            self.query_one("#host").display = False
            self.query_one("#join").display = False
            self.query_one("#settings").display = False
            self.query_one("#exit").display = False

            self.query_one("#create_room").display = True
            self.query_one("#back").display = True

            # here, randomly generated room code is displayed
            # upon selecting enter, host joins the chat and room is created
            # and host_ip is broadcasted (later UDP functionality)

        elif event.button.id == "join":
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

            self.notify(f"{ROOM} - {HOST}")

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

            self.query_one("#room_code").display = False
            self.query_one("#host_ip").display = False
            self.query_one("#create_room").display = False
            self.query_one("#join_room").display = False
            self.query_one("#display_name").display = False
            self.query_one("#display_color").display = False
            self.query_one("#update").display = False
            self.query_one("#back").display = False

        elif event.button.id == "create_room":
            # check condition is user can be host or is user actually able to host
            # like connected to hotspot or LAN.
            # if it is true then host will display its hosting_ip and create a room.
            # (in this case host will be broadcasting its ip UDP Broadcast)

            self.app.push_screen(ChatScreen(display_name, display_color))
            self.notify("room created.")

        elif event.button.id == "join_room":
            room_code = self.query_one("#room_code", Input).value
            host_ip = self.query_one("#host_ip", Input).value

            if room_code == ROOM and host_ip == HOST:
                self.app.push_screen(ChatScreen(display_name, display_color))
                self.notify("chat joined.")
            else:
                self.notify("Red")


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

    def on_input_submitted(self, event: Input.Submitted):
        log = self.query_one("#messages", RichLog)
        log.write(f"[{self.color}]{self.user}[/{self.color}] > {event.value}")
        event.input.clear()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "leave":
            self.app.pop_screen()

class LaternApp(App):
    CSS_PATH = "lantern.tcss"
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("up", "focus_previous", "Up"),
        ("down", "focus_next", "Down"),
        # ("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Footer()

    def on_mount(self):
        self.push_screen(HomeScreen())

if __name__ == "__main__":
    LaternApp().run()
