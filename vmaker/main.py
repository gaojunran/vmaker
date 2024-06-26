import typer

app = typer.Typer()


@app.callback()
def callback():
	"""
    Awesome Portal Gun
    """


@app.command()
def add(new_name: str, source: str = ""):
	typer.echo(f"Invoking the command `add` with filename {new_name}...")
	typer.echo(f"{source}")

# @app.command()
# def shoot():
#     """
#     Shoot the portal gun
#     """
#     typer.echo("Shooting portal gun")
#
#
# @app.command()
# def load():
#     """
#     Load the portal gun
#     """
#     typer.echo("Loading portal gun")
