import re
from typing import List, Tuple

class WhatsAppChatParser:
    def __init__(self, path: str):
        self.path: str = path
        
        self._regex: str = r'(\d+/\d+/\d+, \d{1,2}:\d{2}\s*[APap][Mm]\s*-\s*)|\[\d+/\d+/\d+, \d{1,2}:\d{2}:\d{2} [APM]{2}\]'
        self._extract_info: str = r"(?:\d{2}/\d{2}/\d{4},?\s+\d{1,2}:\d{2}(?:\s?[apAP][mM])?\s*-\s*|\[\d{4}/\d{1,2}/\d{1,2},?\s+\d{1,2}:\d{2}:\d{2}\s+[APM]{2}\]\s*|\[\d{2}/\d{2}/\d{4},?\s+\d{1,2}:\d{2}:\d{2}\s+[APM]{2}\]\s*)([^:]+):\s*(.*)"
        
        self.messages: List[str] = []
        self.subject_list: List[str] = []
        self.message_list: List[str] = []
        self.subjects: set = set()

        self._parse()
        self._extract()

    def _extract(self):
        for message in self.messages:
            match = re.match(self._extract_info, message)
            if match:
                sender, text = match.groups()
                self.subject_list.append(sender)
                self.message_list.append(text)

        self.subjects = set(self.subject_list)
    
    def _parse(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove all occurrences of \u200e
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

        self.messages = messages

    def retrieve_subjects_and_messages(self) -> Tuple[List[str], List[str]]:
        return self.subject_list, self.message_list
