from datetime import timedelta, datetime
from typing import Optional, List

from aiohttp import ClientSession
from genie_common.tools import logger
from genie_common.tools.email_sender import EmailSender

from genie_radio.components.component_factory import ComponentFactory
from genie_radio.logic.playlists_manager import PlaylistsManager
from genie_radio.logic.spotify_session_creator import SpotifySessionCreator
from genie_radio.models import ApplicationException


class ApplicationRunner:
    def __init__(self,
                 email_sender: EmailSender,
                 spotify_session_creator: SpotifySessionCreator,
                 max_exceptions: int = 3,
                 exceptions_relevance_window: timedelta = timedelta(minutes=60),
                 exceptions: Optional[List[ApplicationException]] = None):
        self._email_sender = email_sender
        self._spotify_session_creator = spotify_session_creator
        self._max_exceptions = max_exceptions
        self._exceptions_relevance_window = exceptions_relevance_window
        self._exceptions = exceptions or []

    async def run(self):
        with self._email_sender.notify_failure():
            await self._inner_run()

    async def _inner_run_wrapper(self):
        spotify_session = self._spotify_session_creator.create()

        async with ClientSession() as client_session:
            playlists_manager = PlaylistsManager()

    async def _inner_run(self):
        if len(self._exceptions) > self._max_exceptions:
            raise RuntimeError("Exceptions count exceeded max allowed exceptions. Aborting")

        try:
            await self._playlists_manager.run_forever()

        except PermissionError:
            logger.info("Session authorization expired. Re-creating session")
            return await self._inner_run()

        except BaseException as e:
            logger.exception("Encountered exception! Retrying")
            self._update_application_exceptions_state(e)
            return await self._inner_run()

    def _update_application_exceptions_state(self, exception: BaseException) -> None:
        now = datetime.now()

        for i, app_exception in enumerate(self._exceptions):
            if not self._is_relevant_exception(now, app_exception):
                self._exceptions.pop(i)

        current_exception = ApplicationException(exception=exception, time=now)
        self._exceptions.append(current_exception)

    def _is_relevant_exception(self, now: datetime, app_exception: ApplicationException):
        return now - app_exception.time < self._exceptions_relevance_window