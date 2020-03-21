def get_extra_data(urls):
    import json
    import requests
    import re
    import multiprocessing as multi
    from bs4 import BeautifulSoup
    from user_agent import generate_user_agent
    from datetime import datetime
    from random import randint
    
    err_numbers = randint(1,100000)
    
    SITE = 'https://www.tripadvisor.com'
    SUBCATEGORIES = ['Food', 'Service', 'Value', 'Atmosphere']
    COMMENTS_CAT = ['Excellent', 'Very good', 'Average', 'Poor', 'Terrible']
    DETAILS = ['PRICE RANGE', 'CUISINES', 'SPECIAL DIETS', 'MEALS', 'FEATURES']
    AWARDS = ['AWARD', 'YEARS']
    
    results = []
    header_site = urls[0][1:-5]
    
    for url in urls:
    
        try:
            headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}
            response = requests.get(SITE + url, headers=headers)
        except Exception as err:
            print('Caught exception')
            print(err)
            with open('error_' + datetime.now().strftime('%Y%m%d-%H%M%S') +'.txt', 'w') as f:
                text = 'for url ' + url + '\n'
                f.write(text + str(err))
            results.append({'URL_TA': url, 'website': False, 'subratings': {}, 'comments': {}, 'adds_info': {}, 'awards': {}, 'comments_count': 0})
            continue
            
        try:

            page = BeautifulSoup(response.text, 'html.parser')

            # есть сайт или нет
            website = page.find(class_='detail ui_link level_1')
            #print(website)
            # здесь разная инфа
            adds_info = page.find_all('div', attrs={'class': 'restaurants-detail-overview-cards-DetailsSectionOverviewCard__detailsSummary--evhlS'})
            #print(adds_info)
            # подрейтинги
            subratings = page.find_all('div', attrs={'class': 'restaurants-detail-overview-cards-RatingsOverviewCard__ratingQuestionRow--5nPGK'})
            #print(subratings)
            # сколько оставили комментариев каждой категории
            comments = page.find_all('div', attrs={'class': 'choices', 'data-name': 'ta_rating', 'data-param': 'trating'})
            #print(comments)

            # обрабатываем инфу о сайте
            if website is None:
                website = 0
            elif website.text.lower() == 'website':
                website = 1

            # обрабатываем подрейтинги
            sbrs = dict.fromkeys(SUBCATEGORIES, 0)

            if len(subratings) != 0:     
                for element in subratings:
                    k = element.find('span', attrs={'class': 'restaurants-detail-overview-cards-RatingsOverviewCard__ratingText--1P1Lq'}).text
                    v = element.find('span', attrs={'class': 'restaurants-detail-overview-cards-RatingsOverviewCard__ratingBubbles--1kQYC'}).span['class'][1][-2:]
                    v = int(v) / 10
                    sbrs[k] = v

            # обрабатываем количество комментариев
            comms = dict.fromkeys(COMMENTS_CAT, 0)

            if len(comments) != 0:
                tags = [t.text for t in comments[0].find_all('label', attrs={'class': 'row_label label'})]
                scores = [s.text for s in comments[0].find_all('span', attrs={'class': 'row_num is-shown-at-tablet'})]

                for tag, score in zip(tags, scores):
                    comms[tag] = score

            # обрабатываем дополнительную инфу
            adds = dict.fromkeys(DETAILS, None)

            if len(adds_info) != 0:
                temp = adds_info[0].find_all('div', attrs={'class': 'restaurants-detail-overview-cards-DetailsSectionOverviewCard__categoryTitle--2RJP_'})
                tags = [t.text.upper() for t in temp]
                values = [v.next_sibling.text for v in temp]

                for tag, value in zip(tags, values):
                    adds[tag] = value
                    
            meals = page.find_all('div', text='Meals')
            if len(meals) != 0:
                adds['MEALS'] = meals[0].next_sibling.text
                
            features = page.find_all('div', text='FEATURES')
            if len(features) != 0:
                adds['FEATURES'] = features[0].next_sibling.text
                    
            # обрабатываем общее количество комментов
            comms_count = page.find('span', attrs={'class': 'reviews_header_count'})
            if comms_count is not None:
                cc = comms_count.text[1:-1].replace(',', '')
                #comms_count = int(cc)
                comms_count = cc
            else:
                comms_count = 0
                
            # обрабатываем награды если есть
            awds = dict.fromkeys(AWARDS, None)
            
            awards = page.find_all('div', attrs={'class': 'restaurants-detail-overview-cards-RatingsOverviewCard__award--31yzt'})
            if len(awards) != 0:
                temp = awards[0].find('span', class_='restaurants-detail-overview-cards-RatingsOverviewCard__awardText--1Kl1_')
                
                if temp is not None:
                    awds['AWARD'] = temp.text
                    years = temp.next_sibling
                    
                    if years is not None:
                        awds['YEARS'] = years.text
                    
            # добавляем в список
            results.append({'URL_TA': url, 'website': website, 'subratings': sbrs, 'comments': comms, 'adds_info': adds, 'awards': awds, 'comments_count': comms_count})
        
        except Exception as err:
            #print('Caught exception')
            #print(err)
            with open('error_' + datetime.now().strftime('%Y%m%d-%H%M%S') +'.txt', 'w') as f:
                text = 'for url ' + url + '\n'
                f.write(text + str(err))
            results.append({'URL_TA': url, 'website': False, 'subratings': {}, 'comments': {}, 'adds_info': {}, 'awards': {}, 'comments_count': 0})
            continue
    
    #file_name = multi.current_process().name+'.txt'
    file_name = header_site + '.json'
    with open(file_name, 'w') as f:
        json.dump(results, f)
    #return results