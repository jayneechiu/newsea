"""
Flask Preview Server - 用于实时预览 Newsletter 模板
"""

from flask import Flask, render_template, request
from datetime import datetime
import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

app = Flask(__name__, template_folder=os.path.join(project_root, 'templates'))

# 配置 Flask 开发模式
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# 禁用模板缓存以实现实时更新
app.jinja_env.auto_reload = True
app.jinja_env.cache = {}

def get_sample_posts():
    """生成示例帖子数据"""
    sample_posts = [
        {
            'id': 'sample1',
            'title': '🚀 Python 3.12 性能提升 20%！新特性全面解析',
            'author': 'python_guru',
            'subreddit': 'Python',
            'score': 3456,
            'num_comments': 234,
            'selftext': '''
Python 3.12 正式发布了！这个版本带来了令人兴奋的性能改进和新特性：

1. **性能提升**：整体性能提升 20%，特别是在循环和函数调用方面
2. **改进的错误消息**：更清晰、更有帮助的错误提示
3. **新的语法特性**：支持更灵活的类型注解
4. **内存优化**：减少了内存占用，提高了垃圾回收效率

这些改进让 Python 在性能和开发体验上都有了显著提升。
            '''.strip(),
            'permalink': 'https://reddit.com/r/Python/comments/sample1',
            'url': 'https://reddit.com/r/Python/comments/sample1',
            'is_video': False,
            'created_utc': datetime.now().timestamp()
        },
        {
            'id': 'sample2',
            'title': '🎥 【视频教程】Docker 容器化最佳实践 - 10分钟入门指南',
            'author': 'docker_master',
            'subreddit': 'docker',
            'score': 2187,
            'num_comments': 89,
            'selftext': None,  # 视频帖子通常没有文本内容
            'permalink': 'https://reddit.com/r/docker/comments/sample2',
            'url': 'https://youtube.com/watch?v=docker-tutorial-123',
            'is_video': True,
            'created_utc': datetime.now().timestamp()
        },
        {
            'id': 'sample3',
            'title': '🔥 GitHub 开源项目推荐：超强的代码分析工具',
            'author': 'opensource_hunter',
            'subreddit': 'opensource',
            'score': 1654,
            'num_comments': 145,
            'selftext': '发现了一个非常棒的开源代码分析工具，支持多种编程语言，可以自动检测代码质量问题、安全漏洞和性能优化建议。项目文档详细，社区活跃，强烈推荐！',
            'permalink': 'https://reddit.com/r/opensource/comments/sample3',
            'url': 'https://github.com/awesome-tool/code-analyzer',
            'is_video': False,
            'created_utc': datetime.now().timestamp()
        },
        {
            'id': 'sample4',
            'title': '💡 机器学习新突破：GPT-5 架构设计细节曝光',
            'author': 'ai_researcher',
            'subreddit': 'MachineLearning',
            'score': 4521,
            'num_comments': 378,
            'selftext': '''
最新的研究论文披露了 GPT-5 的一些架构细节：

• **规模**：参数量预计达到 1.8 万亿
• **训练数据**：使用了更高质量的多模态数据集
• **架构改进**：采用了新的注意力机制，减少了计算复杂度
• **能力增强**：在推理、编程和创作方面有显著提升

这些改进可能会带来 AI 领域的下一次重大突破。
            '''.strip(),
            'permalink': 'https://reddit.com/r/MachineLearning/comments/sample4',
            'url': 'https://reddit.com/r/MachineLearning/comments/sample4',
            'is_video': False,
            'created_utc': datetime.now().timestamp()
        },
        {
            'id': 'sample5',
            'title': '🛠️ Web 开发神器：一行代码实现响应式布局',
            'author': 'frontend_ninja',
            'subreddit': 'webdev',
            'score': 2890,
            'num_comments': 156,
            'selftext': '',  # 空内容测试
            'permalink': 'https://reddit.com/r/webdev/comments/sample5',
            'url': 'https://codepen.io/awesome-css-trick',
            'is_video': False,
            'created_utc': datetime.now().timestamp()
        }
    ]
    
    return sample_posts

