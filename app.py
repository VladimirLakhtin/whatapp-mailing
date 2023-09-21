from functools import partial
import logging
import os
import random
import re
import sys
import time
from typing import List

from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QFileDialog,
                             QVBoxLayout, QHBoxLayout, QTextEdit, QLabel)
from pynput.keyboard import Key, Controller
import pywhatkit as w

logger = logging.getLogger()


class Window(QWidget):

    sub_letters = {'а': 'a', 'е': 'e', 'с': 'c', 'р': 'p', 'у': 'y', 'о': 'o', 'х': 'x'}

    def __init__(self):
        super(Window, self).__init__()
        self.keyboard = Controller()
        self.workdir = ''
        self.initUI()

    def initUI(self):
        self.image = None
        self.numbers = []
        self.msg = 'Введите сообщение...'

        self.count_numbers = QLabel('Количество номеров: -')
        self.time_to_send = QLabel('Прогнозируемое время рассылки: -')
        self.image_text = QLabel('Изображение не выбрано')
        self.send_btn = QPushButton('Начать рассылку')
        self.choose_btn = QPushButton('Добавить номера')
        self.edit_message = QPushButton('Редактировать сообщение')
        self.add_image = QPushButton('Добавить изображение')
        self.ok_btn = QPushButton('Ок')
        self.cancel_btn = QPushButton('Отмена')
        self.table = QTextEdit()

        btns_layout = QHBoxLayout()
        btns_layout.addWidget(self.ok_btn)
        btns_layout.addWidget(self.cancel_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.choose_btn)
        main_layout.addWidget(self.count_numbers)
        main_layout.addWidget(self.time_to_send)
        main_layout.addWidget(self.image_text)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.edit_message)
        main_layout.addWidget(self.add_image)
        main_layout.addWidget(self.send_btn)
        main_layout.addLayout(btns_layout)

        self.setLayout(main_layout)

        self.ok_btn.hide()
        self.cancel_btn.hide()

        self.choose_btn.clicked.connect(self.get_numbers_from_file)
        self.edit_message.clicked.connect(self.show_message_editor)
        self.add_image.clicked.connect(self.add_image_func)
        self.ok_btn.clicked.connect(partial(self.back_menu,True))
        self.cancel_btn.clicked.connect(partial(self.back_menu,False))
        self.send_btn.clicked.connect(self.start_sending)

    def send_message(self, number) -> None:
        """Send one message"""

        try:
            if self.image:
                w.sendwhats_image(
                    img_path=self.image,
                    caption=self.msg,
                    receiver=number,
                )
            else:
                w.sendwhatmsg_instantly(
                    phone_no=number,
                    message=self.msg,
                    tab_close=True
                )
                self.keyboard.press(Key.enter)
                self.keyboard.release(Key.enter)
                time.sleep(random.randint(10, 50))
        except Exception as e:
            logger.error(str(e))
        else:
            logger.info(f"Send message to number: {number}")

    def start_sending(self) -> None:
        """Start sending messages"""

        logger.info("Start sending messages")
        for i, number in enumerate(self.numbers):
            self.msg = self.random_message_transformer(self.msg)
            self.send_message(number)

    @classmethod
    def random_message_transformer(cls, msg: str) -> str:
        """Replace symbols in message to increase it unique"""

        return ''.join([
            cls.sub_letters[sym]
            if sym in cls.sub_letters and random.uniform(0, 1) > 0.5
            else sym
            for i, sym in enumerate(msg)
        ])

    def get_numbers_from_file(self) -> None:
        """Read and display numbers info from file"""

        file_path = QFileDialog.getOpenFileName()[0]
        if not file_path.endswith('.txt'):
            logger.error("File with numbers should ends with: '.txt'")

        with open(file_path, 'r', encoding='utf-8') as file:
            numbers = file.readlines()

        self.numbers = self.format_numbers(numbers)
        self.table.setText('\n'.join(self.numbers))
        self.count_numbers.setText(f'Количество номеров: {len(self.numbers)}')
        sending_time = self.get_sending_time_str(len(self.numbers))
        self.time_to_send.setText(sending_time)

    @staticmethod
    def format_numbers(numbers: List) -> List:
        """Transform the numbers to the correct format"""

        return [
            '+7' + re.sub(r'[\(\)\- "\n+]', '', num)[1:]
            for num in numbers
            if len(num) > 10
        ]

    @staticmethod
    def get_sending_time_str(count_numbers: int) -> str:
        """Calculate sending message time"""

        mes_time_to_send = 'Прогнозируемое время рассылки: '
        mins = count_numbers * (16 + 30) // 60
        hours, mins = divmod(mins, 60)
        mes_time_to_send += f'{hours} ч' if hours else ''
        return mes_time_to_send + f'{mins} мин'

    def show_message_editor(self) -> None:
        """Show message edit"""

        self.ok_btn.show()
        self.cancel_btn.show()
        self.count_numbers.hide()
        self.time_to_send.hide()
        self.image_text.hide()
        self.send_btn.hide()
        self.choose_btn.hide()
        self.edit_message.hide()
        self.add_image.hide()
        self.table.setText(self.msg)

    def back_menu(self, is_edit) -> None:
        """Back to menu from message editor"""

        self.ok_btn.hide()
        self.cancel_btn.hide()
        self.count_numbers.show()
        self.time_to_send.show()
        self.image_text.show()
        self.send_btn.show()
        self.choose_btn.show()
        self.edit_message.show()
        self.add_image.show()
        if is_edit:
            self.msg = self.table.toPlainText()
            logger.debug("Message is edited")
        self.table.setText('\n'.join(self.numbers))

    def add_image_func(self) -> None:
        """Add image from file"""

        image_path = QFileDialog.getOpenFileName()[0]
        if not image_path.endswith(('.jpeg', '.jpg', '.png')):
            logger.error("Image file should ends with: '.jpeg', '.jpg', '.png'")
        self.image = image_path
        image_filename = os.path.split(image_path)[-1]
        self.image_text.setText(f"Выбрано изображение: {image_filename}")


if __name__ == "__main__":
    logging.basicConfig(
        level='DEBUG',
        filename='app_logs.log',
        filemode='a',
        format="%(asctime)s || %(levelname)s || %(message)s",
        datefmt='%H:%M:%S',
    )

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    logger.debug('App started')
    app.exec()
