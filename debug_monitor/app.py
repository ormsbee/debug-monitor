"""
Textual App that provides our terminal UI.

TODO: Move the zmq stuff entirely out of here.
"""
import asyncio
import json

from rich.markdown import Markdown
from rich.text import Text

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import var
from textual.widgets import DataTable, Footer, Header, Static, TextLog, Button
from textual.widgets.tabs import Tab, Tabs

import zmq
import zmq.asyncio

from .messages import MessageLog


class DebugMonitorApp(App):
    """A working 'desktop' calculator."""
    CSS_PATH = "app.css"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket = None
        self.messages = MessageLog()

    def update_request_log(self):
        self.request_log.clear()
        for request_uuid, _sender_data in self.messages.get_messages(20):
            # request_info = sender_data.get("request")
            request_info = self.messages.get_message(request_uuid, "request")
            if not request_info:
                self.request_log.write(f"INTERNAL ERROR: No Request Info for {request_uuid}")
                continue
            
            # Hacky, for display purposes
            started_at_str = request_info['started_at'][11:-4]
            request_text_line = Text(
                (
                    f"{started_at_str} "
                    f"{request_info['method']} "
                    f"{request_info['path']}"
                ),
                style="bold",
            )
            if qs := request_info['querystring']:
                request_text_line.append(f"?{qs}", style="bold")

            self.request_log.write(request_text_line)

            # response_info = sender_data.get("response")
            response_info = self.messages.get_message(request_uuid, "response")
            response_text_line = Text("↳ ")
            if response_info is None:
                response_text_line.append(f"(waiting for response... {request_uuid})")
                # debugging
                # self.message_log.write(self.messages.requests)
            else:
                status_code = int(response_info['status_code'])
                if status_code < 400:
                    status_color = "green"
                elif status_code < 500:
                    status_color = "yellow"
                else:
                    status_color = "red"

                response_text_line.append(str(status_code), f"bold {status_color}")

                content_type = response_info['headers']['Content-Type'].split(";")[0]
                response_text_line.append(f" {content_type}")

                content_length = int(response_info['headers']['Content-Length'])
                response_text_line.append(
                    f"\t{content_length:>12,d}"
                    f"{response_info['duration']:>12,.1f} ms"
                )

                view_info = self.messages.get_message(request_uuid, "view")
                if view_info:
                    response_text_line.append(f" {view_info['view_func']}")

            self.request_log.write(response_text_line)

        self.request_log.refresh()

    def new_message(self, msg_data):
        # 🏃
        #if msg_data['sender'] == 'request':
        #    request_msg = msg_data['data']['']
        
#        self.request_table.add_row(f"Message arrived from {msg_data['sender']}")

        parsed_msg_data = json.loads(msg_data)
        self.messages.add_message(
            parsed_msg_data["request_uuid"],
            parsed_msg_data["sender"],
            parsed_msg_data["data"],
        )
        # self.request_table.scroll_end(animate=False)

        formatted_msg = json.dumps(
            parsed_msg_data,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        # self.message_log.write(formatted_msg)

        if parsed_msg_data['sender'] in ('request', 'response', 'view'):
            self.update_request_log()


    async def recv_and_process(self):
        while True:
            msg_data = await self.socket.recv_string() # waits for msg to be ready
            self.new_message(msg_data)

    def compose(self) -> ComposeResult:
        """Add our buttons."""
        self.request_table = DataTable(id="request_table")
        # self.request_table.add_column("Status", "URL", "Size", "Latency", "Time")
        self.request_table.add_column("Debug Monitor")
        self.request_log = TextLog(id="request_log")

        self.message_log = TextLog(id="message_log", highlight=True, wrap=True)
        self.header = Header(id="header", classes="")
        self.panel_tabs = Tabs(
            tabs=[
                Tab("Request"),
                Tab("Response"),
                Tab("View"),
                Tab("Database"),
                Tab("Templates"),
                Tab("Logs"),
                Tab("Python API"),
            ],
            active_tab="Request",
            tab_padding=2,
#            id="panel_tabs",
        )
        self.footer = Footer()
        self.panel_placeholder = Static("Placeholder for Content", markup=True)

        # Using Ctrl-# doesn't scale to the number of panels we might have.
        # Probably better to have type-based selection? (key to start freetext
        # search, and then switch panels as appropriate).
        #
        buttons_ids_and_text = [
            ("request", "Request"),
            ("response", "Response"),
            ("view", "View"),
#            ("database", "Database"),
#            ("templates", "Templates"),
#            ("logs", "Logs"),
#            ("cache", "Cache"),
#            ("signals", "Signals"),
#            ("config", "Config"),
#            ("celery", "Celery"),
#           ("app_apis", "App APIs"),
#           ("profiling", "Profiling"),
        ]
        buttons = [
            # Button(f"{row}: {button_text}", id=button_id)
            Button(button_text, id=button_id)
            for (row, (button_id, button_text))
            in enumerate(buttons_ids_and_text, start=1)
        ]
        self.button_panel = Vertical(*buttons, id="button_panel")

        #yield self.request_table
        #yield Footer()

        yield Container(
            Vertical(
                self.header,
                self.request_log,
                id="request_nav",
            ),
            # self.request_table,
            Horizontal(
                self.button_panel,
                self.message_log,
                id="detail_view"
            ),
            # self.panel_tabs,
            self.footer,
        #    self.panel_placeholder,
        )
    
    #async def on_button_pressed(self, event: Button.Pressed) -> None:
    #    """Called when a button is pressed."""

    async def on_mount(self) -> None:
        self.title = "Debug Monitor"

        self.ctx = zmq.asyncio.Context()
        self.socket = self.ctx.socket(zmq.SUB)
        url = "tcp://127.0.0.1:7999"
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.socket.bind(url)

        asyncio.create_task(self.recv_and_process())

        self.bind("q", "quit", description="Quit")


        self.bind("j", "down", description="Down")
        self.bind("k", "up", description="Up")
        self.bind("f", "filter_requests", description="Filter Requests")

        self.bind("p", "panel", description="Panel")
        self.bind("ctrl-f", "filter_details", description="Filter Details")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        # Just get the most recent message for now.
        self.render_details(self.messages.last_request_uuid_reported, event.button.id)


    def render_details(self, request_uuid, sender):
        self.message_log.clear()
        data = self.messages.requests[request_uuid].get(sender)

        if not data:
            self.message_log.write(
                f"No {sender} data available for request {request_uuid}."
            )
            self.message_log.refresh()
            self.refresh()
            return

        self.message_log.write(data)
        self.message_log.refresh()

    #async def on_key(self, event: events.Key) -> None:
    #    """Called when the user presses a key."""
    #    now = datetime.now().strftime("%H:%M:%S")
    #    self.new_message(
    #        f"{now}  200  /api/itemstore/v1/items",
    #    )
        # self.request_log.write("Hello!\n")
