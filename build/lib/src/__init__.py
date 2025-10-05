from .storage import UserFile
from rich.console import Console

console = Console()

uf = UserFile()
uf.load()
subjects = uf.subjects

