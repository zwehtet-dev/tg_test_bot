"""
Admin handlers for receipt verification and transaction management
"""
import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TimedOut, NetworkError

from app.config.settings import Config
from app.services.database_service import DatabaseService
from app.services.ocr_service import OCRService
from app.utils.command_protection import admin_only, admin_group_only_callback

logger = logging.getLogger(__name__)


class AdminHandlers:
    """Handle admin operations for transaction verification"""
    
    def __init__(self, db_service: DatabaseService, ocr_service: OCRService):
        """
        Initialize admin handlers
        
        Args:
            db_service: Database service instance
            ocr_service: OCR service instance
        """
        self.db = db_service
        self.ocr = ocr_service
        self.config = Config
        logger.info("Admin handlers initialized")
    
    @admin_only
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current balances (admin only)"""
        balances = self.db.get_balances()
        
        message = "💰 **Current Bank Balances:**\n\n"
        
        current_currency = None
        for currency, bank, balance, display_name in balances:
            if currency != current_currency:
                if current_currency is not None:
                    message += "\n"
                message += f"**{currency}:**\n"
                current_currency = currency
            # Use display_name if available, otherwise fall back to bank name
            display = display_name if display_name else 'No Display Name'
            message += f"• {display}: {balance:,.2f}\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    @admin_only
    async def rate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View or set exchange rate (admin only)"""
        if context.args:
            try:
                new_rate = float(context.args[0])
                self.db.update_rate(new_rate)
                await update.message.reply_text(
                    f"✅ **Exchange rate updated**\n\n"
                    f"New rate: 1 THB = {new_rate} MMK",
                    parse_mode='Markdown'
                )
            except ValueError:
                await update.message.reply_text("❌ Invalid rate value. Use: /rate 121.5")
        else:
            rate = self.db.get_current_rate()
            await update.message.reply_text(
                f"📊 **Current Exchange Rate**\n\n"
                f"1 THB = {rate} MMK\n\n"
                f"To update: `/rate <new_rate>`\n"
                f"Example: `/rate 122.0`",
                parse_mode='Markdown'
            )
    
    @admin_only
    async def transactions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show today's transactions (admin only)"""
        transactions = self.db.get_today_transactions()
        
        if not transactions:
            await update.message.reply_text("📊 No transactions today.")
            return
        
        message = "📊 **Today's Transactions:**\n\n"
        total_thb = 0
        total_mmk = 0
        confirmed_count = 0
        pending_count = 0
        
        for txn in transactions:
            status_emoji = "✅" if txn[13] == 'confirmed' else "⏳" if txn[13] == 'pending' else "❌"
            message += f"{status_emoji} **#{txn[0]}** - {txn[6]} THB → {txn[7]:,.0f} MMK - `{txn[13]}`\n"
            
            if txn[13] == 'confirmed':
                total_thb += txn[6]
                total_mmk += txn[7]
                confirmed_count += 1
            elif txn[13] == 'pending':
                pending_count += 1
        
        message += f"\n**Summary:**\n"
        message += f"Total Confirmed: {confirmed_count}\n"
        message += f"Pending: {pending_count}\n"
        message += f"Total Volume: {total_thb:,.0f} THB → {total_mmk:,.0f} MMK"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    @admin_only
    async def handle_admin_receipt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin receipt photo upload"""
        # Check if message has a photo
        if not update.message.photo:
            logger.debug("No photo in message, skipping")
            return
        
        # Check if this is a reply to a transaction message
        if not update.message.reply_to_message:
            logger.debug("No reply_to_message found, skipping")
            return
        
        # Extract transaction ID from the replied message (could be text or caption)
        replied_text = update.message.reply_to_message.text or update.message.reply_to_message.caption
        logger.info(f"Admin receipt handler triggered. Replied text: {replied_text[:100] if replied_text else 'None'}")
        
        if not replied_text or ("Transaction ID:" not in replied_text and "Buy" not in replied_text):
            logger.debug("Message doesn't contain transaction markers, skipping")
            return
        
        # Try to extract transaction ID from message
        transaction_id = None
        
        # Method 1: Try to extract from inline keyboard (Cancel button)
        if hasattr(update.message.reply_to_message, 'reply_markup') and update.message.reply_to_message.reply_markup:
            # Extract from cancel button callback data
            for row in update.message.reply_to_message.reply_markup.inline_keyboard:
                for button in row:
                    if button.callback_data and button.callback_data.startswith('cancel_'):
                        transaction_id = int(button.callback_data.split('_')[1])
                        break
        
        # Method 2: If not found in keyboard, try to extract from message text
        # Look for pattern like "Transaction ID: #123" or just find the user ID and timestamp
        if not transaction_id and replied_text:
            # Try to find user ID in the message (format: "ID: 123456")
            import re
            user_id_match = re.search(r'ID:\s*(\d+)', replied_text)
            if user_id_match:
                user_id = int(user_id_match.group(1))
                # Get the most recent pending transaction for this user
                recent_txn = self.db.get_user_recent_pending_transaction(user_id)
                if recent_txn:
                    transaction_id = recent_txn[0]  # transaction ID is first column
                    logger.info(f"Found transaction #{transaction_id} for user {user_id} from message text")
        
        if not transaction_id:
            await update.message.reply_text("❌ Could not identify transaction. Please reply to the transaction message.")
            return
        
        # Get transaction to verify it exists and is pending
        transaction = self.db.get_transaction(transaction_id)
        if not transaction:
            await update.message.reply_text("❌ Transaction not found.")
            return
        
        # Check if transaction is already confirmed (not just pending)
        status = transaction.status
        if status == 'confirmed':
            await update.message.reply_text(f"❌ Transaction #{transaction_id} is already confirmed.")
            return
        elif status == 'cancelled':
            await update.message.reply_text(f"❌ Transaction #{transaction_id} has been cancelled.")
            return
        
        # Download admin receipt photo with retry logic for network timeouts
        photo = update.message.photo[-1]
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                file = await context.bot.get_file(photo.file_id)
                admin_receipt_path = f"{self.config.ADMIN_RECEIPTS_DIR}/admin_{transaction_id}_{datetime.now().timestamp()}.jpg"
                await file.download_to_drive(admin_receipt_path)
                break
            except (TimedOut, NetworkError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Network timeout on attempt {attempt + 1}, retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to download admin receipt after {max_retries} attempts: {e}")
                    await update.message.reply_text(
                        f"❌ **Network Error**\n\n"
                        f"Unable to download receipt for transaction #{transaction_id} due to network issues.\n\n"
                        f"Please try uploading again in a moment."
                    )
                    return
        
        # Save admin receipt path to database
        self.db.update_transaction_admin_receipt(transaction_id, admin_receipt_path)
        
        logger.info(f"Admin receipt saved for transaction #{transaction_id}: {admin_receipt_path}")
        
        # Verify receipt amount using OCR (only for MMK)
        to_currency = transaction.to_currency
        expected_amount = transaction.received_amount
        
        logger.info(f"Starting receipt verification for transaction #{transaction_id}, currency: {to_currency}, expected: {expected_amount}")
        
        # Flag to track if verification passed
        verification_passed = True
        detected_amount = None
        
        if to_currency == 'MMK':
            try:
                logger.info(f"🔍 Running OCR on admin receipt for transaction #{transaction_id}")
                receipt_info = self.ocr.extract_receipt_info(admin_receipt_path)
                logger.info(f"OCR result for transaction #{transaction_id}: {receipt_info}")
                
                if receipt_info.get('amount'):
                    detected_amount = float(receipt_info['amount'])
                    logger.info(f"💰 Amount detected: {detected_amount} MMK (expected: {expected_amount} MMK)")
                    
                    # Allow 1000 MMK tolerance for OCR errors and rounding
                    tolerance = 1000
                    amount_diff = abs(detected_amount - expected_amount)
                    
                    if amount_diff > tolerance:
                        # Amount mismatch - block proceeding
                        verification_passed = False
                        logger.warning(f"⚠️ AMOUNT MISMATCH in transaction #{transaction_id}: expected {expected_amount}, detected {detected_amount}, diff {amount_diff}")
                        
                        # Show warning with skip button
                        skip_keyboard = [[InlineKeyboardButton(
                            "⚠️ Skip Verification & Continue",
                            callback_data=f"skip_verify_{transaction_id}"
                        )]]
                        skip_markup = InlineKeyboardMarkup(skip_keyboard)
                        
                        await update.message.reply_text(
                            f"⚠️ **Amount Mismatch Detected**\n\n"
                            f"Transaction #{transaction_id}\n"
                            f"Expected: **{expected_amount:,.0f} MMK**\n"
                            f"Detected: **{detected_amount:,.0f} MMK**\n"
                            f"Difference: **{amount_diff:,.0f} MMK**\n\n"
                            f"❌ **Cannot proceed with bank selection**\n\n"
                            f"**Options:**\n"
                            f"1. Upload the correct receipt (reply to this transaction again)\n"
                            f"2. Click 'Skip Verification' below to proceed anyway",
                            reply_markup=skip_markup,
                            parse_mode='Markdown'
                        )
                        return  # Stop here, don't show bank selection
                    else:
                        # Amount within tolerance - update transaction with actual amount if different
                        if amount_diff > 0:
                            logger.info(f"✅ Amount verified for transaction #{transaction_id}: {detected_amount} MMK (diff: {amount_diff} MMK, within {tolerance} MMK tolerance)")
                            logger.info(f"📝 Updating transaction #{transaction_id} received_amount from {expected_amount} to {detected_amount} MMK")
                            
                            # Update transaction with actual amount sent by admin
                            self.db.update_transaction_received_amount(transaction_id, detected_amount)
                            
                            # Reload transaction to get updated amount
                            transaction = self.db.get_transaction(transaction_id)
                        else:
                            logger.info(f"✅ Amount verified for transaction #{transaction_id}: {detected_amount} MMK (exact match)")
                
                    # Verify account name if detected (check multiple possible field names)
                    detected_account_name = receipt_info.get('receiver_name') or receipt_info.get('receiver_account_name')
                    if detected_account_name:
                        expected_account_name = transaction.user_account_name
                        
                        logger.info(f"👤 Checking account name: detected '{detected_account_name}' vs expected '{expected_account_name}'")
                        
                        # Use the database validation method for fuzzy matching
                        similarity = self.db._calculate_similarity(detected_account_name, expected_account_name)
                        
                        if similarity < 0.70:  # 70% similarity threshold
                            # Account name mismatch warning (non-blocking)
                            logger.warning(f"⚠️ ACCOUNT NAME MISMATCH in transaction #{transaction_id}: expected '{expected_account_name}', detected '{detected_account_name}', similarity {similarity:.2%}")
                            
                            await update.message.reply_text(
                                f"⚠️ **Account Name Warning**\n\n"
                                f"Transaction #{transaction_id}\n"
                                f"Expected: **{expected_account_name}**\n"
                                f"Detected: **{detected_account_name}**\n"
                                f"Similarity: {similarity:.0%}\n\n"
                                f"⚠️ Please verify you sent to the correct account!",
                                parse_mode='Markdown'
                            )
                        else:
                            logger.info(f"✅ Account name verified: '{detected_account_name}' matches '{expected_account_name}' ({similarity:.0%} similarity)")
                    else:
                        logger.warning(f"⚠️ Could not detect receiver account name in admin receipt #{transaction_id}")
                        
                else:
                    logger.warning(f"⚠️ Could not detect amount in admin receipt #{transaction_id}. OCR result: {receipt_info}")
                    # If OCR fails, allow to proceed (don't block)
                    
            except Exception as e:
                logger.error(f"❌ Error verifying admin receipt amount for transaction #{transaction_id}: {e}", exc_info=True)
                # If error, allow to proceed (don't block)
        else:
            logger.info(f"Skipping OCR verification for transaction #{transaction_id} (currency: {to_currency}, only MMK is verified)")
        
        # Only reach here if verification passed or was skipped
        # Get banks for the currency user will receive (to_currency)
        bank_accounts = self.db.get_bank_accounts(to_currency)
        
        if not bank_accounts:
            await update.message.reply_text(
                f"❌ No {to_currency} bank accounts configured. Please add {to_currency} banks using /addbank command."
            )
            return
        
        # Build dynamic keyboard from database
        keyboard = []
        for account in bank_accounts:
            keyboard.append([InlineKeyboardButton(
                f"{account.display}", 
                callback_data=f"bank_{account.bank_name}_{transaction_id}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Get transaction details for display
        from app.utils.currency_utils import format_amount
        
        sent_amount = transaction.sent_amount
        received_amount = transaction.received_amount
        user_bank = transaction.user_bank_name
        
        # Format amounts based on currency
        sent_text = format_amount(sent_amount, transaction.from_currency)
        received_text = format_amount(received_amount, transaction.to_currency)
        
        await update.message.reply_text(
            f"✅ **Receipt saved for Transaction #{transaction_id}**\n\n"
            f"💰 Amount: {sent_text} {transaction.from_currency} → {received_text} {transaction.to_currency}\n"
            f"🏦 User's Bank: {user_bank}\n\n"
            f"📤 **Select which {to_currency} bank you used for transfer:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    @admin_group_only_callback
    async def admin_bank_selection_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle bank selection for manual confirmation"""
        query = update.callback_query
        await query.answer()
        
        parts = query.data.split('_')
        bank = parts[1]
        transaction_id = int(parts[2])
        
        # Get transaction details
        transaction = self.db.get_transaction(transaction_id)
        
        if not transaction:
            await query.edit_message_text("❌ Transaction not found.")
            return
        
        # Get transaction details
        user_id = transaction.user_id
        sent_amount = transaction.sent_amount
        received_amount = transaction.received_amount
        admin_receiving_bank = transaction.admin_receiving_bank
        
        # Get balances before update
        balances_before = self.db.get_balances()
        to_currency = transaction.to_currency
        balance_before = next((b[2] for b in balances_before if b[0] == to_currency and b[1] == bank), 0)
        
        # Check for insufficient funds
        balance_after = balance_before - received_amount
        if balance_after < 0:
            # Insufficient funds - notify admin
            await query.edit_message_text(
                f"{query.message.text}\n\n"
                f"⚠️ **INSUFFICIENT FUNDS - Transaction #{transaction_id}**\n\n"
                f"❌ Cannot process transaction\n"
                f"{to_currency} Bank: {bank}\n"
                f"Current Balance: {balance_before:,.2f} {to_currency}\n"
                f"Required Amount: {received_amount:,.2f} {to_currency}\n"
                f"Shortage: {abs(balance_after):,.2f} {to_currency}\n\n"
                f"⚠️ Please top up the {bank} account before confirming this transaction."
            )
            
            # Send alert to admin group
            try:
                admin_group_id = self.db.get_setting('admin_group_id') or self.config.ADMIN_GROUP_ID
                admin_topic_id = self.db.get_setting('admin_topic_id')
                
                alert_message = f"""🚨 **INSUFFICIENT FUNDS ALERT**

Transaction #{transaction_id} cannot be processed

💰 **{to_currency} Account ({bank}):**
• Current Balance: {balance_before:,.2f} {to_currency}
• Required Amount: {received_amount:,.2f} {to_currency}
• Shortage: {abs(balance_after):,.2f} {to_currency}

⚠️ Please top up the account and try again.

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                
                if admin_topic_id:
                    await context.bot.send_message(
                        chat_id=admin_group_id,
                        text=alert_message,
                        message_thread_id=int(admin_topic_id),
                        parse_mode='Markdown'
                    )
                else:
                    await context.bot.send_message(
                        chat_id=admin_group_id,
                        text=alert_message,
                        parse_mode='Markdown'
                    )
            except Exception as e:
                logger.error(f"Error sending insufficient funds alert: {e}")
            
            return
        
        # Get balance for the currency being sent (already updated when receipt was submitted)
        from_currency = transaction.from_currency
        if admin_receiving_bank:
            from_current = next((b[2] for b in balances_before if b[0] == from_currency and b[1] == admin_receiving_bank), None)
            from_before = from_current - sent_amount if from_current is not None else None
            from_after = from_current
        else:
            from_before = None
            from_after = None
        
        # Update balance for currency being sent out
        self.db.update_balance(to_currency, bank, -received_amount)
        
        # Get balances after update
        balances_after = self.db.get_balances()
        to_after = next((b[2] for b in balances_after if b[0] == to_currency and b[1] == bank), 0)
        
        # Update transaction status
        self.db.update_transaction_status(transaction_id, 'confirmed')
        
        # Try to edit message, if fails (message not modified), just answer the callback
        try:
            await query.edit_message_text(
                f"✅ **Transaction #{transaction_id} Confirmed**\n\n"
                f"{to_currency} Bank: {bank}\n"
                f"Amount: {received_amount:,.2f} {to_currency}\n\n"
                f"Transaction completed successfully!"
            )
        except Exception as e:
            # If edit fails (e.g., message not modified), just answer callback
            logger.debug(f"Could not edit message: {e}")
            await query.answer("✅ Transaction confirmed!")
        
        # Send balance update to balance topic
        await self._send_balance_update(
            context, transaction_id, sent_amount, received_amount,
            admin_receiving_bank, bank, from_before, from_after, balance_before, to_after,
            from_currency, to_currency
        )
        
        # Notify user with admin receipt photo
        try:
            from app.utils.currency_utils import format_amount
            
            sent_text = format_amount(sent_amount, from_currency)
            received_text = format_amount(received_amount, to_currency)
            
            notification_text = (
                f"✅ **Payment Confirmed!**\n\n"
                f"Transaction ID: #{transaction_id}\n"
                f"Amount: {sent_text} {from_currency} → {received_text} {to_currency}\n\n"
                f"The money has been transferred to your account.\n"
                f"Thank you for using our service! 💚"
            )
            
            # Send with admin receipt photo if available
            if transaction.admin_receipt_path and os.path.exists(transaction.admin_receipt_path):
                with open(transaction.admin_receipt_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo,
                        caption=notification_text,
                        parse_mode='Markdown'
                    )
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=notification_text,
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"Error notifying user: {e}")
    
    async def _send_balance_update(self, context, transaction_id, from_amount, to_amount,
                                   from_bank, to_bank, from_before, from_after, to_before, to_after,
                                   from_currency='THB', to_currency='MMK'):
        """Send balance update to balance topic"""
        balance_message = f"""💰 **Balance Update - Transaction #{transaction_id}**

