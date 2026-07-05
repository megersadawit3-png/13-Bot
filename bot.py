"""
የተጠቃሚ ቴሌግራም ቦት - የዲጂታል ህትመት ገበያ መድረክ
በሶስት ቋንቋዎች: አማርኛ, እንግሊዝኛ, ኦሮምኛ
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)

from config import BOT_TOKEN, ADMIN_IDS, SALES_THRESHOLD
from database import (
    init_db, get_user, create_user, update_user_language, get_user_language,
    create_author, get_author_by_user, get_author_by_id,
    create_content, get_content, get_published_content, get_content_by_author,
    update_content_status, increment_sales, update_content_price,
    create_purchase, add_to_library, get_user_library, update_download_status,
    create_report, get_reports
)
from language import get_text, get_language_name, get_supported_languages

# ============================================
# ሎግ ማዋቀር
# ============================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================
# የቋንቋ ምርጫ ቁልፍ ሰሌዳ
# ============================================

def get_language_keyboard():
    """የቋንቋ ምርጫ ቁልፍ ሰሌዳ መፍጠር"""
    keyboard = [
        [
            InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="lang_am"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇪🇹 Oromiffa", callback_data="lang_or")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ============================================
# የቋንቋ ምርጫ አስተናጋጅ
# ============================================

async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የቋንቋ ምርጫ ማስቀመጥ"""
    query = update.callback_query
    await query.answer()
    
    lang = query.data.split('_')[1]
    user_id = update.effective_user.id
    
    # ቋንቋ ማስቀመጥ
    update_user_language(user_id, lang)
    
    # ማሳወቂያ
    await query.edit_message_text(get_text(lang, 'language_changed'))
    
    # ወደ መነሻ ገጽ መመለስ
    await start(update, context)

# ============================================
# መሰረታዊ ትዕዛዞች
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የ/start ትዕዛዝ"""
    user = update.effective_user
    
    # ተጠቃሚው ቋንቋ አለው?
    db_user = get_user(user.id)
    
    if not db_user:
        # አዲስ ተጠቃሚ - ቋንቋ ይምረጡ
        await update.message.reply_text(
            "🌍 Welcome! / እንኳን ደህና መጣህ! / Anaadhufu!\n\n"
            "Please select your language:\n"
            "እባክህ ቋንቋህን ምረጥ:\n"
            "Afaan keessan filadhaa:",
            reply_markup=get_language_keyboard()
        )
        return
    
    # የተጠቃሚ ቋንቋ
    lang = db_user.get('language', 'am')
    
    # መነሻ ገጽ
    keyboard = [
        [InlineKeyboardButton(get_text(lang, 'buttons.browse'), callback_data="browse")],
        [InlineKeyboardButton(get_text(lang, 'buttons.become_author'), callback_data="become_author")],
        [InlineKeyboardButton(get_text(lang, 'buttons.my_library'), callback_data="my_library")],
        [InlineKeyboardButton(get_text(lang, 'buttons.about'), callback_data="about")],
        [InlineKeyboardButton(get_text(lang, 'buttons.change_language'), callback_data="change_language")]
    ]
    
    if db_user.get('role') == 'admin':
        keyboard.append([InlineKeyboardButton(get_text(lang, 'buttons.admin'), callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text(lang, 'welcome', name=user.full_name or user.username or '') + "\n\n" +
        get_text(lang, 'welcome_description'),
        reply_markup=reply_markup
    )

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ቋንቋ መቀየር"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🌍 Select your language / ቋንቋህን ምረጥ / Afaan keessan filadhaa:",
        reply_markup=get_language_keyboard()
    )

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ወደ መነሻ ገጽ መመለስ"""
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ስለ መድረክ"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    message = f"""
📖 *ስለ መድረክ / About / Waa'ee Mardachaa*

ይህ የዲጂታል ህትመት ገበያ መድረክ ነው።
This is a Digital Publishing Marketplace.
Kun Mardacha Gaazexaa Digitaalaa ti.

*ባህሪያት / Features / Amaloota:*
• 📚 የይዘት መደርደሪያ / Content Browsing / Marii Wantootaa
• ✍️ ደራሲ መሆን / Become an Author / Barreessaa ta'uu
• 🛒 ይዘት መግዛት / Purchase Content / Wantoota bituu
• 📖 ቤተ-መጽሐፍት / Personal Library / Mankitaabaa Ofii
• 🔐 DRM ጥበቃ / DRM Protection / Eegumsa DRM
• 🌍 ሶስት ቋንቋዎች / Three Languages / Afaanota Sadan

