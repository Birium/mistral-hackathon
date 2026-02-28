import os
import re
from openai import OpenAI
from typing import Tuple
from pathlib import Path
from agent.editor.prompt_editor import SYSTEM_PROMPT
from agent.context.context import Contexts
from agent.document.document import Document, Version
from agent.message.message import HumanMessage, SystemMessage, Message
from pydantic import BaseModel
from typing import List
from model_config import ModelConfig, CLAUDE_3_5_HAIKU
from utils.object_logger import object_logger

class SearchReplace(BaseModel):
    search: str
    replace: str

class Editor:
    def __init__(self, model: ModelConfig = CLAUDE_3_5_HAIKU):
        self.client = OpenAI(
            base_url=model.base_url,
            api_key=model.api_key
        )
        self.model = model
        self.cost_details = None
    
    def extract_edits(self, diff_text: str) -> List[SearchReplace]:
        pattern = r'<<<<<<< SEARCH\n(.*?)=======\n(.*?)>>>>>>> REPLACE'
        edit_blocks = re.findall(pattern, diff_text, re.DOTALL)
        
        search_replace_pairs = []
        for block in edit_blocks:
            if len(block) == 2:
                search_text, replace_text = block
                search_text = search_text.strip()
                search_replace_pairs.append(SearchReplace(search=search_text, replace=replace_text))
                
        return search_replace_pairs
    
    def edit(self, content: str, query: str, document : Document, contexts: Contexts) -> Tuple[str, List[SearchReplace]]:
        try:
            messages : List[Message] = [
                SystemMessage(content=SYSTEM_PROMPT)
            ]
            
            messages.append(contexts.to_message())
            messages.append(document.to_message())
            messages.append(HumanMessage(content=f"<user_instructions>\n{query}\n</user_instructions>"))
            messages_serialized = [mess.to_dict() for mess in messages]
            object_logger.log_object(messages_serialized)

            completion = self.client.chat.completions.create(
                model=self.model.model_id,
                messages=messages_serialized
            )
            search_replace_pairs = self.extract_edits(completion.choices[0].message.content)
            edited_content = self.apply_edits(content, search_replace_pairs)

            prompt_tokens = completion.usage.prompt_tokens
            completion_tokens = completion.usage.completion_tokens
            self.cost_details = self.model.calculate_cost(prompt_tokens, completion_tokens)

            return edited_content, search_replace_pairs
            
        except Exception as e:
            print(f"Error calling API: {e}")
            return content, []
    
    def apply_edits(self, original_text: str, search_replace_pairs: List[SearchReplace]) -> str:
        if not search_replace_pairs:
            return original_text
        
        result = original_text
        for sr_pair in search_replace_pairs:
            if sr_pair.search in result:
                result = result.replace(sr_pair.search, sr_pair.replace)
                    
        return result

def test_editor():
    editor = Editor()
    file_path = "../../data/test.md"
    new_path = Path(file_path).with_stem(f"{Path(file_path).stem}_v2")

    document = Document(name=Path(file_path).stem)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        version = Version(id=1, content=content, instruction="Initial version")
        document.versions.append(version)
        document.current_version_id = 1

    contexts = Contexts(contexts=[])
    
    query = "Phase 1 Sign-off etait le 2 october et l'UX Designer s'appelle Eddie"
    edited_content, search_replace_pairs = editor.edit(content, query, document, contexts)
    
    for sr_pair in search_replace_pairs:
        print(f"\nSEARCH:\n{sr_pair.search}\n\nREPLACE:\n{sr_pair.replace}\n{'-'*50}")

    with open(new_path, 'w', encoding='utf-8') as file:
        file.write(edited_content)
    print(f"Successfully saved edited content to {new_path}")