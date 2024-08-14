import json
import os


# 打开JSON文件并读取数据
with open('/Users/njyzlzf/Documents/Elite/Doc/Definition.json', 'r', encoding='utf-8') as file:
    file_content = file.read()

# 使用json.loads解析JSON字符串
data = json.loads(file_content)
print(data)



# 设置文件夹路径
folder_path = '/prompts'

# 假设你有三个JSON文件：file1.json, file2.json, file3.json
file_names = ['definition', 'data_structure']

# 初始化一个字典来存储所有的prompts
prompts = {}

# 遍历文件名列表
for file_name in file_names:
    # 构建完整的文件路径
    file_path = f"{folder_path}/{file_name}.json"
    
    # 打开并读取JSON文件
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            # 将JSON数据加载到字典中
            prompts[file_name] = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error reading {file_name}: {e}")
        except FileNotFoundError as e:
            print(f"File {file_name} not found: {e}")

# 现在，prompts字典包含了所有的prompts，你可以根据文件名来访问它们
# 例如，要获取file1.json的内容，可以使用prompts['file1.json']

# 如果你想要将每个文件的内容分别赋值给不同的变量，可以这样做：
prompt1 = prompts.get('definition')
print(prompt1)