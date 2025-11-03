"""
User handlers for exchange operations
"""
import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TimedOut, NetworkError

from app.config.settings import Config
from app.services.database_service import DatabaseService
from app.services.ocr_service import OCRService
from app.utils.command_protection import private_chat_only, private_chat_only_callback

logger = logging.getLogger(__name__)


class UserHandlers:
    """Handle user interactions for currency exchange"""
    
    def __init__(self, db_service: DatabaseService, ocr_service: OCRService):
        """
        Initialize user handlers
        
        Args:
            db_service: Database service instance
            ocr_service: OCR service instance
        """
        self.db = db_service
        self.ocr = ocr_service
        self.config = Config
        logger.info("User handlers initialized")
    
    @private_chat_only
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        rate = self.db.get_current_rate()
        
        # Get THB and MMK admin accounts from database
        thb_accounts = self.db.get_bank_accounts('THB')
        mmk_accounts = self.db.get_bank_accounts('MMK')
        
        # Build THB accounts section
        thb_section = "🇹🇭 **THB Banks:**\n"
        if thb_accounts:
            for account in thb_accounts:
                thb_section += f"• {account.display}\n"
        else:
            thb_section += "📌 Contact admin\n"
        
        # Build MMK accounts section
        mmk_section = "\n🇲🇲 **MMK Banks:**\n"
        if mmk_accounts:
            for account in mmk_accounts:
                mmk_section += f"• {account.display}\n"
        else:
            mmk_section += "📌 Contact admin\n"
        
        welcome_message = f"""💱 **Welcome to Currency Exchange Service**

Exchange between Thai Baht (THB) and Myanmar Kyat (MMK) easily and securely.

📊 **Current Exchange Rate:** 
1 THB = {rate} MMK

{thb_section}{mmk_section}

⚠️ **Important:**
• Make sure your transfer is successful
• Keep your receipt screenshot ready
• Double-check bank account details

Ready to exchange? Choose your direction:
"""
        
        keyboard = [
            [InlineKeyboardButton("🇹🇭 THB → MMK 🇲🇲", callback_data="exchange_thb_to_mmk")],
            [InlineKeyboardButton("🇲🇲 MMK → THB 🇹🇭", callback_data="exchange_mmk_to_thb")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
    
    @private_chat_only_callback
    async def start_exchange_thb_to_mmk(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle THB to MMK exchange"""
        query = update.callback_query
        await query.answer()
        
        # Store exchange direction
        context.user_data['exchange_direction'] = 'THB_TO_MMK'
        context.user_data['from_currency'] = 'THB'
        context.user_data['to_currency'] = 'MMK'
        
        await query.edit_message_text(
            "📸 **Step 1: Upload THB Payment Receipt**\n\n"
            "Please upload your THB payment receipt screenshot.\n\n"
            "✅ Make sure the receipt shows:\n"
            "• Transfer amount (THB)\n"
            "• Bank names (sender and receiver)\n"
            "• Transaction status (successful)\n"
            "• Date and reference number\n\n"
            "📷 Send a clear screenshot now:",
            parse_mode='Markdown'
        )
        
        return self.config.UPLOAD_RECEIPT
    
    @private_chat_only_callback
    async def start_exchange_mmk_to_thb(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle MMK to THB exchange"""
        query = update.callback_query
        await query.answer()
        
        # Store exchange direction
        context.user_data['exchange_direction'] = 'MMK_TO_THB'
        context.user_data['from_currency'] = 'MMK'
        context.user_data['to_currency'] = 'THB'
        
        await query.edit_message_text(
            "📸 **Step 1: Upload MMK Payment Receipt**\n\n"
            "Please upload your MMK payment receipt screenshot.\n\n"
            "✅ Make sure the receipt shows:\n"
            "• Transfer amount (MMK)\n"
            "• Bank names (sender and receiver)\n"
            "• Transaction status (successful)\n"
            "• Date and reference number\n\n"
            "📷 Send a clear screenshot now:",
            parse_mode='Markdown'
        )
        
        return self.config.UPLOAD_RECEIPT
    
    @private_chat_only
    async def handle_receipt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle receipt image upload"""
        photo = update.message.photo[-1]
        
        # Get exchange direction
        exchange_direction = context.user_data.get('exchange_direction', 'THB_TO_MMK')
        from_currency = context.user_data.get('from_currency', 'THB')
        to_currency = context.user_data.get('to_currency', 'MMK')
        
        # Download photo with retry logic for network timeouts
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                file = await context.bot.get_file(photo.file_id)
                file_path = f"{self.config.RECEIPTS_DIR}/{update.message.from_user.id}_{datetime.now().timestamp()}.jpg"
                await file.download_to_drive(file_path)
                break
            except (TimedOut, NetworkError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Network timeout on attempt {attempt + 1}, retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to download receipt after {max_retries} attempts: {e}")
                    await update.message.reply_text(
                        "❌ **Network Error**\n\n"
                        "Unable to download your receipt due to network issues.\n\n"
                        "Please try again in a moment. If the problem persists, "
                        "try sending a smaller image or contact support."
                    )
                    return self.config.UPLOAD_RECEIPT
        
        # Store file path in context
        context.user_data['receipt_path'] = file_path
        
        processing_msg = await update.message.reply_text("🔍 Processing your receipt... Please wait.")
        
        # Extract receipt info using OCR
        receipt_info = self.ocr.extract_receipt_info(file_path)
        
        if not receipt_info:
            await self._send_message_with_retry(
                processing_msg.edit_text,
                "❌ Unable to read your receipt clearly.\n\n"
                "Please send a clearer screenshot with all details visible."
            )
            return self.config.UPLOAD_RECEIPT
        
        context.user_data['receipt_info'] = receipt_info
        
        # Validate receipt status
        if receipt_info.get('status') and 'success' not in receipt_info['status'].lower():
            await self._send_message_with_retry(
                processing_msg.edit_text,
                "⚠️ Your transaction doesn't appear to be successful.\n\n"
                "Please check your transaction status and resend a successful receipt."
            )
            return self.config.UPLOAD_RECEIPT
        
        # Validate receiver account based on direction
        receiver_name = receipt_info.get('receiver_name')
        receiver_bank = receipt_info.get('receiver_bank')
        
        if receiver_name:
            # Validate against the currency being sent
            admin_account = self.db.validate_receiver_account(receiver_name, receiver_bank, from_currency)
            
            if not admin_account:
                # Get all admin accounts to show in error message
                all_accounts = self.db.get_bank_accounts(from_currency)
                
                error_msg = f"❌ **Invalid Receiver Account**\n\n"
                error_msg += f"📋 **Detected from receipt:**\n"
                if receiver_name:
                    error_msg += f"• Name: '{receiver_name}'\n"
                if receiver_bank:
                    error_msg += f"• Bank: '{receiver_bank}'\n"
                error_msg += f"\n"
                error_msg += f"⚠️ This doesn't match our official {from_currency} accounts.\n\n"
                
                if all_accounts:
                    error_msg += f"✅ **Our Official {from_currency} Accounts:**\n"
                    for acc in all_accounts[:3]:  # Show first 3 accounts
                        error_msg += f"• {acc.bank_name} - {acc.account_name}\n"
                    error_msg += f"\n"
                
                error_msg += f"Please make sure you transferred to one of our official accounts.\n"
                error_msg += f"If you believe this is an error, contact admin."
                
                await self._send_message_with_retry(processing_msg.edit_text, error_msg)
                return self.config.UPLOAD_RECEIPT
            
            # Store validated admin bank info
            context.user_data['admin_receiving_bank'] = admin_account.bank_name
            context.user_data['admin_account_validated'] = True
            
            # Log successful validation
            matched_name = admin_account.account_name
            matched_bank = admin_account.bank_name
            logger.info(f"Receipt validated: '{receiver_name}' at '{receiver_bank}' → matched {matched_name} at {matched_bank}")
        
        # Check if amount is detected
        if receipt_info.get('amount'):
            from app.utils.currency_utils import calculate_exchange
            
            amount = float(receipt_info['amount'])
            rate = self.db.get_current_rate()
            
            # Calculate with proper rounding
            sent_amount, received_amount = calculate_exchange(
                amount, rate, from_currency, to_currency
            )
            
            context.user_data['sent_amount'] = sent_amount
            context.user_data['received_amount'] = received_amount
            
            rate_text = f"1 THB = {rate} MMK"
            
            # Build success message with detected info
            success_message = f"✅ **Receipt Processed Successfully!**\n\n"
            
            # Format amounts based on currency
            if from_currency == 'MMK':
                success_message += f"💰 Amount detected: **{sent_amount:,.0f} {from_currency}**\n"
            else:
                success_message += f"💰 Amount detected: **{sent_amount:,.2f} {from_currency}**\n"
            
            if to_currency == 'MMK':
                success_message += f"📊 You will receive: **{received_amount:,.0f} {to_currency}**\n"
            else:
                success_message += f"📊 You will receive: **{received_amount:,.2f} {to_currency}**\n"
            
            success_message += f"📈 Rate: {rate_text}\n\n"
            
            # Show what was detected from receipt
            if receiver_name or receiver_bank:
                success_message += f"📋 **Verified Transfer To:**\n"
                if receiver_name:
                    success_message += f"• {receiver_name}\n"
                if receiver_bank:
                    success_message += f"• {receiver_bank}\n"
                success_message += f"\n"
            
            success_message += f"📝 **Step 2: Enter Your {to_currency} Bank Details**\n\n"
            success_message += f"Please provide your receiving account information:\n\n"
            success_message += f"**Format:**\n"
            success_message += f"`Bank Name | Account Number | Account Name`\n\n"
            success_message += f"**Example:**\n"
            if to_currency == 'MMK':
                success_message += f"`AYA | 00987654321 | AUNG AUNG`"
            else:
                success_message += f"`SCB | 1234567890 | SOMCHAI SMITH`"
            
            # Try to edit message with retry logic
            await self._send_message_with_retry(
                processing_msg.edit_text,
                success_message,
                parse_mode='Markdown'
            )
            return self.config.ENTER_BANK_INFO
        else:
            amount_message = (
                f"✅ Receipt uploaded successfully!\n\n"
                f"💰 Please enter the amount in {from_currency} you have transferred:\n\n"
                f"Example: 1000"
            )
            
            # Try to edit message with retry logic
            await self._send_message_with_retry(
                processing_msg.edit_text,
                amount_message
            )
            return self.config.ENTER_AMOUNT
    
    @private_chat_only
    async def handle_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle manual amount entry"""
        try:
            amount = float(update.message.text.replace(',', ''))
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            # Get exchange direction
            from app.utils.currency_utils import calculate_exchange
            
            exchange_direction = context.user_data.get('exchange_direction', 'THB_TO_MMK')
            from_currency = context.user_data.get('from_currency', 'THB')
            to_currency = context.user_data.get('to_currency', 'MMK')
            
            rate = self.db.get_current_rate()
            
            # Calculate with proper rounding
            sent_amount, received_amount = calculate_exchange(
                amount, rate, from_currency, to_currency
            )
            
            context.user_data['sent_amount'] = sent_amount
            context.user_data['received_amount'] = received_amount
            
            rate_text = f"1 THB = {rate} MMK"
            
            # Format amounts based on currency
            if from_currency == 'MMK':
                amount_text = f"{sent_amount:,.0f} {from_currency}"
            else:
                amount_text = f"{sent_amount:,.2f} {from_currency}"
            
            if to_currency == 'MMK':
                receive_text = f"{received_amount:,.0f} {to_currency}"
            else:
                receive_text = f"{received_amount:,.2f} {to_currency}"
            
            await update.message.reply_text(
                f"✅ **Amount Confirmed**\n\n"
                f"💰 Amount: **{amount_text}**\n"
                f"📊 You will receive: **{receive_text}**\n"
                f"📈 Rate: {rate_text}\n\n"
                f"📝 **Step 2: Enter Your {to_currency} Bank Details**\n\n"
                f"Please provide your receiving account information:\n\n"
                f"**Format:**\n"
                f"`Bank Name | Account Number | Account Name`\n\n"
                f"**Example:**\n"
                f"{'`AYA | 00987654321 | AUNG AUNG`' if to_currency == 'MMK' else '`SCB | 1234567890 | SOMCHAI SMITH`'}",
                parse_mode='Markdown'
            )
            return self.config.ENTER_BANK_INFO
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid amount. Please enter a valid number:\n\n"
                "Example: 1000"
            )
            return self.config.ENTER_AMOUNT
    
    @private_chat_only
    async def handle_bank_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle bank information for receiving currency"""
        bank_info = update.message.text.split('|')
        
        if len(bank_info) != 3:
            await update.message.reply_text(
                "❌ Invalid format.\n\n"
                "Please use this format:\n"
                "`Bank Name | Account Number | Account Name`\n\n"
                "Example:\n"
                "`AYA | 00987654321 | AUNG AUNG`",
                parse_mode='Markdown'
            )
            return self.config.ENTER_BANK_INFO
        
        bank_name = bank_info[0].strip()
        account_number = bank_info[1].strip()
        account_name = bank_info[2].strip()
        
        # Get exchange direction
        exchange_direction = context.user_data.get('exchange_direction', 'THB_TO_MMK')
        from_currency = context.user_data.get('from_currency', 'THB')
        to_currency = context.user_data.get('to_currency', 'MMK')
        
        # Validate bank name based on receiving currency
        supported_banks = self.config.MMK_BANKS if to_currency == 'MMK' else self.config.THB_BANKS
        if not any(bank.lower() in bank_name.lower() for bank in supported_banks):
            banks_list = '\n'.join([f"• {bank}" for bank in supported_banks])
            await update.message.reply_text(
                f"⚠️ Please use one of the supported {to_currency} banks:\n\n"
                f"{banks_list}\n\n"
                f"Please resend in correct format."
            )
            return self.config.ENTER_BANK_INFO
        
        # Store user bank info
        context.user_data['user_bank_name'] = bank_name
        context.user_data['user_account_number'] = account_number
        context.user_data['user_account_name'] = account_name
        
        # Get amounts
        sent_amount = context.user_data['sent_amount']
        received_amount = context.user_data['received_amount']
        rate = self.db.get_current_rate()
        
        # Get sender bank from receipt
        receipt_info = context.user_data.get('receipt_info', {})
        from_bank = receipt_info.get('sender_bank', 'Unknown')
        
        # Get admin receiving bank from validated receipt
        admin_receiving_bank = context.user_data.get('admin_receiving_bank', receipt_info.get('receiver_bank', 'Unknown'))
        
        # Create transaction
        transaction_id = self.db.create_transaction(
            user_id=update.message.from_user.id,
            username=update.message.from_user.username,
            exchange_direction=exchange_direction,
            from_currency=from_currency,
            to_currency=to_currency,
            sent_amount=sent_amount,
            received_amount=received_amount,
            exchange_rate=rate,
            user_bank_name=bank_name,
            user_account_number=account_number,
            user_account_name=account_name,
            from_bank=from_bank,
            admin_receiving_bank=admin_receiving_bank,
            receipt_path=context.user_data.get('receipt_path')
        )
        
        # Update balance - add to admin account for received currency
        self.db.update_balance(from_currency, admin_receiving_bank, sent_amount)
        
        # Notify admin
        await self._notify_admin(
            context, 
            transaction_id, 
            update.message.from_user,
            exchange_direction,
            from_currency,
            to_currency,
            sent_amount,
            received_amount,
            rate,
            bank_name,
            account_number,
            account_name,
            admin_receiving_bank
        )

        calculation_symbol = 'x' if from_currency == 'THB' or to_currency == 'MMK' else '/'
        
        await update.message.reply_text(
            f"**Buy {sent_amount} {calculation_symbol} {rate} = {received_amount:,.2f} **\n\n"
            f"{account_number}\n"
            f"{account_name}\n"
            f"{bank_name}\n",
            parse_mode='Markdown'
        )
        
        # Clear user data
        context.user_data.clear()
        
        return ConversationHandler.END
    
    async def _send_message_with_retry(self, send_func, *args, **kwargs):
        """
        Send or edit a message with retry logic for network timeouts
        
        Args:
            send_func: The function to call (e.g., message.edit_text, message.reply_text)
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        """
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                return await send_func(*args, **kwargs)
            except (TimedOut, NetworkError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Network timeout on attempt {attempt + 1}, retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to send message after {max_retries} attempts: {e}")
                    # Don't raise, just log - the user will see the previous message
                    return None
    
    async def _notify_admin(self, context, transaction_id, user, exchange_direction,
                           from_currency, to_currency, sent_amount, received_amount,
                           rate, user_bank_name, user_account_number, 
                           user_account_name, admin_receiving_bank):
        """Notify admin group about new transaction with receipt photo"""
        
        # Format message based on exchange direction
        if exchange_direction == 'THB_TO_MMK':
            title = f"Buy {sent_amount:,.0f} × {rate} = **{received_amount:,.0f}**"
            # calculation = f"Buy {sent_amount:,.0f} THB × {rate} = **{received_amount:,.0f} MMK**"
        else:  # MMK_TO_THB
            title = f"Buy {sent_amount:,.0f} / {rate} = **{received_amount:,.0f}**"
            # calculation = f"Buy {sent_amount:,.0f} MMK / {rate} = **{received_amount:,.2f} THB**"
        
        admin_message = f"""{title}

{user_account_number}
{user_account_name}
{user_bank_name}

"""
        
        keyboard = [
            [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{transaction_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            # Get admin group and topic from database
            admin_group_id = self.db.get_setting('admin_group_id') or self.config.ADMIN_GROUP_ID
            admin_topic_id = self.db.get_setting('admin_topic_id') or self.config.ADMIN_TOPIC_ID
            
            # Get receipt path from transaction in database
            transaction = self.db.get_transaction(transaction_id)
            receipt_path = transaction.receipt_path if transaction else None
            
            logger.info(f"Notifying admin for transaction #{transaction_id}, receipt_path: {receipt_path}")
            
            if receipt_path:
                logger.info(f"Receipt path exists check: {os.path.exists(receipt_path)}")
                if not os.path.exists(receipt_path):
                    logger.warning(f"Receipt file not found at: {receipt_path}")
            
            if receipt_path and os.path.exists(receipt_path):
                logger.info(f"Sending notification WITH photo")
                # Send with photo
                if admin_topic_id:
                    await self._send_message_with_retry(
                        context.bot.send_photo,
                        chat_id=admin_group_id,
                        photo=open(receipt_path, 'rb'),
                        caption=admin_message,
                        message_thread_id=int(admin_topic_id),
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    await self._send_message_with_retry(
                        context.bot.send_photo,
                        chat_id=admin_group_id,
                        photo=open(receipt_path, 'rb'),
                        caption=admin_message,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
            else:
                # Send without photo (fallback)
                logger.info(f"Sending notification WITHOUT photo (receipt_path: {receipt_path})")
                if admin_topic_id:
                    await self._send_message_with_retry(
                        context.bot.send_message,
                        chat_id=admin_group_id,
                        text=admin_message,
                        message_thread_id=int(admin_topic_id),
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    await self._send_message_with_retry(
                        context.bot.send_message,
                        chat_id=admin_group_id,
                        text=admin_message,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
        except Exception as e:
            logger.error(f"Error sending to admin: {e}")
    
    @private_chat_only
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the conversation"""
        await update.message.reply_text(
            "❌ Operation cancelled.\n\n"
            "Use /start to begin again."
        )
        context.user_data.clear()
        return ConversationHandler.END
