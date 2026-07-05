"""
የአስተዳዳሪ ቴሌግራም ቦት - የዲጂታል ህትመት ገበያ መድረክ
በሶስት ቋንቋዎች: አማርኛ, እንግሊዝኛ, ኦሮምኛ
"""

import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)

from config import ADMIN_BOT_TOKEN, ADMIN_IDS
from database import (
    init_db, get_user, get_all_users, get_all_authors, get_author_by_user,
    get_content, get_all_content, get_pending_content, get_content_by_author,
    update_content_status, update_content_price,
    get_all_purchases, create_report, get_reports, get_report, update_report_status,
    get_user_library, update_author_level, get_author_by_id
)
from language import get_text, get_user_language, get_supported_languages

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================
# የደህንነት ማረጋገጫ
# ============================================

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def admin_only(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ አስተዳዳሪ አይደለህም!")
        return False
    return True

# ============================================
# መነሻ
# ============================================

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የአስተዳዳሪ ቦት መጀመሪያ"""
    if not await admin_only(update, context):
        return
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    pending_count = len(get_pending_content())
    dispute_count = len(get_reports(status='pending'))
    
    status = ""
    if pending_count > 0:
        status += get_text(lang, 'admin.pending_count', count=pending_count) + "\n"
    if dispute_count > 0:
        status += get_text(lang, 'admin.dispute_count', count=dispute_count) + "\n"
    
    keyboard = [
        [InlineKeyboardButton("📊 " + get_text(lang, 'admin.dashboard'), callback_data="admin_dashboard")],
        [InlineKeyboardButton("📝 " + get_text(lang, 'admin.pending'), callback_data="admin_pending")],
        [InlineKeyboardButton("✅ " + get_text(lang, 'admin.verify_authors'), callback_data="admin_verify_authors")],
        [InlineKeyboardButton("⚠️ " + get_text(lang, 'admin.disputes'), callback_data="admin_disputes")],
        [InlineKeyboardButton("👥 Users / ተጠቃሚዎች", callback_data="admin_users")],
        [InlineKeyboardButton("📈 " + get_text(lang, 'admin.analytics'), callback_data="admin_analytics")],
        [InlineKeyboardButton("📢 " + get_text(lang, 'admin.broadcast'), callback_data="admin_broadcast")],
        [InlineKeyboardButton("⚙️ " + get_text(lang, 'system.status'), callback_data="admin_system")],
        [InlineKeyboardButton("🌍 Change Language / ቋንቋ ቀይር", callback_data="admin_change_lang")]
    ]
    
    await update.message.reply_text(
        get_text(lang, 'admin.welcome', 
            name=update.effective_user.full_name,
            status=status
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================
# ዳሽቦርድ
# ============================================

async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.id):
        await query.edit_message_text("⛔ አስተዳዳሪ አይደለህም!")
        return
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    total_users = len(get_all_users())
    total_authors = len(get_all_authors())
    total_content = len(get_all_content())
    pending_content = len(get_pending_content())
    total_purchases = len(get_all_purchases())
    
    total_revenue = sum(p.get('amount', 0) for p in get_all_purchases())
    
    keyboard = [[InlineKeyboardButton("🔄 Refresh / አድስ", callback_data="admin_dashboard")],
                [InlineKeyboardButton("🔙 Back / ተመለስ", callback_data="admin_back")]]
    
    await query.edit_message_text(
        get_text(lang, 'admin.dashboard',
            total_users=total_users,
            total_authors=total_authors,
            total_content=total_content,
            pending_content=pending_content,
            total_purchases=total_purchases,
            revenue=total_revenue
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ============================================
# ይዘት ግምገማ
# ============================================

async def admin_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.id):
        await query.edit_message_text("⛔ አስተዳዳሪ አይደለህም!")
        return
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    pending = get_pending_content()
    
    if not pending:
        await query.edit_message_text(get_text(lang, 'admin.no_pending'))
        return
    
    message = "📝 *ለግምገማ የቀረቡ ይዘቶች* / *Pending Content*\n\n"
    keyboard = []
    
    for idx, content in enumerate(pending[:10], 1):
        message += f"{idx}. *{content['title']}*\n"
        message += f"   ✍️ {content.get('author_full_name', 'ያልታወቀ')}\n"
        message += f"   💰 {content['price']} ብር\n"
        message += f"   📂 {content.get('category', 'አልተመደበም')}\n\n"
        keyboard.append([
            InlineKeyboardButton(
                f"📖 {content['title'][:25]}...",
                callback_data=f"admin_review_{content['id']}"
            )
        ])
    
    if len(pending) > 10:
        message += f"\n... እና {len(pending) - 10} ተጨማሪ"
    
    keyboard.append([InlineKeyboardButton("🔙 Back / ተመለስ", callback_data="admin_back")])
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def admin_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.id):
        await query.edit_message_text("⛔ አስተዳዳሪ አይደለህም!")
        return
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    content_id = int(query.data.split('_')[2])
    content = get_content(content_id)
    
    if not content:
        await query.edit_message_text(get_text(lang, 'content.not_found'))
        return
    
    author = get_author_by_id(content['author_id'])
    author_user = get_user(author['user_id']) if author else None
    
    copyright_status = '✅ ተገልጿል' if content.get('copyright_declared') else '❌ አልተገለጸም'
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve / አፅድቅ", callback_data=f"admin_approve_{content_id}"),
            InlineKeyboardButton("❌ Reject / ውድቅ", callback_data=f"admin_reject_{content_id}")
        ],
        [InlineKeyboardButton("💰 Price / ዋጋ", callback_data=f"admin_price_{content_id}")],
        [InlineKeyboardButton("🔙 Back / ተመለስ", callback_data="admin_pending")]
    ]
    
    await query.edit_message_text(
        get_text(lang, 'admin.review',
            title=content['title'],
            description=content['description'] or 'ምንም የለም',
            category=content.get('category', 'አልተመደበም'),
            price=content['price'],
            author=author_user.get('full_name', 'ያልታወቀ') if author_user else 'ያልታወቀ',
            copyright=copyright_status,
            date=content.get('created_at', '')
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.id):
        await query.edit_message_text("⛔ አስተዳዳሪ አይደለህም!")
        return
    
    content_id = int(query.data.split('_')[2])
    content = get_content(content_id)
    
    if not content:
        await query.edit_message_text("❌ ይዘቱ አልተገኘም")
        return
    
    update_content_status(content_id, 'published')
    
    # ደራሲውን ማሳወቅ
    author = get_author_by_id(content['author_id'])
    if author:
        author_user = get_user(author['user_id'])
        if author_user:
            await context.bot.send_message(
                chat_id=author_user['telegram_id'],
                text=f"🎉 እንኳን ደስ አለህ!\n"
                     f"ይዘትህ '{content['title']}' ተፅድቋል!\n\n"
                     f"📖 {content['title']}\n"
                     f"💰 {content['price']} ብር"
            )
    
    await query.edit_message_text(
        get_text('am', 'admin.approved', title=content['title'])
    )

async def admin_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.id):
        await query.edit_message_text("⛔ አስተዳዳሪ አይደለህም!")
        return
    
    content_id = int(query.data.split('_')[2])
    content = get_content(content_id)
    
    if not content:
        await query.edit_message_text("❌ ይዘቱ አልተገኘም")
        return
    
    update_content_status(content_id, 'rejected')
    
    # ደራሲውን ማሳወቅ
    author = get_author_by_id(content['author_id'])
    if author:
        author_user = get_user(author['user_id'])
        if author_user:
            await context.bot.send_message(
                chat_id=author_user['telegram_id'],
                text=f"😔 ይቅርታ፣ ይዘትህ '{content['title']}' ተሰርዟል።\n\n"
                     f"ምክንያት: የጥራት ደረጃዎችን አላሟላም"
            )
    
    await query.edit_message_text(
        get_text('am', 'admin.rejected', title=content['title'])
    )

# ============================================
# ደራሲ ማረጋገጫ
# ============================================

async def admin_verify_authors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.id):
        await query.edit_message_text("⛔ አስተዳዳሪ አይደለህም!")
        return
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    authors = get_all_authors()
    unverified = [a for a in authors if not a.get('is_verified', 0)]
    
    if not unverified:
        await query.edit_message_text("✅ ሁሉም ደራሲዎች ተረጋግጠዋል!")
        return
    
    message = "✅ *ያልተረጋገጡ ደራሲዎች* / *Unverified Authors*\n\n"
    keyboard = []
    
    for author in unverified[:10]:
        user = get_user(author['user_id'])
        if user:
            message += f"• *{user.get('full_name', 'ያልታወቀ')}*\n"
            message += f"  📱 @{user.get('username', 'የለም')}\n"
            message += f"  📊 ሽያጭ: {author.get('total_sales', 0)}\n\n"
            keyboard.append([
                InlineKeyboardButton(
                    f"✅ {user.get('full_name', '')[:20]}",
                    callback_data=f"admin_verify_author_{author['id']}"
                )
            ])
    
    if len(unverified) > 10:
        message += f"\n... እና {len(unverified) - 10} ተጨማሪ"
    
    keyboard.append([InlineKeyboardButton("🔙 Back / ተመለስ", callback_data="admin_back")])
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def admin_verify_author(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.id):
        await query.edit_message_text("⛔ አስተዳዳሪ አይደለህም!")
        return
    
    author_id = int(query.data.split('_')[3])
    author = get_author_by_id(author_id)
    
    if author:
        update_author_level(author_id, 'Verified')
        user = get_user(author['user_id'])
        if user:
            await context.bot.send_message(
                chat_id=user['telegram_id'],
                text="✅ እንኳን ደስ አለህ!\n"
                     "የደራሲ ማረጋገጫህ ተፅድቋል!"
            )
        await query.edit_message_text("✅ ደራሲው ተረጋግጧል!")

# ============================================
# ክርክር አፈታት
# ============================================

async def admin_disputes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.id):
        await query.edit_message_text("⛔ አስተዳዳሪ አይደለህም!")
        return
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    reports = get_reports(status='pending')
    
    if not reports:
        await query.edit_message_text("✅ ምንም ክርክር የለም!")
        return
    
    message = "⚠️ *በመጠባበቅ ላይ ያሉ ክርክሮች* / *Pending Disputes*\n\n"
    keyboard = []
    
    for report in reports[:10]:
        content = get_content(report['content_id'])
        if content:
            message += f"📖 {content['title']}\n"
            message += f"📝 {report.get('reason', 'ምንም ምክንያት')[:50]}...\n\n"
            keyboard.append([
                InlineKeyboardButton(
                    f"🔍 {content['title'][:25]}...",
                    callback_data=f"admin_dispute_{report['id']}"
                )
            ])
    
    if len(reports) > 10:
        message += f"\n... እና {len(reports) - 10} ተጨማሪ"
    
    keyboard.append([InlineKeyboardButton("🔙 Back / ተመለስ", callback_data="admin_back")])
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def admin_resolve_dispute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.id):
        await query.edit_message_text("⛔ አስተዳዳሪ አይደለህም!")
        return
    
    report_id = int(query.data.split('_')[2])
    report = get_report(report_id)
    
    if report:
        update_report_status(report_id, 'resolved')
        content = get_content(report['content_id'])
        if content:
            await query.edit_message_text(
                f"✅ ክርክሩ ተፈትቷል!\n"
                f"📖 {content['title']}"
            )
    else:
        await query.edit_message_text("❌ ሪፖርቱ አልተገኘም")

# ============================================
# ማስታወቂያ
# ============================================

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.id):
        await query.edit_message_text("⛔ አስተዳዳሪ አይደለህም!")
        return
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    await query.edit_message_text(
        get_text(lang, 'admin.broadcast') + "\n\n"
        "ለመሰረዝ /cancel ይጠቀሙ"
    )
    context.user_data['broadcast'] = True

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('broadcast'):
        return
    
    if not is_admin(update.effective_user.id):
        return
    
    message = update.message.text
    users = get_all_users()
    
    sent = 0
    failed = 0
    
    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user['telegram_id'],
                text=f"📢 *ማስታወቂያ / Announcement*\n\n{message}",
                parse_mode='Markdown'
            )
            sent += 1
        except:
            failed += 1
    
    await update.message.reply_text(
        f"✅ ማስታወቂያ ተልኳል!\n"
        f"📤 የተላከ: {sent}\n"
        f"❌ አልተላከ: {failed}"
    )
    context.user_data['broadcast'] = False

async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ ተሰርዟል / Cancelled")

# ============================================
# ትንታኔዎች
# ============================================

async def admin_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.id):
        await query.edit_message_text("⛔ አስተዳዳሪ አይደለህም!")
        return
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    all_content = get_all_content()
    all_purchases = get_all_purchases()
    
    # በምድብ ሽያጭ
    category_sales = {}
    for content in all_content:
        cat = content.get('category', 'አልተመደበም')
        category_sales[cat] = category_sales.get(cat, 0) + content.get('total_sales', 0)
    
    data = "*በምድብ ሽያጮች* / *Sales by Category*\n"
    for cat, sales in sorted(category_sales.items(), key=lambda x: x[1], reverse=True)[:10]:
        data += f"• {cat}: {sales} ሽያጮች\n"
    
    # ከፍተኛ ሽያጭ ያላቸው
    top_content = sorted(all_content, key=lambda x: x.get('total_sales', 0), reverse=True)[:5]
    data += "\n*🏆 ከፍተኛ ሽያጭ ያላቸው* / *Top Content*\n"
    for idx, content in enumerate(top_content, 1):
        if content.get('total_sales', 0) > 0:
            data += f"{idx}. {content['title']}: {content['total_sales']} ሽያጮች\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Back / ተመለስ", callback_data="admin_back")]]
    
    await query.edit_message_text(
        "📈 *የመድረክ ትንታኔዎች* / *Platform Analytics*\n\n" + data,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ============================================
# ስርዓት ሁኔታ
# ============================================

async def admin_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(update.effective_user.id):
        await query.edit_message_text("⛔ አስተዳዳሪ አይደለህም!")
        return
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    import os
    db_size = os.path.getsize('marketplace.db') / (1024 * 1024) if os.path.exists('marketplace.db') else 0
    
    keyboard = [[InlineKeyboardButton("🔄 Refresh / አድስ", callback_data="admin_system")],
                [InlineKeyboardButton("🔙 Back / ተመለስ", callback_data="admin_back")]]
    
    await query.edit_message_text(
        get_text(lang, 'system.status',
            size=round(db_size, 2),
            time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ============================================
# ተመላሽ
# ============================================

async def admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await admin_start(update, context)

# ============================================
# ዋና ተግባር
# ============================================

def main():
    init_db()
    logger.info("✅ የውሂብ ጎታ ተዘጋጅቷል")
    
    application = Application.builder().token(ADMIN_BOT_TOKEN).build()
    
    # ትዕዛዞች
    application.add_handler(CommandHandler("start", admin_start))
    application.add_handler(CommandHandler("cancel", admin_cancel))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(admin_dashboard, pattern="^admin_dashboard$"))
    application.add_handler(CallbackQueryHandler(admin_pending, pattern="^admin_pending$"))
    application.add_handler(CallbackQueryHandler(admin_review, pattern="^admin_review_"))
    application.add_handler(CallbackQueryHandler(admin_approve, pattern="^admin_approve_"))
    application.add_handler(CallbackQueryHandler(admin_reject, pattern="^admin_reject_"))
    application.add_handler(CallbackQueryHandler(admin_verify_authors, pattern="^admin_verify_authors$"))
    application.add_handler(CallbackQueryHandler(admin_verify_author, pattern="^admin_verify_author_"))
    application.add_handler(CallbackQueryHandler(admin_disputes, pattern="^admin_disputes$"))
    application.add_handler(CallbackQueryHandler(admin_resolve_dispute, pattern="^admin_dispute_"))
    application.add_handler(CallbackQueryHandler(admin_broadcast, pattern="^admin_broadcast$"))
    application.add_handler(CallbackQueryHandler(admin_analytics, pattern="^admin_analytics$"))
    application.add_handler(CallbackQueryHandler(admin_system, pattern="^admin_system$"))
    application.add_handler(CallbackQueryHandler(admin_back, pattern="^admin_back$"))
    
    # መልእክት አስተናጋጅ
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast))
    
    logger.info("🚀 የአስተዳዳሪ ቦት በስራ ላይ ነው...")
    application.run_polling()

if __name__ == '__main__':
    main()