*ተልዕኮ / Mission / Dhaabbata:*
ደራሲዎችን እና አንባቢዎችን በኢትዮጵያ እና በአፍሪካ ማገናኘት።
Connecting authors and readers in Ethiopia and Africa.
Barreessootaa fi loholtoota Itoophiyaa fi Afrikaa walitti qabu.

📌 *ስሪት / Version / Fooyya'insa:* MVP 1.0
📅 *ቀን / Date / Guyyaa:* {datetime.now().strftime('%Y-%m-%d')}
"""
    
    keyboard = [[InlineKeyboardButton(get_text(lang, 'buttons.back'), callback_data="back_to_start")]]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# ============================================
# መደርደሪያ
# ============================================

async def browse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የታተሙ ይዘቶችን ማሳየት"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    content_list = get_published_content()
    
    if not content_list:
        await query.edit_message_text(get_text(lang, 'browse.empty'))
        return
    
    message = get_text(lang, 'browse.title') + "\n\n"
    keyboard = []
    
    for idx, content in enumerate(content_list[:10], 1):
        message += f"{idx}. *{content['title']}*\n"
        message += f"   {get_text(lang, 'browse.price', price=content['price'])}\n"
        desc = content['description'][:50] if content['description'] else get_text(lang, 'browse.no_description')
        message += f"   📝 {desc}...\n\n"
        keyboard.append([InlineKeyboardButton(
            f"📖 {content['title'][:30]}",
            callback_data=f"view_{content['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton(get_text(lang, 'buttons.back'), callback_data="back_to_start")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def view_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የይዘት ዝርዝሮችን ማሳየት"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    content_id = int(query.data.split('_')[1])
    content = get_content(content_id)
    
    if not content:
        await query.edit_message_text(get_text(lang, 'content.not_found'))
        return
    
    # ደራሲ ስም ማግኘት
    author = get_author_by_id(content['author_id'])
    author_user = get_user(author['user_id']) if author else None
    author_name = author_user.get('full_name', 'ያልታወቀ') if author_user else 'ያልታወቀ'
    
    keyboard = [
        [InlineKeyboardButton(get_text(lang, 'buttons.buy'), callback_data=f"buy_{content_id}")],
        [InlineKeyboardButton(get_text(lang, 'buttons.back'), callback_data="browse")]
    ]
    
    if content.get('sample_file_id'):
        keyboard.insert(0, [InlineKeyboardButton("📎 " + get_text(lang, 'content.sample_available'), callback_data=f"sample_{content_id}")])
    
    # ሪፖርት ማድረጊያ
    keyboard.append([InlineKeyboardButton("🚨 ሪፖርት / Report / Gabaasa", callback_data=f"report_{content_id}")])
    
    message = get_text(lang, 'content.view',
        title=content['title'],
        description=content['description'] or get_text(lang, 'browse.no_description'),
        price=content['price'],
        sales=content['total_sales'],
        category=content['category'] or 'አልተመደበም'
    )
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ============================================
# ግዢ
# ============================================

async def buy_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ይዘት መግዛት"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    content_id = int(query.data.split('_')[1])
    content = get_content(content_id)
    user = get_user(user_id)
    
    if not content:
        await query.edit_message_text(get_text(lang, 'content.not_found'))
        return
    
    # ይዘቱ የታተመ መሆኑን መፈተሽ
    if content['status'] != 'published':
        await query.edit_message_text("⛔ ይህ ይዘት አሁን አይገኝም።")
        return
    
    # ተጠቃሚው ቀድሞ ገዝቶ እንደሆነ መፈተሽ
    library = get_user_library(user['id'])
    for item in library:
        if item['id'] == content_id:
            await query.edit_message_text(
                get_text(lang, 'purchase.already_owned', title=content['title'])
            )
            return
    
    # ግዢ መፍጠር
    create_purchase(user['id'], content_id, content['price'])
    add_to_library(user['id'], content_id)
    new_sales = increment_sales(content_id)
    
    # የደራሲ ሽያጭ መጨመር
    author = get_author_by_id(content['author_id'])
    if author:
        update_author_sales(author['id'])
    
    # የሽያጭ ገደብ መፈተሽ (50 ሽያጭ)
    if new_sales >= SALES_THRESHOLD:
        # ደራሲውን ማሳወቅ
        author_user = get_user(author['user_id']) if author else None
        if author_user:
            await context.bot.send_message(
                chat_id=author_user['telegram_id'],
                text=f"⚠️ የይዘትህ '{content['title']}' {SALES_THRESHOLD} ሽያጭ ደርሷል!\n"
                     f"የአገልግሎት ክፍያ ለመክፈል አስተዳዳሪውን አግኝ።"
            )
        
        # አስተዳዳሪውን ማሳወቅ
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📢 {content['title']} {SALES_THRESHOLD} ሽያጭ ደርሷል!\n"
                     f"የአገልግሎት ክፍያ መከፈል አለበት።"
            )
    
    await query.edit_message_text(
        get_text(lang, 'purchase.success', title=content['title'], price=content['price'])
    )

# ============================================
# ቤተ-መጽሐፍት
# ============================================

async def my_library(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የተጠቃሚ ቤተ-መጽሐፍት"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    user = get_user(user_id)
    library = get_user_library(user['id'])
    
    if not library:
        await query.edit_message_text(get_text(lang, 'library.empty'))
        return
    
    message = get_text(lang, 'library.title') + "\n\n"
    keyboard = []
    
    for item in library:
        message += f"• *{item['title']}*\n"
        message += f"  💰 {item['price']} ብር\n"
        if item.get('downloaded'):
            message += "  ✅ ተውርዷል\n"
        message += "\n"
        keyboard.append([InlineKeyboardButton(
            f"📥 {item['title'][:30]}",
            callback_data=f"download_{item['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton(get_text(lang, 'buttons.back'), callback_data="back_to_start")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def download_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ይዘት ማውረድ"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    content_id = int(query.data.split('_')[1])
    content = get_content(content_id)
    
    if not content:
        await query.edit_message_text(get_text(lang, 'content.not_found'))
        return
    
    # የማውረጃ ሁኔታ ማሻሻል
    update_download_status(user_id, content_id)
    
    # ፋይሉን መላክ (በቴሌግራም በኩል)
    if content.get('file_id'):
        await query.edit_message_text(
            f"📥 {get_text(lang, 'library.download', title=content['title'])}\n\n"
            f"ፋይሉን ለማውረድ / እዚህ ላይ ይጫኑ:"
        )
        # የፋይል መላክ
        await context.bot.send_document(
            chat_id=user_id,
            document=content['file_id'],
            caption=f"📖 {content['title']}\n💰 {content['price']} ብር"
        )
    else:
        await query.edit_message_text("❌ ፋይሉ አልተገኘም።")

# ============================================
# ደራሲ መሆን
# ============================================

async def become_author(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ደራሲ ለመሆን ማመልከቻ"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    user = get_user(user_id)
    author = get_author_by_user(user['id'])
    
    if author:
        await query.edit_message_text(
            get_text(lang, 'author.already', 
                level=author['level'],
                sales=author['total_sales']
            )
        )
        return
    
    # አዲስ ደራሲ መፍጠር
    author_id = create_author(user['id'])
    
    await query.edit_message_text(get_text(lang, 'author.welcome'))

# ============================================
# ይዘት መጫኛ
# ============================================

async def upload_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ይዘት መጫን መጀመር"""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    user = get_user(user_id)
    author = get_author_by_user(user['id'])
    
    if not author:
        await update.message.reply_text(get_text(lang, 'author.not_author'))
        return
    
    # የመጫኛ መመሪያ
    context.user_data['upload_step'] = 'title'
    await update.message.reply_text(get_text(lang, 'upload.instruction'))

