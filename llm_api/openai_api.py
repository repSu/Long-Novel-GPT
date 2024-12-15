import httpx
from openai import OpenAI

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_api.chat_messages import ChatMessages
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
        messages[0:1] = [{'role': 'user', 'content': messages[0]['content']}, {'role': 'assistant', 'content': ''}]
    
    chatstream = client.chat.completions.create(
        stream=True,
        model=model, 
        messages=messages, 
        max_tokens=max_tokens,
        response_format={ "type": "json_object" } if response_json else None,
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
        stream_chat_with_gpt(messagesBase, model='gpt-4o', response_json=True, api_key=api_key, base_url=base_url, max_tokens=max_tokens, n=n, proxies=proxies)
    return messages
      
if __name__ == '__main__':
    pass
    messages = ChatMessages()
    messages.append({'role': 'user', 'content': '###任务\n我会给你小说的剧情和正文，需要你将剧情和正文对应上。\n\n###剧情\n  \n（1）李珣担心回山后被师门发现，不知如何解释。\n \n  \n（2）担心师门如何看待他。\n \n  \n（3）这些事李珣无法面对。\n \n  \n（4）他害怕被师门找到，内心充满负罪感。\n \n  \n（5）决定离开躲避，认为血魇的事不急。\n \n  \n（6）为了躲避各方势力，他选择西城门离开。\n \n  \n（7）他低调出城，计划出城后御剑飞行。\n \n  \n（8）南城恢复人气，李珣的打扮不引人注目。\n \n  \n（9）他用步法快速走到西城门，天色渐晚。\n \n  \n（10）他计划出城后找个地方御剑飞行。\n \n  \n（11）出城顺利，他松了口气，快速离开城门。\n \n  \n（12）他寻找僻静处准备御剑。\n \n  \n（13）一个神秘的女冠叫住了他。\n \n\n\n###正文\n  \n（1）李珣站在城墙的阴影下，心中如同翻滚的海浪。他的目光不时扫向远处的山脉，那里是他的师门所在。\n  \n（2）回山后如何解释自己的行为，他无从下手。师门的目光如同无形的枷锁，令他喘不过气来。\n\n  \n（3）他无法面对这些事情，内心的负罪感如同沉重的石块压在心头。\n  \n（4）他害怕被师门找到，害怕那双审视的眼睛。他决定暂时离开，血魇的事情可以稍后再说。\n\n  \n（5）为了躲避各方势力的追踪，他选择了西城门。南城的人气渐渐恢复，他的打扮在熙熙攘攘的人群中并不显眼。\n  \n（6）他低着头，步伐轻快地穿过街道，天色渐晚，暮色为他提供了天然的掩护。\n\n  \n（7）出城的过程比他想象中顺利得多，城门的守卫并未多加盘问。他松了一口气，快步离开城门，心中盘算着出城后御剑飞行的计划。\n\n  \n（8）在一处僻静的林间空地，他停下脚步，准备御剑。然而，就在此时，一个清冷的声音从身后传来：“这位道友，请留步\n。”\n\n  \n（9）李珣心中一紧，转过身来。那是一位女冠，衣着打扮如同道士，神情淡然。\n  \n（10）李珣勉强挤出一个微笑，心中却不安如潮。他感觉自己被看穿，仿佛所有的秘密都暴露在对方的目光下。\n\n  \n（11）“你是明心剑宗的弟子？”女冠问道。\n\n  \n（12）李珣点了点头，心中忐忑不安，不敢反问女冠的来历。\n“你来此有何目的？”女冠继续问。\n\n  \n（13）李珣心中一动，谎称自己不知道，装出一副可怜的样子，希望能让谎言显得真实。\n\n\n\n###输出格式\n//以JSON格式输出\n{ \n"1": [1, 2, ...], //在列表中依次填写剧情段1对应的一个或多个连续的正文段序号\n"2": [...], //在列表中依次填写剧情段2对应的一个或多个连续的正文段序号\n... //对每个剧情段都需要填写其对应的正文段序号，每个序号只能提及一次\n}'})
    GPT_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdXRoMHx1c2VyXzAxSkVRWjYxRUo2NTM4SldGNVFGODJENFlEIiwidGltZSI6IjE3MzM5MDUwNzciLCJyYW5kb21uZXNzIjoiMTdhZTc2OGQtNmQwYi00YzE0IiwiZXhwIjo0MzI1OTA1MDc3LCJpc3MiOiJodHRwczovL2F1dGhlbnRpY2F0aW9uLmN1cnNvci5zaCIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgb2ZmbGluZV9hY2Nlc3MiLCJhdWQiOiJodHRwczovL2N1cnNvci5jb20ifQ.yGHAosy1oOfXpQGxKpIPhTkaRDh2LzP5CzqS7ujtA9U'
    client_params = {
        "api_key": GPT_API_KEY,
        "base_url": "http://192.168.1.200:9600/v1",
    }
    n = 1
    max_tokens = 4096
    response_json = True
    client = OpenAI(**client_params)
    chatstream = client.chat.completions.create(
        stream=True,
        model="claude-3.5-sonnet", 
        messages=messages, 
        max_tokens=max_tokens,
        response_format={ "type": "json_object" } if response_json else None,
        n=n
    )
    
    messages.append({'role': 'assistant', 'content': ''})
    content = ['' for _ in range(n)]
    for part in chatstream:
        for choice in part.choices:
            content[choice.index] += choice.delta.content or ''
            messages[-1]['content'] = content if n > 1 else content[0]
            print(messages)
    
    print(content)
