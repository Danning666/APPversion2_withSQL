import prompts_temple
from data_parse import build_info_prompt


def build_prompt_system():
    data_info = build_info_prompt.data_info
    prompt_system = f"{prompts_temple.prompt_system_temple}"
    return prompt_system


def build_prompt_sql(question):
    prompt_system = build_prompt_system()
    data_structure = build_info_prompt.data_structure
    structure_str = ", ".join(
        [f"{col} ({dtype})" for col, dtype in data_structure.items()]
    )
    prompt_sql = f"{prompts_temple.prompt_sql_temple}"
    print(prompt_sql)


def build_prompt_ans1(question, result):
    prompt_system = build_prompt_system()
    prompt_ans = f"{prompts_temple.prompt_ans_temple}"
    return prompt_ans


def build_prompt_ans2(question):
    data_structure = build_info_prompt.data_structure
    structure_str = ", ".join(
        [f"{col} ({dtype})" for col, dtype in data_structure.items()]
    )
    document = structure_str
    prompt_ans = f"{prompts_temple.prompt_ans_temple2}"
    return prompt_ans