async def handle_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የመጫኛ ሂደት አያያዝ"""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    user = get_user(user_id)
    author = get_author_by_user(user['id'])
    
    if not author:
        await update.message.reply_text(get_text(lang, 'author.not_author'))
        return
    
    step = context.user_data.get('upload_step')
    
    if step == 'title':
        context.user_data['title'] = update.message.text
        context.user_data['upload_step'] = 'description'
        await update.message.reply_text(get_text(lang, 'upload.title_prompt'))
    
    elif step == 'description':
        context.user_data['description'] = update.message.text
        context.user_data['upload_step'] = 'category'
        await update.message.reply_text(get_text(lang, 'upload.description_prompt'))
    
    elif step == 'category':
        context.user_data['category'] = update.message.text
        context.user_data['upload_step'] = 'price'
        await update.message.reply_text(get_text(lang, 'upload.category_prompt'))
    
    elif step == 'price':
        try:
            price = float(update.message.text)
            if price <= 0:
                raise ValueError
            context.user_data['price'] = price
            context.user_data['upload_step'] = 'file'
            await update.message.reply_text(get_text(lang, 'upload.price_prompt'))
        except ValueError:
            await update.message.reply_text(get_text(lang, 'upload.invalid_price'))
    
    elif step == 'file':
        if update.message.document:
            file = update.message.document
            file_name = file.file_name or 'unknown.pdf'
            
            if not file_name.lower().endswith('.pdf'):
                await update.message.reply_text(get_text(lang, 'upload.invalid_file'))
                return
            
            # ይዘት መፍጠር
            content_id = create_content(
                author_id=author['id'],
                title=context.user_data['title'],
                description=context.user_data['description'],
                category=context.user_data['category'],
                file_id=file.file_id,
                price=context.user_data['price']
            )
            
            # አስተዳዳሪዎችን ማሳወቅ
            for admin_id in ADMIN_IDS:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"📢 አዲስ ይዘት ተጭኗል!\n"
                         f"📖 {context.user_data['title']}\n"
                         f"✍️ {update.effective_user.full_name or update.effective_user.username}\n"
                         f"💰 {context.user_data['price']} ብር\n"
                         f"🆔 {content_id}"
                )
            
            await update.message.reply_text(
                get_text(lang, 'upload.success',
                    title=context.user_data['title'],
                    price=context.user_data['price']
                )
            )
            
            context.user_data.clear()
        else:
            await update.message.reply_text(get_text(lang, 'upload.file_prompt'))

# ============================================
# ሪፖርት ማድረግ
# ============================================

async def report_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ይዘት ሪፖርት ማድረግ"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    content_id = int(query.data.split('_')[1])
    context.user_data['report_content_id'] = content_id
    context.user_data['report_step'] = 'reason'
    
    await query.edit_message_text(
        "🚨 *ሪፖርት ማድረግ / Report / Gabaasuu*\n\n"
        "ምክንያቱን ይጻፉ:\n"
        "Write the reason:\n"
        "Sababa barreessaa:",
        parse_mode='Markdown'
    )

async def handle_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የሪፖርት ምክንያት መቀበል"""
    if context.user_data.get('report_step') != 'reason':
        return
    
    user_id = update.effective_user.id
    content_id = context.user_data.get('report_content_id')
    
    if not content_id:
        return
    
    reason = update.message.text
    create_report(content_id, user_id, reason)
    
    await update.message.reply_text(
        "✅ ሪፖርትህ ተልኳል!\n"
        "አስተዳዳሪው ይገመግመዋል።\n\n"
        "Your report has been sent!\n"
        "The admin will review it.\n\n"
        "Gabaasaan keessan ergame!\n"
        "Bulchaan ni mirkaneessa."
    )
    
    context.user_data.clear()

