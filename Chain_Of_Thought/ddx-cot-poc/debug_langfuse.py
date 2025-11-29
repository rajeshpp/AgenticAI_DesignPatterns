from dotenv import load_dotenv
load_dotenv()
import os
print('OPENAI_API_KEY set?', bool(os.getenv('OPENAI_API_KEY')))
print('LANGFUSE_SECRET_KEY', repr(os.getenv('LANGFUSE_SECRET_KEY')))
print('LANGFUSE_PUBLIC_KEY', repr(os.getenv('LANGFUSE_PUBLIC_KEY')))
print('LANGFUSE_BASE_URL', repr(os.getenv('LANGFUSE_BASE_URL')))

try:
    from langfuse import get_client
    from langfuse.langchain import CallbackHandler
    client = get_client()
    print('get_client returned:', type(client))
    handler = CallbackHandler()
    print('CallbackHandler created:', type(handler))
except Exception as e:
    print('Exception creating langfuse client/handler:')
    import traceback
    traceback.print_exc()
