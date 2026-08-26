import asyncio
import ctypes
import threading
import pyglet
from winrt.windows.security.credentials.ui import (
    UserConsentVerifier,
    UserConsentVerifierAvailability,
    UserConsentVerificationResult
)

async def verify_windows_pin(message: str) -> bool:
    # 1. Check if Windows Hello / PIN is available
    availability = await UserConsentVerifier.check_availability_async()
    if availability != UserConsentVerifierAvailability.AVAILABLE:
        print("Windows Hello / PIN is not available on this device.")
        return False

    # 2. Trigger native Windows Security PIN prompt
    result = await UserConsentVerifier.request_verification_async(message)

    # 3. Handle verification result
    return result == UserConsentVerificationResult.VERIFIED

def prompt_pin_pyglet(message: str, on_complete_callback):
    """
    Executes PIN verification in a background thread so Pyglet doesn't freeze.
    Calls `on_complete_callback(success: bool)` on Pyglet's main thread when finished.
    """
    def worker():
        # Initialize COM Multithreaded Apartment (MTA) for WinRT on this thread
        ctypes.windll.ole32.CoInitializeEx(None, 0x0)
        try:
            success = asyncio.run(verify_windows_pin(message))
        finally:
            ctypes.windll.ole32.CoUninitialize()

        # Schedule the callback back on Pyglet's main loop (dt is passed by Pyglet clock)
        pyglet.clock.schedule_once(lambda dt: on_complete_callback(success), 0)

    threading.Thread(target=worker, daemon=True).start()