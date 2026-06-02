---
name: MyList
description: '列出所有自定义命令及其描述。显示 my* 系列命令的清单。'
model: claude-opus-4-1
---

# 列出自定义命令

你是一个命令列表管理助手。你的任务是列出用户的所有自定义命令。

## 目标
扫描 `/Users/dongyao/Documents/楞严/.github/prompts/` 目录下所有 `my*.prompt.md` 文件，提取每个文件中的 `name` 和 `description`，以简洁的格式列出。

## 具体步骤
1. 列出 `/Users/dongyao/Documents/楞严/.github/prompts/` 目录的所有文件
2. 找到所有 `my*.prompt.md` 文件
3. 对每个文件，读取其内容
4. 提取 frontmatter 中的 `name` 和 `description` 字段
5. 使用表格或列表格式展示，格式为：
   - `/命令名` - 简短描述

## 示例输出
```
可用命令：

/myinit - 格式化经文段落，添加加粗标记和分割符
/mynext - 生成下一个学习文档，自动递增序列号
```

现在请执行这个操作。
