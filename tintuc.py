import asyncio
import time
import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# CẤU HÌNH THÔNG TIN CỦA BẠN TẠI ĐÂY
TELEGRAM_TOKEN = '8876193993:AAG4U1gmYJRe4OLhAjZ1_pyEHumbop4UaWw'
CHANNEL_ID = '@wtuweg'  # Đã sửa đúng định dạng có dấu @

sent_links = set()  # Bộ nhớ tạm tránh gửi trùng bài trên Kênh

def get_latest_news():
    """Cào 5 tin tức mới nhất từ chuyên mục 24h của VnExpress"""
    # Dùng đường dẫn /tin-tuc-24h để đảm bảo cấu trúc thẻ HTML luôn chính xác
    url = "https://vnexpress.net"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    news_list = []
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('article', class_='item-news', limit=5)
        
        for article in articles:
            title_tag = article.find('h3', class_='title-news')
            if title_tag and title_tag.find('a'):
                title = title_tag.find('a').text.strip()
                link = title_tag.find('a')['href']
                
                desc_tag = article.find('p', class_='description')
                desc = desc_tag.text.strip() if desc_tag else ""
                
                news_list.append({'title': title, 'link': link, 'desc': desc})
    except Exception as e:
        print(f"Lỗi khi cào dữ liệu từ VnExpress: {e}")
        
    return news_list

async def tintuc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý khi người dùng gõ câu lệnh /tintuc"""
    print(f"[{time.strftime('%H:%M:%S')}] Có người gọi lệnh /tintuc")
    
    # Gửi thông báo đang xử lý để người dùng không phải chờ đợi
    waiting_message = await update.message.reply_text("⏳ Đang lấy tin tức mới nhất, vui lòng đợi trong giây lát...")
    
    news_items = get_latest_news()
    
    if not news_items:
        await waiting_message.edit_text("❌ Không thể lấy được tin tức lúc này. Vui lòng thử lại sau!")
        return

    # Xóa tin nhắn chờ và tiến hành gửi 5 bài báo
    await waiting_message.delete()
    
    for item in news_items:
        message = f"📰 *{item['title']}*\n\n{item['desc']}\n\n🔗 [Đọc chi tiết tại đây]({item['link']})"
        await update.message.reply_text(text=message, parse_mode='Markdown')
        await asyncio.sleep(1) # Nghỉ ngắn giữa các tin nhắn chống spam

async def auto_send_to_channel(bot: Bot):
    """Hàm chạy ngầm tự động gửi tin lên Kênh mỗi 2 giờ"""
    while True:
        print(f"[{time.strftime('%H:%M:%S')}] Đang quét tin tự động cho Kênh...")
        news_items = get_latest_news()
        
        for item in reversed(news_items):
            if item['link'] not in sent_links:
                message = f"📰 *{item['title']}*\n\n{item['desc']}\n\n🔗 [Đọc chi tiết tại đây]({item['link']})"
                try:
                    await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode='Markdown')
                    sent_links.add(item['link'])
                    print(f"-> Kênh đã đăng: {item['title']}")
                    await asyncio.sleep(3)
                except Exception as e:
                    print(f"Lỗi gửi bài lên Kênh: {e}")
                    
        # Nghỉ 2 tiếng (7200 giây) trước khi quét lần tiếp theo
        await asyncio.sleep(7200)

async def main():
    # Sử dụng bộ framework Application mới của python-telegram-bot
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Đăng ký câu lệnh /tintuc với hệ thống
    application.add_handler(CommandHandler("tintuc", tintuc_command))

    # Kích hoạt luồng chạy ngầm gửi tin tự động lên Kênh 2h/lần mà không làm kẹt lệnh /tintuc
    asyncio.create_task(auto_send_to_channel(application.bot))

    print("Bot đã sẵn sàng! Gõ /tintuc trong Telegram để test thử.")
    
    # Bắt đầu vòng lặp nhận lệnh liên tục từ người dùng
    await application.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply() # Chống lỗi xung đột vòng lặp trên một số môi trường máy tính
    asyncio.run(main())