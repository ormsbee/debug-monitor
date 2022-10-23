import click

from .app import DebugMonitorApp

@click.command()
def run():
    app = DebugMonitorApp()
    app.run()
    app.socket.close()

if __name__ == '__main__':
    run()
