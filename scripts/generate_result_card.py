"""SBTI 结果卡片生成：基于 ljg-card 信息图风格，输出 PNG"""
import json, sys, os

SKILL_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_BASE, 'scripts'))

# capture.js 本地路径
CAPTURE_JS = os.path.join(SKILL_BASE, 'scripts', 'capture.js')


def generate_card_html(result: dict, name: str = 'sbti_result', username: str = '') -> str:
    """生成 SBTI 结果信息图 HTML，返回文件路径

    Args:
        result: SBTI 计算结果 dict
        name: 卡片文件名前缀
        username: 测试者用户名（显示在左下角），空则不显示
    """
    code = result['type_code']
    cn = result['type_cn']
    intro = result.get('type_intro', '')
    badge = result.get('badge', '')
    desc = result.get('type_desc', '')
    is_special = result.get('is_special', False)
    best_normal = result.get('best_normal', {})
    similarity = best_normal.get('similarity', 0)
    dimensions = result.get('dimensions', [])[:5]  # 只取前5个最有特色的维度

    # 图片路径（SBTI skill 的 image 目录）
    type_image = os.path.join(SKILL_BASE, 'image', f'{code}.png').replace('\\', '/')
    type_image_url = f'file:///{type_image}'

    # 维度高亮 HTML
    dim_items = ''
    for d in dimensions:
        level_label = {'L': '低', 'M': '中', 'H': '高'}.get(d.get('level', 'M'), '中')
        dim_items += f'''
        <div class="dim-item">
            <span class="dim-name">{d.get('name', d.get('dim', ''))}</span>
            <span class="dim-level">{d.get('level', 'M')} <em>({level_label})</em></span>
            <span class="dim-score">{d.get('score', 0)}分</span>
        </div>'''

    # 从 desc 提取第一句作为展示
    first_sentence = desc.split('。')[0] + '。' if desc else ''

    # 底色：纯白；强调色随类型变化
    bg = '#FFFFFF'  # 纯白底
    if is_special or code in ('HHHH', 'DRUNK', 'FUCK', 'SHIT'):
        green, pink = '#C8B898', '#C17F4E'  # 温暖色调
    elif code in ('SEXY', 'LOVE-R', 'MUM'):
        green, pink = '#C0A89C', '#B8432F'  # 情感色调
    elif code in ('CTRL', 'BOSS', 'THAN-K'):
        green, pink = '#B8D8BE', '#4D6A53'  # 清新绿
    else:
        green, pink = '#B8D8BE', '#E91E63'  # 默认

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
:root {{
  --bg: {bg};
  --green: {green};
  --pink: {pink};
  --ink: #2D2926;
  --ink-light: #5C5350;
  --white: #FFFFFF;
  --serif: 'KingHwa_OldSong', 'PingFang SC', system-ui, sans-serif;
  --sans: 'DM Sans', 'PingFang SC', system-ui, sans-serif;
  --mono: 'SF Mono', monospace;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1080px; background: var(--bg); font-family: var(--sans); }}
