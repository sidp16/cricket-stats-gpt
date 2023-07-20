import json
import openai

training_data = [
    {
        "prompt": "",
        "completion": "",
    },
    {
        "prompt": "",
        "completion": "",
    },
]

if __name__ == "__main__":
    file_name = "training_data.jsonl"

    with open(file_name, "w") as output_file:
        for entry in training_data:
            json.dump(entry, output_file)
            output_file.write("\n")
