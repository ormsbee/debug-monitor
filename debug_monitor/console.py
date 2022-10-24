"""
CLI module for the debug_monitor command.

Handling optional flags and configuration reading (if any) happens here.
"""
import click

from .app import DebugMonitorApp

@click.command()
def run():
    """
    Start debug-monitor service and Terminal UI.
    """
    app = DebugMonitorApp()
    app.run()
    app.socket.close()

if __name__ == '__main__':
    run()
