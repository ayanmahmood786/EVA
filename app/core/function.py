import re
from concurrent.futures import ThreadPoolExecutor
import asyncio

executor = ThreadPoolExecutor(max_workers=50)

def clean_response(result):
    result=result.replace("**","\\b")
    result = re.sub(r'\\b(.*?)\\b', r'<strong>\1</strong>', result)
    result=result.replace("```json","").replace("```","")
    result=result.replace("##","")
    return result



def run_in_thread(func, *args):
    """Helper to run sync code in threadpool"""
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(executor, func, *args)

def format_answer(answer):
    answer=answer.replace("**","\\b")
    answer = re.sub(r'\\b(.*?)\\b', r'<strong>\1</strong>', answer)
    return answer