"""
        
        # Add from currency section if bank info is available
        if from_bank and from_before is not None and from_after is not None:
            balance_message += f"""📊 **{from_currency} Account ({from_bank}):**
• Before: {from_before:,.2f} {from_currency}
• Change: +{from_amount:,.2f} {from_currency}
• After: {from_after:,.2f} {from_currency}

"""
        elif from_bank:
            balance_message += f"""📊 **{from_currency} Account ({from_bank}):**
• Change: +{from_amount:,.2f} {from_currency} (already applied when receipt submitted)

"""
        
        balance_message += f"""📊 **{to_currency} Account ({to_bank}):**
• Before: {to_before:,.2f} {to_currency}
• Change: -{to_amount:,.2f} {to_currency}
• After: {to_after:,.2f} {to_currency}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        # Add balance overview
        balances = self.db.get_balances()
        if balances:
            balance_message += "💰 **Current Bank Balances:**\n"
            
            # Group by currency
            mmk_balances = [(bank, balance, display) for currency, bank, balance, display in balances if currency == 'MMK']
            thb_balances = [(bank, balance, display) for currency, bank, balance, display in balances if currency == 'THB']
            
            if mmk_balances:
                balance_message += "\n**MMK:**\n"
                for bank, balance, display in mmk_balances:
                    display_name = display if display else bank
                    balance_message += f"• {display_name}: {balance:,.2f}\n"
            
            if thb_balances:
                balance_message += "\n**THB:**\n"
                for bank, balance, display in thb_balances:
                    display_name = display if display else bank
                    balance_message += f"• {display_name}: {balance:,.2f}\n"
        
        try:
            # Get balance topic from database
            admin_group_id = self.db.get_setting('admin_group_id') or self.config.ADMIN_GROUP_ID
            balance_topic_id = self.db.get_setting('balance_topic_id')
            
            if balance_topic_id:
                await context.bot.send_message(
                    chat_id=admin_group_id,
                    text=balance_message,
                    message_thread_id=int(balance_topic_id),
                    parse_mode='Markdown'
                )
                logger.info(f"Balance update sent to topic {balance_topic_id}")
            else:
                # Send to main admin group if no balance topic configured
                logger.warning("Balance topic ID not configured, sending to main admin group")
                await context.bot.send_message(
                    chat_id=admin_group_id,
                    text=balance_message,
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"Error sending balance update: {e}")
    
    @admin_group_only_callback
    async def skip_verification_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle skip verification button - proceed despite amount mismatch"""
        query = update.callback_query
        await query.answer()
        
        transaction_id = int(query.data.split('_')[2])
        
        logger.warning(f"⚠️ Admin skipped verification for transaction #{transaction_id}")
        
        # Get transaction
        transaction = self.db.get_transaction(transaction_id)
        if not transaction:
            await query.edit_message_text("❌ Transaction not found.")
            return
        
        # Get banks for the currency user will receive
        to_currency = transaction.to_currency
        bank_accounts = self.db.get_bank_accounts(to_currency)
        
        if not bank_accounts:
            await query.edit_message_text(
                f"❌ No {to_currency} bank accounts configured."
            )
            return
        
        # Build bank selection keyboard
        keyboard = []
        for account in bank_accounts:
            keyboard.append([InlineKeyboardButton(
                f"{account.display}", 
                callback_data=f"bank_{account.bank_name}_{transaction_id}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Update message to show bank selection
        from app.utils.currency_utils import format_amount
        
        sent_amount = transaction.sent_amount
        received_amount = transaction.received_amount
        user_bank = transaction.user_bank_name
        
        sent_text = format_amount(sent_amount, transaction.from_currency)
        received_text = format_amount(received_amount, transaction.to_currency)
        
        await query.edit_message_text(
            f"⚠️ **Verification Skipped by Admin**\n\n"
            f"Transaction #{transaction_id}\n"
            f"💰 Amount: {sent_text} {transaction.from_currency} → {received_text} {transaction.to_currency}\n"
            f"🏦 User's Bank: {user_bank}\n\n"
            f"📤 **Select which {to_currency} bank you used for transfer:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    
    @admin_group_only_callback
    async def admin_cancel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle transaction cancellation"""
        query = update.callback_query
        await query.answer()
        
        transaction_id = int(query.data.split('_')[1])
        
        # Update transaction status
        self.db.update_transaction_status(transaction_id, 'cancelled')
        
        await query.edit_message_text(
            f"{query.message.text}\n\n"
            f"❌ Transaction #{transaction_id} cancelled."
        )
        
        # Notify user
        transaction = self.db.get_transaction(transaction_id)
        if transaction:
            user_id = transaction[1]
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"❌ Your transaction #{transaction_id} has been cancelled.\n"
                         f"Please contact support if you have questions."
                )
            except Exception as e:
                logger.error(f"Error notifying user: {e}")

    @admin_only
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View or update bot settings (admin only)"""
        if not context.args:
            # Show current settings
            admin_group_id = self.db.get_setting('admin_group_id') or self.config.ADMIN_GROUP_ID
            admin_topic_id = self.db.get_setting('admin_topic_id') or self.config.ADMIN_TOPIC_ID or "Not set"
            balance_topic_id = self.db.get_setting('balance_topic_id') or "Not set"
            
            message = f"""⚙️ **Bot Settings:**