.card {{ width: 1080px; background: var(--bg); padding: 56px 64px 48px; position: relative; overflow: hidden; }}
/* 噪点纹理 */
.card::before {{ content: ''; position: absolute; inset: 0; background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E"); pointer-events: none; z-index: 0; }}
/* 顶部横条 */
.top-bar {{ height: 4px; background: var(--green); margin-bottom: 48px; position: relative; z-index: 1; }}
/* 主内容区 */
.main {{ display: grid; grid-template-columns: 340px 1fr; gap: 48px; align-items: start; position: relative; z-index: 1; }}
/* 左：人格图片 */
.portrait {{ position: relative; }}
.portrait img {{ width: 340px; height: 340px; object-fit: contain; border-radius: 16px; background: rgba(255,255,255,0.7); display: block; }}
/* 右：文字区 */
.info {{ display: flex; flex-direction: column; gap: 0; }}
/* 标签 */
.kicker {{ font-size: 22px; color: var(--ink-light); letter-spacing: 0.08em; margin-bottom: 12px; font-family: var(--sans); }}
/* 类型名 */
.type-name {{ font-family: var(--serif); font-size: 96px; font-weight: 700; color: var(--ink); letter-spacing: -0.03em; line-height: 1.0; margin-bottom: 8px; }}
.type-cn {{ font-family: var(--serif); font-size: 36px; color: var(--ink-light); letter-spacing: 0.02em; margin-bottom: 20px; }}
/* badge */
.badge {{ display: inline-flex; align-items: center; gap: 8px; background: var(--green); color: var(--ink); padding: 8px 18px; border-radius: 999px; font-size: 22px; font-weight: 600; width: fit-content; margin-bottom: 20px; }}
/* 引言 */
.intro {{ font-family: var(--serif); font-size: 32px; color: var(--ink); line-height: 1.5; border-left: 3px solid var(--pink); padding-left: 18px; margin-bottom: 24px; }}
/* 描述 */
.desc {{ font-size: 26px; color: var(--ink-light); line-height: 1.75; }}
/* 维度区 */
.dims {{ margin-top: 36px; position: relative; z-index: 1; }}
.dims-title {{ font-size: 24px; color: var(--ink-light); margin-bottom: 16px; letter-spacing: 0.05em; }}
.dim-list {{ display: flex; flex-direction: column; gap: 10px; }}
.dim-item {{ display: grid; grid-template-columns: 1fr auto auto; gap: 12px; align-items: center; padding: 12px 16px; background: rgba(255,255,255,0.85); border-radius: 10px; border: 1px solid rgba(0,0,0,0.06); }}
.dim-name {{ font-size: 24px; color: var(--ink); font-weight: 500; }}
.dim-level {{ font-size: 22px; color: var(--ink-light); font-family: var(--mono); }}
.dim-level em {{ font-style: normal; color: var(--green); }}
.dim-score {{ font-size: 22px; color: var(--ink-light); font-family: var(--mono); }}
/* footer */
.footer {{ margin-top: 32px; display: flex; justify-content: space-between; align-items: center; position: relative; z-index: 1; }}
.footer-left {{ display: flex; align-items: center; gap: 12px; }}
.logo {{ width: 36px; height: 36px; object-fit: contain; border-radius: 4px; }}
.brand {{ font-size: 22px; color: var(--ink-light); }}
.footer-right {{ font-size: 20px; color: var(--ink-light); }}
</style>
</head>
<body>
<div class="card">
  <div class="top-bar"></div>
  <div class="main">
    <div class="portrait">
      <img src="{type_image_url}" alt="{code}人格图" />
    </div>
    <div class="info">
      <div class="kicker">SBTI · {result.get('mode_kicker', '你的主类型')}</div>
      <div class="type-name">{code}</div>
      <div class="type-cn">{cn}</div>
      <div class="badge">{'★' if is_special else '●'} {badge}</div>
      <div class="intro">{intro}</div>
      <div class="desc">{first_sentence}</div>
    </div>
  </div>
  <div class="dims">
    <div class="dims-title">十五维度（节选）</div>
    <div class="dim-list">{dim_items}</div>
  </div>
  <div class="footer">
    <div class="footer-left">
      <span class="brand">{username or ''}</span>
    </div>
    <div class="footer-right">由 sbti-skill 生成</div>
  </div>
</div>
</body>
</html>'''

    output_path = os.path.join('/tmp', f'sbti_card_{name}.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return output_path


def capture_card(html_path: str, name: str = 'sbti_result') -> str:
    """调用 ljg-card capture.js 截图，返回 PNG 路径"""
    output_png = os.path.expanduser(f'~/Downloads/{name}.png')
    # 确保 capture.js 存在
    if not os.path.exists(CAPTURE_JS):
        raise FileNotFoundError(f"capture.js not found at {CAPTURE_JS}")
    import subprocess
    cmd = [
        'node', CAPTURE_JS, html_path, output_png, '1080', '900', 'fullpage'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"capture failed: {result.stderr}")
    return output_png


if __name__ == '__main__':
    # CLI: 读取 stdin JSON result，生成并截图卡片
    import sys as _sys
    _sys.stdin.reconfigure(encoding='utf-8')
    result = json.load(_sys.stdin)
    name = result.get('type_code', 'result')
    username = result.get('username', '')
    html_path = generate_card_html(result, name, username)
    png_path = capture_card(html_path, name)
    print(json.dumps({'html': html_path, 'png': png_path}, ensure_ascii=False))
