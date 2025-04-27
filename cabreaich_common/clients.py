# /home/reaich/CAB_ReAIch_Cloud/cabreaich-common/cabreaich_common/clients.py
# Provides reusable clients for interacting with different CAB ReAIch services.
# REWRITTEN: Added QLogicResponse import and injectable httpx.AsyncClient pattern.

import httpx # Use httpx for both sync and async support
import asyncio
from typing import Any, Dict, Optional, Type, Union # Added Union
from pydantic import BaseModel

# Import common settings and exceptions
from .config import settings #
from .exceptions import APIError #
# Import models for type hinting
from .models import QLogicResponse # <-- Added import

# Import common logger
try:
    from .logging import setup_logger #
    log = setup_logger(__name__, settings.LOG_LEVEL) #
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    log.warning("Could not import common logger setup in clients.py")


# --- Async Base Client (Modified for Injectable Client) ---
class AsyncBaseClient:
    """
    Base class for asynchronous HTTP clients using httpx.
    Supports using an externally managed httpx.AsyncClient instance for connection pooling.
    """
    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        client: Optional[httpx.AsyncClient] = None # <-- Allow injecting a client
    ):
        """
        Initializes the async client.

        Args:
            base_url: The base URL for the target service.
            timeout: Default request timeout in seconds (only used if creating a client).
            client: An optional existing httpx.AsyncClient instance. If provided,
                    this client will be used and NOT closed by this class instance.
                    If None, a new client instance will be created and managed internally.
        """
        self.base_url = base_url
        self._should_close_client: bool # Flag to track if we own the client lifecycle

        if client:
            # Use the provided (shared) client instance
            self._client = client
            self._should_close_client = False # Don't close the shared client
            log.debug(f"Initialized {self.__class__.__name__} with shared httpx.AsyncClient for base URL: {base_url}")
        else:
            # Create a new internal client instance
            self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout, follow_redirects=True)
            self._should_close_client = True # We are responsible for closing this client
            log.debug(f"Initialized {self.__class__.__name__} with internal httpx.AsyncClient for base URL: {base_url}")

    async def _handle_response(self, response: httpx.Response, response_model: Optional[Type[BaseModel]] = None) -> Any:
        """
        Handles HTTP responses asynchronously, raising APIError on failure
        and optionally parsing the response using a Pydantic model.
        """
        try:
            # Raise HTTPStatusError for 4xx/5xx responses
            response.raise_for_status()
            # If successful and a model is provided, parse and validate
            if response_model:
                # Use model_validate for Pydantic v2+
                return response_model.model_validate(response.json())
            # Otherwise, return raw JSON or text if no JSON
            try:
                return response.json()
            except Exception:
                return response.text # Fallback to text if JSON parsing fails
        except httpx.HTTPStatusError as e:
            # Log the error and raise a standardized APIError
            log.error(f"API request failed: {e.response.status_code} {e.response.reason_phrase} - {e.response.text[:200]}")
            raise APIError( #
                f"API request failed: {e.response.status_code} {e.response.reason_phrase} - {e.response.text[:200]}",
                status_code=e.response.status_code
            ) from e
        except httpx.RequestError as e:
             # Handle network errors, timeouts etc.
             log.error(f"HTTP request error: {e}")
             raise APIError(f"HTTP request error: {e}") from e #
        except Exception as e:
             # Handle JSON decoding errors or Pydantic validation errors
             log.exception(f"Error handling response: {e}")
             raise APIError(f"Error handling response: {e}", status_code=response.status_code) from e #


    async def close(self):
         """
         Closes the underlying async HTTP client ONLY if it was created internally.
         """
         # Only close the client if this instance created it
         if self._should_close_client and hasattr(self, '_client'):
             await self._client.aclose()
             log.debug(f"Closed internal httpx client for {self.base_url}")
         elif not self._should_close_client:
              log.debug(f"Skipping close for shared httpx client used by {self.base_url}")


    # Implement async context manager protocol
    async def __aenter__(self):
        """Enter the async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager, closing the client if necessary."""
        await self.close()

# --- Specific Async Clients (Modified to accept optional client) ---

