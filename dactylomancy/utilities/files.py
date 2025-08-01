import logging
import tempfile
from tomlkit import dumps
from tomlkit.toml_document import TOMLDocument


class TemporaryTextFile(object):
    suffix = '.txt'

    def __init__(self, text: str):
        self.text = text

    def __enter__(self) -> str:
        self.file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix=self.suffix,
            delete_on_close=False
        )
        logging.debug(f'Created temporary file: {self.file.name}')
        self.file.write(self.text)
        self.file.close()
        return self.file.name

    def __exit__(self, *exc_info):
        logging.debug(f'Deleting temporary file {self.file.name}.')


class TemporaryTOMLFile(TemporaryTextFile):
    suffix = '.toml'

    def __init__(self, doc: TOMLDocument):
        text = dumps(doc)
        super().__init__(text)