# ============================================
# ዋና ተግባር
# ============================================

def main():
    """የቦት ማስጀመሪያ"""
    # የውሂብ ጎታ ማስጀመር
    init_db()
    logger.info("✅ የውሂብ ጎታ ተዘጋጅቷል")
    
    # መተግበሪያ መፍጠር
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ============================================
    # ትዕዛዞች
    # ============================================
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("upload", upload_content))
    application.add_handler(CommandHandler("language", change_language))
    
    # ============================================
    # Callback አስተናጋጆች
    # ============================================
    application.add_handler(CallbackQueryHandler(language_selection, pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(change_language, pattern="^change_language$"))
    application.add_handler(CallbackQueryHandler(browse, pattern="^browse$"))
    application.add_handler(CallbackQueryHandler(view_content, pattern="^view_"))
    application.add_handler(CallbackQueryHandler(buy_content, pattern="^buy_"))
    application.add_handler(CallbackQueryHandler(my_library, pattern="^my_library$"))
    application.add_handler(CallbackQueryHandler(download_content, pattern="^download_"))
    application.add_handler(CallbackQueryHandler(become_author, pattern="^become_author$"))
    application.add_handler(CallbackQueryHandler(back_to_start, pattern="^back_to_start$"))
    application.add_handler(CallbackQueryHandler(about, pattern="^about$"))
    application.add_handler(CallbackQueryHandler(report_content, pattern="^report_"))
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    
    # ============================================
    # መልእክት አስተናጋጆች
    # ============================================
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_upload))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_upload))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_report))
    
    # ============================================
    # ቦት ማስጀመር
    # ============================================
    logger.info("🚀 የተጠቃሚ ቦት በስራ ላይ ነው...")
    application.run_polling()

if __name__ == '__main__':
    main()