class AsyncIntegrationClient(AsyncBaseClient):
    """Async client for interacting with the Integration API."""
    def __init__(
        self,
        base_url: str = str(settings.INTEGRATION_API_URL), #
        client: Optional[httpx.AsyncClient] = None # Allow passing shared client
    ):
        super().__init__(base_url=base_url, client=client)

    async def post_event(self, event_data: BaseModel) -> Dict[str, Any]:
        """Sends an event (e.g., VADEventData) to the integration event endpoint."""
        try:
            # Use model_dump for Pydantic v2+
            response = await self._client.post("/integration/event", json=event_data.model_dump(mode='json'))
            return await self._handle_response(response)
        except APIError: #
             raise # Re-raise standardized error
        except Exception as e:
             log.exception(f"Unexpected error posting event to Integration API: {e}")
             raise APIError(f"Unexpected error posting event: {e}") from e #

class AsyncSpeechApiClient(AsyncBaseClient):
    """Async client for interacting with the Speech Container API (e.g., for pause/resume)."""
    def __init__(
        self,
        base_url: str = str(settings.SPEECH_API_URL), #
        client: Optional[httpx.AsyncClient] = None # Allow passing shared client
    ):
        super().__init__(base_url=base_url, client=client)

    async def control_audio(self, session_id: Union[str, uuid.UUID], action: str) -> Dict[str, Any]: # Accept UUID too
        """Sends a pause or resume command to the speech container."""
        if action not in ["pause", "resume"]:
             raise ValueError("Invalid action for control_audio, must be 'pause' or 'resume'")
        url = f"/session/{str(session_id)}/audio/{action}" # Ensure session_id is string for URL
        try:
            response = await self._client.post(url)
            return await self._handle_response(response)
        except APIError: #
            raise # Re-raise standardized error
        except Exception as e:
             log.exception(f"Unexpected error controlling speech audio: {e}")
             raise APIError(f"Unexpected error controlling speech audio: {e}") from e #

class AsyncQLogicClient(AsyncBaseClient):
    """Async client for interacting with the QLogic API."""
    def __init__(
        self,
        base_url: str = str(settings.QLOGIC_ROUTE_URL), #
        client: Optional[httpx.AsyncClient] = None # Allow passing shared client
    ):
        super().__init__(base_url=base_url, client=client)

    async def route_turn(self, turn_input: BaseModel) -> QLogicResponse: # Type hint added
        """Sends turn data to QLogic and gets the next action."""
        url = "/qlogic/route_turn" # Example endpoint - confirm actual QLogic endpoint if different
        try:
            # Use model_dump for Pydantic v2+
            response = await self._client.post(url, json=turn_input.model_dump(mode='json'))
            # Use the QLogicResponse model for validation
            return await self._handle_response(response, response_model=QLogicResponse) #
        except APIError: #
            raise # Re-raise standardized error
        except Exception as e:
             log.exception(f"Unexpected error routing turn via QLogic: {e}")
             raise APIError(f"Unexpected error routing turn: {e}") from e #


# --- Example Usage (using injectable client pattern) ---
# import asyncio
# from cabreaich_common.config import settings
# from cabreaich_common.clients import AsyncQLogicClient
# from cabreaich_common.models import QLogicTurnInput, QLogicResponse
# import httpx
#
# async def main():
#     # Ideally, manage this client via application lifespan (e.g., FastAPI lifespan)
#     async with httpx.AsyncClient() as shared_http_client:
#
#         # Inject the shared client into the specific API client
#         qlogic_client = AsyncQLogicClient(client=shared_http_client)
#
#         try:
#             # Assume turn_data is a QLogicTurnInput instance
#             turn_data = QLogicTurnInput(child_id=uuid.uuid4(), session_id=uuid.uuid4(), module_context="test") # Minimal example
#             qlogic_response = await qlogic_client.route_turn(turn_data)
#             print(f"QLogic action type: {qlogic_response.type}")
#             # ... handle response ...
#         except APIError as e:
#             print(f"Error communicating with QLogic: {e}")
#
#         # Note: No need to call qlogic_client.close() here,
#         # as the shared_http_client's context manager handles closing.
#
# # asyncio.run(main())