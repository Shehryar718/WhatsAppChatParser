import re
import pandas as pd
from typing import List, Tuple

class WhatsAppChatParser:
    def __init__(self, path: str, turns: bool = True):
        self.path: str = path
        
        self._regex: str = r'(\d+/\d+/\d+, \d{1,2}:\d{2}\s*[APap][Mm]\s*-\s*)|\[\d+/\d+/\d+, \d{1,2}:\d{2}:\d{2} [APM]{2}\]'
        self._extract_info: str = r"(?:\d{2}/\d{2}/\d{4},?\s+\d{1,2}:\d{2}(?:\s?[apAP][mM])?\s*-\s*|\[\d{4}/\d{1,2}/\d{1,2},?\s+\d{1,2}:\d{2}:\d{2}\s+[APM]{2}\]\s*|\[\d{2}/\d{2}/\d{4},?\s+\d{1,2}:\d{2}:\d{2}\s+[APM]{2}\]\s*)([^:]+):\s*(.*)"
        
        self.messages: List[str] = []
        self.subject_list: List[str] = []
        self.message_list: List[str] = []
        self.subjects: set = set()

        self._parse()
        self._extract()

        if turns: self._format_turns()

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

    def _format_turns(self):
        subjects: List[str] = [self.subject_list[0]]
        messages: List[str] = [self.message_list[0]]

        current_subject: str = self.subject_list[0]
        for subject, message in zip(self.subject_list[1:], self.message_list[1:]):
            if subject != current_subject:
                current_subject = subject
                subjects.append(current_subject)
                messages.append(message)
            else:
                messages[-1] += ' ' + message

        self.subject_list = subjects
        self.message_list = messages

    def retrieve_subjects_and_messages(self) -> Tuple[List[str], List[str]]:
        return self.subject_list, self.message_list
    
    def get_main_subject(self) -> str:
        return self.subject_list[0]
    
    def set_main_subject(self, subject: str):
        if subject not in self.subjects:
            raise ValueError(f"Subject '{subject}' not found in the chat.")

        if subject == self.get_main_subject():
            return

        self.message_list = self.message_list[1:]
        self.subject_list = self.subject_list[1:]

    def replace_subject(self, old_subject: str, new_subject: str):
        if old_subject not in self.subjects:
            raise ValueError(f"Subject '{old_subject}' not found in the chat.")

        self.subject_list = [new_subject if subject == old_subject else subject for subject in self.subject_list]
        
    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(zip(self.subject_list, self.message_list), columns=['subject', 'message'])
    
    def to_csv(self, path: str) -> None:
        df = self.to_frame()
        df.to_csv(path, index=False)

    def to_json(self, path: str) -> None:
        df = self.to_frame()
        df.to_json(path, orient='records', lines=True)