📱 **Admin Group ID:** `{admin_group_id}`
💬 **Admin Topic ID:** `{admin_topic_id}`
💰 **Balance Topic ID:** `{balance_topic_id}`

**Update Settings:**
`/settings admin_group_id <value>`
`/settings admin_topic_id <value>`
`/settings balance_topic_id <value>`

**Example:**
`/settings balance_topic_id 12345`
"""
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            # Update setting
            if len(context.args) < 2:
                await update.message.reply_text("❌ Usage: /settings <key> <value>")
                return
            
            key = context.args[0]
            value = context.args[1]
            
            valid_keys = ['admin_group_id', 'admin_topic_id', 'balance_topic_id']
            if key not in valid_keys:
                await update.message.reply_text(f"❌ Invalid key. Valid keys: {', '.join(valid_keys)}")
                return
            
            self.db.set_setting(key, value)
            await update.message.reply_text(f"✅ Setting updated: {key} = {value}")
    
    @admin_only
    async def add_bank_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add admin bank account (admin only)"""
        if len(context.args) < 4:
            message = """🏦 **Add Admin Bank Account**

**Usage:**
`/addbank <currency> <bank_name> <account_number> <account_name> [display_name]`

**Example:**
`/addbank THB KrungthaiBank 1234567890 COMPANY_NAME TZH_(K_Bank)`
`/addbank MMK KBZ 0987654321 COMPANY_NAME`

**Note:** Display name is optional and will be shown in balance reports
**Supported Currencies:** THB, MMK
"""
            await update.message.reply_text(message, parse_mode='Markdown')
            return
        
        currency = context.args[0].upper()
        bank_name = context.args[1]
        account_number = context.args[2]
        
        # Find where account_name ends and display_name begins
        # Look for a parameter that looks like a display name (contains parentheses or underscores)
        remaining_args = context.args[3:]
        account_name_parts = []
        display_name = None
        
        for i, arg in enumerate(remaining_args):
            # If arg contains parentheses or looks like a code, treat it as display_name
            if '(' in arg or '_' in arg or (len(arg) <= 5 and arg.isupper()):
                display_name = ' '.join(remaining_args[i:])
                break
            account_name_parts.append(arg)
        
        account_name = ' '.join(account_name_parts) if account_name_parts else remaining_args[0]
        
        if currency not in ['THB', 'MMK']:
            await update.message.reply_text("❌ Currency must be THB or MMK")
            return
        
        self.db.add_admin_bank_account(currency, bank_name, account_number, account_name, display_name)
        
        response = f"✅ **Admin Bank Account Added**\n\n"
        response += f"Currency: {currency}\n"
        response += f"Bank: {bank_name}\n"
        response += f"Account: {account_number}\n"
        response += f"Name: {account_name}\n"
        if display_name:
            response += f"Display Name: {display_name}\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    @admin_only
    async def list_banks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List admin bank accounts (admin only)"""
        currency_filter = context.args[0].upper() if context.args else None
        
        if currency_filter and currency_filter not in ['THB', 'MMK']:
            await update.message.reply_text("❌ Currency must be THB or MMK")
            return
        
        accounts = self.db.get_bank_accounts(currency_filter)
        
        if not accounts:
            await update.message.reply_text("📋 No admin bank accounts found.")
            return
        
        message = "🏦 **Admin Bank Accounts:**\n\n"
        
        current_currency = None
        for account in accounts:
            if account.currency != current_currency:
                if current_currency is not None:
                    message += "\n"
                message += f"**{account.currency}:**\n"
                current_currency = account.currency
            
            status = "✅" if account.is_active else "❌"
            display = f"{account.display_name} ({account.bank_name})" if account.display_name else account.bank_name
            message += f"{status} ID:{account.id} | {display}\n"
            message += f"   {account.account_number} - {account.account_name}\n"
        
        message += f"\n**Deactivate:** `/removebank <id>`"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    @admin_only
    async def remove_bank_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Deactivate admin bank account (admin only)"""
        if not context.args:
            await update.message.reply_text("❌ Usage: /removebank <account_id>")
            return
        
        try:
            account_id = int(context.args[0])
            self.db.deactivate_admin_bank_account(account_id)
            await update.message.reply_text(f"✅ Bank account #{account_id} deactivated")
        except ValueError:
            await update.message.reply_text("❌ Invalid account ID")

    @admin_only
    async def adjust_balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Adjust balance for a specific bank (admin only)"""
        if len(context.args) < 3:
            message = """💰 **Adjust Bank Balance**

