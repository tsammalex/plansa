from pathlib import Path

from clld.web.assets import environment

import plansa


environment.append_path(
    Path(plansa.__file__).parent.joinpath('static').as_posix(),
    url='/plansa:static/')
environment.load_path = list(reversed(environment.load_path))
