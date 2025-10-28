"""Command protection decorators"""
import functools
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def private_chat_only(func):
    """Decorator to restrict command to private chats only"""
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.type != "private":
            await update.message.reply_text(
                "⚠️ This command can only be used in private chat.\n"
                "Please message me directly."
            )
            return
        return await func(self, update, context)
    return wrapper


def private_chat_only_callback(func):
    """Decorator to restrict callback queries to private chats only"""
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.type != "private":
            await update.callback_query.answer(
                "⚠️ This can only be used in private chat.",
                show_alert=True
            )
            return
        return await func(self, update, context)
    return wrapper


def admin_only(func):
    """Decorator to restrict command to admin group only"""
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        from app.config import Config
        
        chat_id = str(update.effective_chat.id)
        if chat_id != Config.ADMIN_GROUP_ID:
            logger.warning(f"Unauthorized admin command attempt from chat {chat_id}")
            return
        
        return await func(self, update, context)
    return wrapper


def admin_group_only_callback(func):
    """Decorator to restrict callback queries to admin group only"""
    @functools.wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        from app.config import Config
        
        chat_id = str(update.effective_chat.id)
        if chat_id != Config.ADMIN_GROUP_ID:
            logger.warning(f"Unauthorized admin callback attempt from chat {chat_id}")
            await update.callback_query.answer(
                "⚠️ This action is restricted to admin group.",
                show_alert=True
            )
            return
        
        return await func(self, update, context)
    return wrapper
