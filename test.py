from WhatAppChatParser import WhatsAppChatParser

if __name__ == "__main__":

    path = "sample_chats/sample_chat2.txt"
    parser = WhatsAppChatParser(path)
    subjects, messages = parser.retrieve_subjects_and_messages()
    
    print("----------- subjects -----------\n")
    print(parser.subjects)

    print("\n----------- extracted messages -----------\n")
    for subject, message in zip(subjects[:5], messages[:5]):
        print(f"{subject}:  \t{message}")

    print("\n----------- raw messages ----------\n")
    for message in parser.messages[:5]:
        print(message)