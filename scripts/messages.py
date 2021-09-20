import scripts.markup as mk

greeting = '''Приветствую! 👋🏻  
️
Я могу тебе помочь Вам с отслеживанием изменений курсов тикеров представленных на coinmarketcap.com

<b>Чтобы добавить тикер, выберите интересующий, либо введите свой:</b>'''

choose_ticker = 'Чтобы добавить тикер, выберите интересующий, либо введите свой:'

choose_ticker_manual = 'Отправьте мне текстовым сообщением назвение тикера'

ticker_chosen = 'Вы выбрали тикер <b>{0}</b>. Отправьте мне текстовым сообщением процент на который курс должен измениться чтобы я отправил уведомление'

ticker_not_exist = 'Тикер <b>{0}</b> не найден. Проверьте пожалуйста правильность ввода, и попробуйте еще раз'

percent_invalid = 'Вы ввели некорректное значение для процента. Проверьте пожалуйста правильность ввода, и попробуйте еще раз'

percent_too_little = 'Вы ввели слишком мальнькое значение для процента. Проверьте пожалуйста правильность ввода, и попробуйте еще раз'

choose_period = 'Вы выбрали процент <b>{0}%</b>. Выберите период времени, раз в который нужно проверять информацию'

period_invalid = 'Вы ввели некорректное значение для периода. Проверьте пожалуйста правильность ввода, и попробуйте еще раз'

choose_period_manual = 'Отправьте мне текстовым сообщением время периода в минутах'

ticker_added = 'Тикер <b>{0}</b> добавлен. Я буду проверять информацию каждые <b>{1} минут</b>, и отправлю вам уведомление когда курс тикера изменится на <b>{2}%</b> или больше. Вы можете просматривать тикер в разделе <b>«Мои тикеры»</b>'

your_tickers = 'Ваши тикеры'

no_tickers = 'Оу, у вас пока нет ни одного тикера, хотите добавить?'

cant_add_more_tickers = 'Вы не можете добавить больше 10-ти тикеров'

send_new_percent = 'Отправьте мне новый процент'

percent_updated = 'Процент на тикер <b>{0}</b> обновлен'

send_new_period = 'Выберите новый период'

choose_new_period_manual = 'Отправьте мне текстовым сообщением новое время периода в минутах'

period_updated = 'Период на тикер <b>{0}</b> обновлен'

ticker_notification_positive = '📈️ Курс <b>{0}</b> вырос на <b>+{1}%</b>, и составляет <b>{2} USD</b>'

ticker_notification_negative = '📉 Курс <b>{0}</b> упал на <b>-{1}%</b>, и составляет <b>{2} USD</b>'

permission_denied = '⛔️ У вас нет доступа к панели администратора'

send_me_user = 'Отправьте мне Telegram id пользователя, либо перешлите мне его сообщение чтобы посмотреть информацию'

user_id_invalid = 'Вы ввели некорректный Telegram id. Проверьте пожалуйста правильность ввода и попробуйте еще раз'

user_not_found = 'Пользователь с Telegram id <b>{0}</b> не найден в базе'
