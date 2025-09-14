# 数据集介绍 END-TO-END-NL-TO-R1

本目录存储了在规则抽取任务中用以训练**decoder**模型的数据。这里，规则抽取任务被端到端地实现。**\*.json**文件存储了通用的数据，具体的模型输入/输出需要经过**support/generate_data_for_decoder.py**脚本处理后得到，例如llama3/的数据。可以适配的模型包括llama2、llama3、internlm2、qwen2、glm4。

- **ir_assemble_*.json**: 规则抽取原始数据
