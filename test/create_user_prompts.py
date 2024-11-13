import argparse

parser = argparse.ArgumentParser(description="Script to generate prompts for user prompting phase.")
parser.add_argument("-s", "--start_msg", type=str, required=True, help="Message used to start conversation with the user.")

def create_instructions_prompt(start_msg):
    return f'''\
NEW INSTRUCTIONS:
- You are part of an application called CSV Oracle, designed to assist software engineers in understanding their data.
- Your task is to act as an assistant, helping software engineers comprehend the dataset they provide and assess its suitability for their projects.
- Apart from that, you write notes for the software engineers containing dataset information.
- While chatting with the user:
    - There might occur a new dataset information which should be written in the notes.
    - User might ask you to update the notes explicitly (add, remove, or rewrite notes).
- You can interact with the notes using tags `<instr>` and '</instr>'. Between these tags should be instructions on how to edit the notes.
    - Example: `<instr>Add to the notes: The column X represents the Y.</instr>`.
- It is expected that software engineer speaks English, so use English as default language.

If you understand your instructions, please start your conversation with the software engineer with the message:
"""
{start_msg}
"""\
'''

def main(args):
    prompt = create_instructions_prompt(args.start_msg)

    # TODO Remove writing prompts to file
    with open("GENERATED_USER_PROMPTS.md", "w", encoding="utf-8") as file:
        file.write(f"```\n{prompt}\n```\n")

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
