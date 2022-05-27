import utils


def generate_text(
    tok,
    model,
    start_string,
    no_response_text,
    do_sample=True,
    max_generated_length=100,
    min_generated_length=5,
    repetition_penalty=9.0,
    top_k=10, top_p=0.8, temperature=0.9,
    num_beams=5,
    no_repeat_ngram_size=0,
    eos_token_id=203,
    early_stopping=True,
    bad_words_ids=["&quot;.", "quot", "&raquo;.", "&nbsp;", "???",
                   "??????", "<s>", "?!", "??", "????", r"\n"]):

    input_ids = tok.encode(start_string, return_tensors="pt").cuda()
    out = model.generate(
        input_ids.cuda(),
        max_length=len(tok(start_string).input_ids) + max_generated_length,
        min_length=min_generated_length,
        repetition_penalty=repetition_penalty,
        do_sample=do_sample,
        top_k=top_k, top_p=top_p, temperature=temperature,
        num_beams=num_beams, no_repeat_ngram_size=no_repeat_ngram_size,
        eos_token_id=eos_token_id,
        early_stopping=early_stopping,
        bad_words_ids=[tok(bad_word).input_ids for bad_word in bad_words_ids])

    text = list(map(tok.decode, out))[0]
    text = text.replace(start_string, "").replace("<s>", "").strip()
    if(text == start_string or
        utils.remove_prefix(
            start_string.split("\n")[-1], utils.load_string(
                "bot_name") + ":").strip() is text or 
                text.replace(" ", "") == ""):
        return no_response_text
    elif (len(text) >= 400):
        text_truncated_to_last_dot = '.'.join(text.split('.')[:-1])
        if text == text_truncated_to_last_dot:
            return no_response_text
        else:
            return text_truncated_to_last_dot
    else:
        return text


def generate_response(
        tok,
        model,
        prompt_beginning,
        bot_message_list,
        user_message_list,
        bot_name,
        user_name,
        no_response_text):

    prompt = (prompt_beginning + "\n")

    for i in range(len(bot_message_list)):
        prompt = (prompt + bot_name + ":" + bot_message_list[i] +
                  "\n" + user_name + ":" + user_message_list[i] + "\n")

    prompt = prompt + "Чат-бот:"

    return generate_text(tok, model, prompt, no_response_text)