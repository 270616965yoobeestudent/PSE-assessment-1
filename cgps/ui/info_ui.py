from typing import Any
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Pretty
from textual.events import Key


class InfoUi(App):
    def with_data(self, data: Any):
        self._data = data
        return self

    def compose(self) -> ComposeResult:
        yield Pretty(self._data)

    @on(Key)
    def _on_key(self, event: Key) -> None:
        if event.key == "escape" or event.key == "q":
            self.exit()
