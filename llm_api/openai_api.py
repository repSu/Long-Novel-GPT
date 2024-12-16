import httpx
from openai import OpenAI

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .chat_messages import ChatMessages
# Pricing reference: https://openai.com/api/pricing/
gpt_model_config = {
    "gpt-4o": {
        "Pricing": (2.50/1000, 10.00/1000),
        "currency_symbol": '$',
    },
    "gpt-4o-mini": {
        "Pricing": (0.15/1000, 0.60/1000),
        "currency_symbol": '$',
    },
    "o1-preview": {
        "Pricing": (15/1000, 60/1000),
        "currency_symbol": '$',
    },
    "o1-mini": {
        "Pricing": (3/1000, 12/1000),
        "currency_symbol": '$',
    },
}
# https://platform.openai.com/docs/guides/reasoning


def stream_chat_with_gpt(messages, model='gpt-3.5-turbo-1106', response_json=False, api_key=None, base_url=None, max_tokens=4_096, n=1, proxies=None):
    if api_key is None:
        raise Exception('未提供有效的 api_key！')

    messagesBase = messages
    # needGPT = "我会给你小说的剧情和正文，需要你将剧情和正文对应上"
    # if needGPT in messages[0]['content']:
    #     model = 'gpt-4o'
    client_params = {
        "api_key": api_key,
    }

    if base_url:
        client_params['base_url'] = base_url

    if proxies:
        httpx_client = httpx.Client(proxy=proxies)
        client_params["http_client"] = httpx_client

    client = OpenAI(**client_params)

    if model in ['o1-preview', ] and messages[0]['role'] == 'system':
        messages[0:1] = [{'role': 'user', 'content': messages[0]['content']}, {
            'role': 'assistant', 'content': ''}]

    chatstream = client.chat.completions.create(
        stream=True,
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        response_format={"type": "json_object"} if response_json else None,
        n=n
    )

    messages.append({'role': 'assistant', 'content': ''})
    content = ['' for _ in range(n)]
    for part in chatstream:
        for choice in part.choices:
            content[choice.index] += choice.delta.content or ''
            messages[-1]['content'] = content if n > 1 else content[0]
            yield messages

    if messages[1]['content'] == '':
        stream_chat_with_gpt(messagesBase, model='gpt-4o', response_json=True,
                             api_key=api_key, base_url=base_url, max_tokens=max_tokens, n=n, proxies=proxies)
    return messages


if __name__ == '__main__':
    pass
    