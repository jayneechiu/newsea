# Contributing to Reddit Newsletter Bot

感谢您对贡献本项目的兴趣！以下是参与贡献的指南。

## 如何贡献

### 报告 Bug

如果您发现了 bug，请通过 GitHub Issues 报告：

1. 检查是否已有类似的 issue
2. 使用清晰的标题描述问题
3. 提供详细的步骤来复现问题
4. 包含相关的错误日志
5. 说明您的环境（Python 版本、操作系统等）

### 功能请求

如果您有新功能的想法：

1. 检查是否已有类似的请求
2. 详细描述您想要的功能
3. 解释为什么这个功能很有用
4. 如果可能，提供实现的建议

### 代码贡献

#### 开发环境设置

1. Fork 本仓库
2. 克隆您的 fork
```bash
git clone https://github.com/your-username/reddit-newsletter-bot.git
cd reddit-newsletter-bot
```

3. 创建虚拟环境
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS
```

4. 安装依赖
```bash
pip install -r requirements.txt
```

5. 配置环境变量（复制 `.env.example` 到 `.env` 并填入配置）

#### 开发流程

1. 创建新分支
```bash
git checkout -b feature/your-feature-name
```

2. 进行开发
3. 运行测试
```bash
python tools/manage.py test-all
python tests/run_tests.py
```

4. 提交更改
```bash
git add .
git commit -m "描述您的更改"
```

5. 推送并创建 Pull Request

#### 代码规范

- 使用 Python 类型提示
- 遵循 PEP 8 代码风格
- 添加中文注释和文档字符串
- 编写测试用例覆盖新功能
- 更新相关文档

#### Pull Request 指南

1. 确保所有测试通过
2. 更新相关文档
3. 在 PR 描述中说明更改内容
4. 保持提交历史整洁
5. 遵循项目的代码风格

## 项目结构

```
reddit-newsletter-bot/
├── src/                    # 核心源代码
├── tests/                  # 测试文件
├── tools/                  # 管理工具
├── templates/              # 邮件模板
├── data/                   # 数据文件
└── .github/                # GitHub 配置
```

## 开发工具

- `tools/manage.py` - 主要管理脚本
- `tools/preview_server.py` - 邮件模板预览
- `tests/run_tests.py` - 测试运行器

## 问题和建议

如果您有任何问题或建议，欢迎：

1. 创建 GitHub Issue
2. 发起讨论
3. 联系维护者

再次感谢您的贡献！
