import re
import json
import pandas as pd
from typing import List, Tuple, Dict

class WhatsAppChatParser:
    """
    A class to parse WhatsApp chat logs, extracting senders (subjects) and their corresponding messages.
    It provides various methods for formatting, analyzing, and exporting the chat data.

    Attributes:
    -----------
    path : str
        The file path of the WhatsApp chat log.
    messages : List[str]
        List containing the parsed raw messages from the chat log.
    subject_list : List[str]
        List of senders extracted from the chat log.
    message_list : List[str]
        List of messages corresponding to the senders.
    subjects : set
        Set of unique senders (subjects) extracted from the chat log.

    Methods:
    --------
    _extract():
        Extracts the senders and messages from the parsed raw chat data.
    _parse():
        Reads and processes the chat log file to identify individual messages.
    _format_turns():
        Combines consecutive messages from the same sender into a single entry.
    retrieve_subjects_and_messages() -> Tuple[List[str], List[str]]:
        Retrieves the parsed list of senders and corresponding messages.
    get_main_subject() -> str:
        Returns the first sender in the chat (main subject).
    set_main_subject(subject: str):
        Sets a new main subject for the chat, adjusting the message list accordingly.
    replace_subject(old_subject: str, new_subject: str):
        Replaces all occurrences of a sender's name with a new name.
    to_frame() -> pd.DataFrame:
        Converts the parsed data into a pandas DataFrame with columns 'subject' and 'message'.
    to_csv(path: str):
        Exports the parsed chat data to a CSV file.
    to_jsonl(path: str):
        Exports the parsed chat data to a JSONL file.
    export_prompt_completion(path: str):
        Exports the chat data in a prompt-completion format for fine-tuning language models.
    export_user_assistant(path: str):
        Exports chat data in a user-assistant format for training dialogue models.
    export_user_assistant_single(path: str):
        Exports the chat data where a single main subject acts as the user, and others act as the assistant.
    """
    def __init__(self, path: str, turns: bool = True):
        """
        Initializes the WhatsAppChatParser with the chat file path and sets up parsing.

        Parameters:
        -----------
        path : str
            The path to the WhatsApp chat log file.
        turns : bool, optional
            If True, combines consecutive messages from the same sender into one (default is True).
        """
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
        """
        Extracts the sender and message content from each parsed message.
        The extracted data is stored in `subject_list` and `message_list`.
        """
        for message in self.messages:
            match = re.match(self._extract_info, message)
            if match:
                sender, text = match.groups()
                self.subject_list.append(sender)
                self.message_list.append(text)

        self.subjects = set(self.subject_list)
    
    def _parse(self):
        """
        Reads the chat log file, removes unwanted characters, and splits the content into individual messages.
        The parsed messages are stored in `messages`.
        """
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
        """
        Formats the chat log to group consecutive messages from the same sender into a single message.
        The formatted messages are stored in `subject_list` and `message_list`.
        """
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
        """
        Retrieves the parsed list of senders (subjects) and their respective messages.

        Returns:
        --------
        Tuple[List[str], List[str]]:
            A tuple containing the list of senders and the list of messages.
        """
        return self.subject_list, self.message_list
    
    def get_main_subject(self) -> str:
        """
        Retrieves the first sender (main subject) in the chat.

        Returns:
        --------
        str:
            The first sender's name.
        """
        return self.subject_list[0]
    
    def set_main_subject(self, subject: str):
        """
        Sets the main subject (sender) in the chat by removing the first subject and updating the lists accordingly.

        Parameters:
        -----------
        subject : str
            The name of the subject to set as the main subject.

        Raises:
        -------
        ValueError:
            If the specified subject is not found in the chat.
        """
        if subject not in self.subjects:
            raise ValueError(f"Subject '{subject}' not found in the chat.")

        if subject == self.get_main_subject():
            return

        self.message_list = self.message_list[1:]
        self.subject_list = self.subject_list[1:]

    def replace_subject(self, old_subject: str, new_subject: str):
        """
        Replaces all occurrences of a subject with a new name in the chat.
        
        Parameters:
        -----------
        old_subject : str
            The name of the subject to replace.
        new_subject : str
            The new name to replace the old subject.

        Raises:
        -------
        ValueError:
            If the specified subject is not found in the chat.
        """
        if old_subject not in self.subjects:
            raise ValueError(f"Subject '{old_subject}' not found in the chat.")

        self.subject_list = [new_subject if subject == old_subject else subject for subject in self.subject_list]
        
    def to_frame(self) -> pd.DataFrame:
        """
        Converts the parsed senders and messages into a pandas DataFrame.

        Returns:
        --------
        pd.DataFrame:
            A DataFrame with 'subject' and 'message' columns.
        """
        return pd.DataFrame(zip(self.subject_list, self.message_list), columns=['subject', 'message'])
    
    def to_csv(self, path: str) -> None:
        """
        Exports the parsed chat data to a CSV file.

        Parameters:
        -----------
        path : str
            The file path where the CSV will be saved.
        """
        df = self.to_frame()
        df.to_csv(path, index=False)

    def to_jsonl(self, path: str) -> None:
        """
        Exports the parsed chat data to a JSONL file.

        Parameters:
        -----------
        path : str
            The file path where the JSONL will be saved.
        """
        df = self.to_frame()
        df.to_json(path, orient='records', lines=True)

    def export_prompt_completion(self, path: str) -> None:
        """
        Exports the parsed chat data in a prompt-completion format for fine-tuning language models.
        Every alternate message is treated as a prompt and its corresponding response as a completion.

        Parameters:
        -----------
        path : str
            The file path where the JSONL data will be saved.

        Raises:
        -------
        ValueError:
            If the specified path does not end with '.jsonl'.
        """
        if not path.endswith('.jsonl'):
            raise ValueError("Please provide a valid JSONL (.jsonl) file path.")
        
        prompt: List[str] = []
        completion: List[str] = []

        for idx, message in enumerate(self.message_list):
            if idx%2 == 0:
                prompt.append(message)
            else:
                completion.append(message)

        df = pd.DataFrame(zip(prompt, completion), columns=['prompt', 'completion'])
        df.to_json(path, orient='records', lines=True)

    def export_user_assistant(self, path: str) -> None:
        """
        Exports the chat data in a user-assistant conversational format, with alternating user and assistant roles.

        Parameters:
        -----------
        path : str
            The file path where the JSONL data will be saved.

        Raises:
        -------
        ValueError:
            If the specified path does not end with '.jsonl'.
        """
        if not path.endswith('.jsonl'):
            raise ValueError("Please provide a valid JSONL (.jsonl) file path.")
        
        def create_dataset(user, assistant):
            """
            Creates a dataset for a single conversation turn.

            Parameters:
            -----------
            user : str
                The user's message.
            assistant : str
                The assistant's response.

            Returns:
            --------
            Dict[str, List[Dict[str, str]]]:
                A dictionary containing the conversation messages.
            """
            SYSTEM_MESSAGE = "You are a helpful assistant."
            return {
                "messages": [
                    {"role": "system", "content": SYSTEM_MESSAGE},
                    {"role": "user", "content": user},
                    {"role": "assistant", "content": assistant},
                ]
            }

        user: List[str] = []
        assistant: List[str] = []

        for idx, message in enumerate(self.message_list):
            if idx%2 == 0:
                user.append(message)
            else:
                assistant.append(message)

        df = pd.DataFrame(zip(user, assistant), columns=['user', 'assistant'])
        with open(path, "w") as f:
            for _, row in df.iterrows():
                string = json.dumps(create_dataset(row["user"], row["assistant"]))
                f.write(string + "\n")

    def export_user_assistant_single(self, path: str) -> None:
        """
        Exports the chat data in a single user-assistant conversation format, with the main subject as the user and the others as the assistant.

        Parameters:
        -----------
        path : str
            The file path where the JSONL data will be saved.

        Raises:
        -------
        ValueError:
            If the specified path does not end with '.jsonl'.
        """
        if not path.endswith('.jsonl'):
            raise ValueError("Please provide a valid JSONL (.jsonl) file path.")
        
        dataset: Dict[str, List[Dict[str, str]]] = {
            "messages": []
        }

        for subject, message in zip(self.subject_list, self.message_list):
            if subject == self.get_main_subject():
                dataset["messages"].append({"role": "user", "content": message})
            else:
                dataset["messages"].append({"role": "assistant", "content": message})

        with open(path, "w") as f:
            string = json.dumps(dataset)
            f.write(string + "\n")