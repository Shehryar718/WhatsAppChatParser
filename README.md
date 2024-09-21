# WhatsApp Chat Parser

## Overview

The `WhatsAppChatParser` is a Python class designed to parse and process exported WhatsApp chat data. It reads a chat file, extracts sender and message information, and provides functionalities to reformat the data for various use cases, such as data frames, CSV, and JSONL files suitable for machine learning or natural language processing tasks.

## Features

- **Parsing**: Extracts and structures chat messages by sender and timestamp.
- **Formatting**: Groups consecutive messages from the same sender.
- **Exporting**: Allows exporting parsed data to CSV, JSONL, and structured prompt-completion and user-assistant formats for training AI models.

## Usage

### 1. Initializing the Parser

```python
from WhatsAppChatParser import WhatsAppChatParser

# Initialize with the path to the WhatsApp chat file
parser = WhatsAppChatParser('path_to_chat_file.txt', turns=True)
```

- `path`: The path to the exported WhatsApp chat file.
- `turns`: If set to `True`, consecutive messages from the same sender will be combined into a single message.

### 2. Retrieving Data

You can retrieve the processed subjects and messages:

```python
subjects, messages = parser.retrieve_subjects_and_messages()
```

### 3. Exporting Data

You can export the data into different formats:

- **To DataFrame:**

  ```python
  df = parser.to_frame()
  ```

- **To CSV:**

  ```python
  parser.to_csv('output.csv')
  ```

- **To JSONL:**

  ```python
  parser.to_jsonl('output.jsonl')
  ```

- **To Prompt-Completion Format (JSONL):**

  ```python
  parser.export_prompt_completion('prompt_completion.jsonl')
  ```

- **To User-Assistant Format (JSONL):**

  ```python
  parser.export_user_assistant('user_assistant.jsonl')
  ```

### 4. Managing Subjects

You can get or set the main subject (sender) in the conversation:

```python
main_subject = parser.get_main_subject()
parser.set_main_subject('New Subject')
```

Replace a subject in the chat:

```python
parser.replace_subject('Old Subject', 'New Subject')
```

## Example

```python
parser = WhatsAppChatParser('chat.txt', turns=True)
df = parser.to_frame()
parser.to_csv('chat_output.csv')
parser.export_prompt_completion('chat_prompts.jsonl')
parser.export_user_assistant('chat_user_assistant.jsonl')
parser.export_user_assistant_single('chat_user_assistant_single.jsonl')
```

## Error Handling

- **File Format Errors**: The class expects a standard WhatsApp chat export. Ensure the file is in the correct format.
- **Value Errors**: When replacing or setting subjects, make sure the subject exists in the chat data.

---

For any issues or contributions, feel free to submit a pull request or open an issue on the GitHub repository.
