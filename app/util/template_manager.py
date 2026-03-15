"""
模板管理器 - 实现模板热切换功能
"""
import os
import logging
from flask import current_app
from app.model.cms import Theme
from app.ext import db

logger = logging.getLogger(__name__)

class TemplateManager:
    """模板管理器类"""
    
    @staticmethod
    def get_active_theme():
        """获取当前激活的主题"""
        try:
            active_theme = Theme.query.filter_by(is_active=True, deleted=0).first()
            if active_theme:
                return active_theme.code
            else:
                # 如果没有激活的主题，返回默认主题
                return current_app.config.get('H3BLOG_TEMPLATE', 'tend')
        except Exception as e:
            logger.error(f"获取激活主题失败: {e}")
            return current_app.config.get('H3BLOG_TEMPLATE', 'tend')
    
    @staticmethod
    def activate_theme(theme_code):
        """激活指定主题"""
        try:
            # 检查主题是否存在
            theme = Theme.query.filter_by(code=theme_code, deleted=0).first()
            if not theme:
                return False, "主题不存在"
            
            # 检查主题目录是否存在
            theme_path = os.path.join(current_app.root_path, 'main', 'themes', theme_code)
            if not os.path.exists(theme_path):
                return False, "主题目录不存在"
            
            # 检查主题是否包含必要的模板文件
            # 检查index.html文件
            index_path = os.path.join(theme_path, 'index.html')
            if not os.path.exists(index_path):
                return False, "主题缺少必要的模板文件: index.html"
            
            # 检查base.html文件（可能在common目录中）
            # base_path = os.path.join(theme_path, 'common', 'base.html')
            # base_path2 = os.path.join(theme_path, 'base.html')
            # if not os.path.exists(base_path) and not os.path.exists(base_path2):
            #     return False, "主题缺少必要的模板文件: base.html"
            
            try:
                # 取消所有主题的激活状态
                Theme.query.filter_by(deleted=0).update({'is_active': False})
                
                # 激活指定主题
                theme.is_active = True
                
                # 更新应用配置
                current_app.config['H3BLOG_TEMPLATE'] = theme_code
                
                # 更新蓝图静态文件夹路径
                from app.main import main as main_blueprint
                # 重新设置静态文件夹路径
                main_blueprint.static_folder = os.path.join('themes', theme_code, 'static')
                
                # 更新模板文件夹路径
                main_blueprint.template_folder = os.path.join('themes', theme_code)
                
                db.session.commit()
                
                logger.info(f"主题切换成功: {theme_code}")
                return True, "主题激活成功"
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"主题激活失败: {e}")
                return False, f"主题激活失败: {str(e)}"
                
        except Exception as e:
            logger.error(f"主题激活异常: {e}")
            return False, f"主题激活异常: {str(e)}"
    
    @staticmethod
    def scan_themes():
        """扫描主题目录，自动添加新主题和恢复已删除的主题"""
        try:
            themes_dir = os.path.join(current_app.root_path, 'main', 'themes')
            if not os.path.exists(themes_dir):
                return 0, "主题目录不存在"
            
            # 获取所有主题（包括已删除的）
            all_themes = {theme.code: theme for theme in Theme.query.all()}
            
            # 扫描主题目录
            added_count = 0
            restored_count = 0
            
            for item in os.listdir(themes_dir):
                item_path = os.path.join(themes_dir, item)
                if not os.path.isdir(item_path):
                    continue
                    
                if item in all_themes:
                    # 主题已存在，检查是否被删除
                    theme = all_themes[item]
                    if theme.deleted == 1:
                        # 恢复已删除的主题
                        theme.deleted = 0
                        theme.name = item.capitalize()
                        theme.description = f"{item.capitalize()} 主题"
                        theme.author = "系统"
                        theme.version = "1.0.0"
                        theme.is_active = 0
                        theme.sn = 0
                        restored_count += 1
                        logger.info(f"恢复主题: {item}")
                else:
                    # 创建新主题记录
                    theme = Theme(
                        name=item.capitalize(),
                        code=item,
                        description=f"{item.capitalize()} 主题",
                        author="系统",
                        version="1.0.0",
                        is_active=0,
                        sn=0
                    )
                    db.session.add(theme)
                    added_count += 1
                    logger.info(f"新增主题: {item}")
            
            if added_count > 0 or restored_count > 0:
                db.session.commit()
                logger.info(f"扫描完成，新增 {added_count} 个主题，恢复 {restored_count} 个主题")
            
            total_count = added_count + restored_count
            message = f"扫描完成"
            if total_count > 0:
                message += f"，发现 {total_count} 个主题"
                if added_count > 0:
                    message += f"（新增 {added_count} 个"
                if restored_count > 0:
                    if added_count > 0:
                        message += f"，恢复 {restored_count} 个）"
                    else:
                        message += f"（恢复 {restored_count} 个）"
            else:
                message += "，未发现新主题"
            
            return total_count, message
            
        except Exception as e:
            logger.error(f"主题扫描失败: {e}")
            return 0, f"主题扫描失败: {str(e)}"
    
    @staticmethod
    def get_theme_info(theme_code):
        """获取主题信息"""
        try:
            theme_path = os.path.join(current_app.root_path, 'main', 'themes', theme_code)
            if not os.path.exists(theme_path):
                return None
            
            # 检查主题配置文件
            config_file = os.path.join(theme_path, 'theme.json')
            theme_info = {
                'code': theme_code,
                'name': theme_code.capitalize(),
                'description': f"{theme_code.capitalize()} 主题",
                'author': '未知',
                'version': '1.0.0',
                'preview_img': None
            }
            
            if os.path.exists(config_file):
                import json
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        theme_info.update(config)
                except Exception as e:
                    logger.warning(f"读取主题配置文件失败: {e}")
            
            # 检查预览图片
            preview_files = ['preview.jpg', 'preview.png', 'screenshot.jpg', 'screenshot.png']
            for preview_file in preview_files:
                preview_path = os.path.join(theme_path, preview_file)
                if os.path.exists(preview_path):
                    theme_info['preview_img'] = f'/cstatics/{preview_file}'
                    break
            
            return theme_info
            
        except Exception as e:
            logger.error(f"获取主题信息失败: {e}")
            return None
    
    @staticmethod
    def build_template_path(tpl: str) -> str:
        """构建模板路径"""
        try:
            active_theme = TemplateManager.get_active_theme()
            return f'{active_theme}/{tpl}'
        except Exception as e:
            logger.error(f"构建模板路径失败: {e}")
            return f'tend/{tpl}'  # 默认返回tend主题

# 创建全局模板管理器实例
template_manager = TemplateManager()