**Usage:**
`/adjust <currency> <bank_name> <amount>`

**Examples:**
`/adjust THB KrungthaiBank +5000` - Add 5000 THB
`/adjust MMK KBZ -10000` - Subtract 10000 MMK
`/adjust THB PromptPay 150000` - Set to 150000 THB

**Note:** Use + or - for relative changes, or just number for absolute value
"""
            await update.message.reply_text(message, parse_mode='Markdown')
            return
        
        currency = context.args[0].upper()
        bank_name = context.args[1]
        amount_str = context.args[2]
        
        if currency not in ['THB', 'MMK']:
            await update.message.reply_text("❌ Currency must be THB or MMK")
            return
        
        try:
            # Check if it's relative (+/-) or absolute
            if amount_str.startswith('+') or amount_str.startswith('-'):
                # Relative adjustment
                amount_change = float(amount_str)
                old_balance = self.db.get_balance(currency, bank_name)
                self.db.update_balance(currency, bank_name, amount_change)
                new_balance = self.db.get_balance(currency, bank_name)
                
                await update.message.reply_text(
                    f"✅ **Balance Adjusted**\n\n"
                    f"Currency: {currency}\n"
                    f"Bank: {bank_name}\n"
                    f"Old Balance: {old_balance:,.2f}\n"
                    f"Change: {amount_change:+,.2f}\n"
                    f"New Balance: {new_balance:,.2f}",
                    parse_mode='Markdown'
                )
            else:
                # Absolute value
                new_balance = float(amount_str)
                old_balance = self.db.get_balance(currency, bank_name)
                self.db.set_balance(currency, bank_name, new_balance)
                
                await update.message.reply_text(
                    f"✅ **Balance Set**\n\n"
                    f"Currency: {currency}\n"
                    f"Bank: {bank_name}\n"
                    f"Old Balance: {old_balance:,.2f}\n"
                    f"New Balance: {new_balance:,.2f}",
                    parse_mode='Markdown'
                )
                
        except ValueError:
            await update.message.reply_text("❌ Invalid amount format")
    
    @admin_only
    async def init_balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Initialize balance for a new bank (admin only)"""
        if len(context.args) < 3:
            message = """🏦 **Initialize Bank Balance**

**Usage:**
`/initbalance <currency> <bank_name> <initial_amount>`

**Examples:**
`/initbalance THB KrungthaiBank 150000`
`/initbalance MMK KBZ 1500000`

**Note:** This will create or update the balance entry
"""
            await update.message.reply_text(message, parse_mode='Markdown')
            return
        
        currency = context.args[0].upper()
        bank_name = context.args[1]
        initial_amount = context.args[2]
        
        if currency not in ['THB', 'MMK', 'USDT']:
            await update.message.reply_text("❌ Currency must be THB, MMK, or USDT")
            return
        
        try:
            amount = float(initial_amount)
            self.db.set_balance(currency, bank_name, amount)
            
            await update.message.reply_text(
                f"✅ **Balance Initialized**\n\n"
                f"Currency: {currency}\n"
                f"Bank: {bank_name}\n"
                f"Initial Balance: {amount:,.2f}",
                parse_mode='Markdown'
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid amount format")

    @admin_only
    async def update_display_name_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Update display name for a bank account (admin only)"""
        if len(context.args) < 2:
            message = """🏷️ **Update Bank Display Name**

**Usage:**
`/updatedisplay <account_id> <display_name>`

**Examples:**
`/updatedisplay 1 TZH (K Bank)`
`/updatedisplay 2 TKZ (PP)`
`/updatedisplay 3 MMN (SCB)`

**Note:** Use `/listbanks` to see account IDs
"""
            await update.message.reply_text(message, parse_mode='Markdown')
            return
        
        try:
            account_id = int(context.args[0])
            display_name = ' '.join(context.args[1:])
            
            success = self.db.update_bank_display_name(account_id, display_name)
            
            if success:
                await update.message.reply_text(
                    f"✅ **Display Name Updated**\n\n"
                    f"Account ID: {account_id}\n"
                    f"New Display Name: {display_name}",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(f"❌ Account #{account_id} not found")
        except ValueError:
            await update.message.reply_text("❌ Invalid account ID")
