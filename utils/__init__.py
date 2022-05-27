def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def load_tokenizer_and_model(model_name_or_path):
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    return (GPT2Tokenizer.from_pretrained(model_name_or_path),
            GPT2LMHeadModel.from_pretrained(model_name_or_path).cuda())


def load_string(name):
    import json
    with open('strings.json') as f:
        loaded_string = json.load(f)[name]
    return loaded_string
