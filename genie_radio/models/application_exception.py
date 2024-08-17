from dataclasses import dataclass
from datetime import datetime


@dataclass
class ApplicationException:
    exception: BaseException
    time: datetime
