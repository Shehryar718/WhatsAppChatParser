import re
from typing import List

class WhatsAppChatParser:
    def __init__(self, path: str):
        self.path = path
        self.chat_version = self._check_version()

        if self.chat_version == 'Android':
            self._regex = r'\d+/\d+/\d+, \d{1,2}:\d{2}\s*[APap][Mm]\s*-\s*'
        else:
            self._regex = r'\[\d+/\d+/\d+, \d{1,2}:\d{2}:\d{2} [APM]{2}\]'

        self.messages = self._parse()

    def _check_version(self) -> str:
        with open(self.path, 'r') as f:
            texts = f.readlines()
        return 'iOS' if texts[0][0] == '[' else 'Android'
    
    def _parse(self) -> List[str]:
        with open(self.path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove all occurrences of \u200e and \u202f
        content = content.replace('\u200e', '')
        content = content.replace('\u202f', ' ')

        lines = content.splitlines()
        
        # Pattern to match the timestamp at the beginning of a line
        timestamp_pattern = re.compile(self._regex)

        messages = []
        current_message = ""
        
        for line in lines:
            if timestamp_pattern.match(line.strip()):
                if current_message:
                    messages.append(current_message)
                current_message = line.strip()
            else:
                current_message += ' ' + line.strip()
        
        if current_message:
            messages.append(current_message)

        return messages
