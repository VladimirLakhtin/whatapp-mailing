import os
import random
import time
from urllib.parse import quote

import pyautogui as pg
from pywhatkit.core import core, exceptions
import webbrowser as web

from pywhatkit.core.core import _web, copy_image, check_number


class WhatsAppManager:
    """Sender messages in WhatsApp"""

    def sendwhatmsg_instantly(self, phone_no: str, message: str, wait_time: int = 15,
                               close_time: int = 3) -> None:
        """Send WhatsApp Message Instantly"""

        if not core.check_number(number=phone_no):
            raise exceptions.CountryCodeException("Country Code Missing in Phone Number!")

        web.open(f"https://web.whatsapp.com/send?phone={phone_no}&text={quote(message)}")
        time.sleep(random.randint(10, 25))
        pg.press('enter')
        core.close_tab(wait_time=close_time)
        time.sleep(random.randint(5, 15))

    def sendwhats_image(self, receiver: str, img_path: str, caption: str = "", wait_time: int = 15,
                        close_time: int = 3) -> None:
        """Send Image to a WhatsApp Contact or Group at a Certain Time"""

        if (not receiver.isalnum()) and (not core.check_number(number=receiver)):
            raise exceptions.CountryCodeException("Country Code Missing in Phone Number!")

        time.sleep(random.randint(10, 25))
        core.send_image(
            path=img_path, caption=caption, receiver=receiver, wait_time=wait_time
        )
        time.sleep(random.randint(5, 15))
        core.close_tab(wait_time=close_time)