@app.route('/')
def index():
    """主页 - 显示可用的预览选项"""
    return '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Newsletter 模板预览服务器</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #ff4500; text-align: center; }
            .option {
                background: #f8f9fa;
                padding: 20px;
                margin: 15px 0;
                border-radius: 8px;
                border-left: 4px solid #ff4500;
            }
            .option h3 { margin-top: 0; color: #333; }
            .option a {
                background: #ff4500;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                margin-top: 10px;
            }
            .option a:hover { background: #e03d00; }
            .info {
                background: #e3f2fd;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid #2196f3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📧 Newsletter 模板预览服务器</h1>
            
            <div class="info">
                <strong>📋 使用说明：</strong><br>
                • 修改 <code>templates/newsletter_template.html</code> 后刷新页面即可看到效果<br>
                • 服务器运行在开发模式，模板会自动重新加载<br>
                • 可以使用不同的测试数据来预览不同情况
            </div>
            
            <div class="option">
                <h3>🔄 实时预览 (推荐)</h3>
                <p>使用示例数据预览完整的 Newsletter 效果，支持实时更新</p>
                <a href="/preview">查看预览</a>
            </div>
            
            <div class="option">
                <h3>📊 少量数据测试</h3>
                <p>使用少量帖子数据测试布局效果</p>
                <a href="/preview?posts=2">2个帖子</a>
                <a href="/preview?posts=1">1个帖子</a>
            </div>
            
            <div class="option">
                <h3>🎯 特殊情况测试</h3>
                <p>测试各种边界情况和特殊内容</p>
                <a href="/preview/video-only">仅视频帖子</a>
                <a href="/preview/no-content">无内容帖子</a>
                <a href="/preview/long-title">长标题测试</a>
            </div>
            
            <div class="option">
                <h3>🔍 模板检查</h3>
                <p>检查模板语法和变量使用情况</p>
                <a href="/template-info">模板信息</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/preview')
def preview_newsletter():
    """预览 Newsletter"""
    # 获取帖子数量参数
    post_count = request.args.get('posts', type=int)
    
    posts = get_sample_posts()
    
    if post_count:
        posts = posts[:post_count]
    
    return render_template('newsletter_template.html',
                         date=datetime.now().strftime('%Y年%m月%d日'),
                         total_posts=len(posts),
                         posts=posts)

@app.route('/preview/video-only')
def preview_video_only():
    """仅视频帖子预览"""
    posts = [post for post in get_sample_posts() if post.get('is_video')]
    
    return render_template('newsletter_template.html',
                         date=datetime.now().strftime('%Y年%m月%d日'),
                         total_posts=len(posts),
                         posts=posts)

@app.route('/preview/no-content')
def preview_no_content():
    """无内容帖子预览"""
    posts = get_sample_posts()
    # 移除所有 selftext 内容
    for post in posts:
        post['selftext'] = None
    
    return render_template('newsletter_template.html',
                         date=datetime.now().strftime('%Y年%m月%d日'),
                         total_posts=len(posts),
                         posts=posts)

@app.route('/preview/long-title')
def preview_long_title():
    """长标题测试"""
    posts = [
        {
            'id': 'long1',
            'title': '🚀 这是一个非常非常非常长的标题用来测试当标题过长时的显示效果和换行情况以及整体布局是否会受到影响或者变形',
            'author': 'very_long_username_test_user_12345',
            'subreddit': 'VeryLongSubredditNameForTesting',
            'score': 99999,
            'num_comments': 8888,
            'selftext': '这是一段很长的文本内容，用来测试当帖子内容非常长时的显示效果。' * 10,
            'permalink': 'https://reddit.com/r/test/comments/long1',
            'url': 'https://reddit.com/r/test/comments/long1',
            'is_video': False,
            'created_utc': datetime.now().timestamp()
        }
    ]
    
    return render_template('newsletter_template.html',
                         date=datetime.now().strftime('%Y年%m月%d日'),
                         total_posts=len(posts),
                         posts=posts)

@app.route('/template-info')
def template_info():
    """模板信息和语法检查"""
    template_path = os.path.join('templates', 'newsletter_template.html')
    
    info = {
        'file_exists': os.path.exists(template_path),
        'file_size': 0,
        'last_modified': None
    }
    
    if info['file_exists']:
        stat = os.stat(template_path)
        info['file_size'] = stat.st_size
        info['last_modified'] = datetime.fromtimestamp(stat.st_mtime)
    
    return f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>模板信息</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 20px auto; 
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .back-link {{
                background: #ff4500;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">返回主页</a>
            <h1>模板信息</h1>
            <p><strong>文件存在：</strong> {'是' if info['file_exists'] else '否'}</p>
            {f'<p><strong>文件大小：</strong> {info["file_size"]} 字节</p>' if info['file_exists'] else ''}
            {f'<p><strong>最后修改：</strong> {info["last_modified"]}</p>' if info.get('last_modified') else ''}
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🚀 启动 Newsletter 模板预览服务器...")
    print("📍 服务器地址: http://localhost:5000")
    print("📝 实时预览: http://localhost:5000/preview")
    print("🔄 修改模板文件后刷新页面即可看到效果")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    # 启动 Flask 开发服务器
    app.run(
        debug=True,
        host='localhost', 
        port=5000,
        use_reloader=True,
        threaded=True
    )
