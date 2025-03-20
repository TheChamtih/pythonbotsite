from flask import current_app
import os
import logging
from models import SiteSettings, db
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

def save_site_icon(file):
    """Save uploaded site icon"""
    if file:
        filename = secure_filename(file.filename)
        icon_path = os.path.join(current_app.static_folder, 'uploads', filename)
        os.makedirs(os.path.dirname(icon_path), exist_ok=True)
        file.save(icon_path)
        return f'/static/uploads/{filename}'
    return None

def update_site_settings(form_data, icon_file=None):
    """Update site settings"""
    try:
        settings = SiteSettings.get_settings()
        logger.info("Обновление настроек сайта...")

        # Update basic settings
        settings.site_name = form_data.get('site_name', settings.site_name)
        settings.logo_icon_class = form_data.get('logo_icon_class', settings.logo_icon_class)
        if icon_file:
            icon_path = save_site_icon(icon_file)
            if icon_path:
                settings.site_icon = icon_path

        # Update theme settings
        settings.primary_color = form_data.get('primary_color', settings.primary_color)
        settings.accent_color = form_data.get('accent_color', settings.accent_color)
        settings.heading_font = form_data.get('heading_font', settings.heading_font)
        settings.body_font = form_data.get('body_font', settings.body_font)

        logger.info(f"Обновлены настройки темы: шрифт заголовков={settings.heading_font}, шрифт текста={settings.body_font}")

        # Update footer appearance
        settings.footer_icons_color = form_data.get('footer_icons_color', settings.footer_icons_color)
        settings.contact_icons_color = form_data.get('contact_icons_color', settings.contact_icons_color)
        settings.show_social_icons = form_data.get('show_social_icons') == 'true'

        # Update social media links
        settings.website_url = form_data.get('website_url')
        settings.facebook_url = form_data.get('facebook_url')
        settings.instagram_url = form_data.get('instagram_url')
        settings.telegram_url = form_data.get('telegram_url')
        settings.vk_url = form_data.get('vk_url')
        settings.whatsapp_url = form_data.get('whatsapp_url')

        # Update footer content
        settings.footer_about = form_data.get('footer_about')

        # Update contact information
        settings.contact_address = form_data.get('contact_address')
        settings.contact_email = form_data.get('contact_email')
        settings.contact_phone = form_data.get('contact_phone')
        settings.contact_hours = form_data.get('contact_hours')

        # Update SEO and analytics settings
        settings.meta_description = form_data.get('meta_description')
        settings.meta_keywords = form_data.get('meta_keywords')
        settings.meta_author = form_data.get('meta_author')
        settings.og_title = form_data.get('og_title')
        settings.og_description = form_data.get('og_description')
        settings.og_image = form_data.get('og_image')
        settings.google_analytics_id = form_data.get('google_analytics_id')
        settings.yandex_metrika_id = form_data.get('yandex_metrika_id')
        settings.robots_txt = form_data.get('robots_txt')

        # Update content
        settings.welcome_text = form_data.get('welcome_text')
        settings.terms_of_service = form_data.get('terms_of_service')
        settings.privacy_policy = form_data.get('privacy_policy')

        db.session.commit()
        logger.info("Настройки сайта успешно обновлены")
        return True, "Настройки успешно обновлены"
    except Exception as e:
        logger.error(f"Ошибка при обновлении настроек: {str(e)}")
        db.session.rollback()
        return False, f"Ошибка при обновлении настроек: {str(e)}"

def get_site_settings():
    """Get current site settings"""
    return SiteSettings.get_settings()