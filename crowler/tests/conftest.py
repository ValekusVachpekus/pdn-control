"""Делает пакет pdn_parser импортируемым при запуске pytest из любого каталога."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
