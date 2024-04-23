from bs4 import BeautifulSoup
import requests
import re
import time
import random
import matplotlib.pyplot as plt
import numpy as np


def get_name(session, url, soup):    #get name of pitcher
    meta_data = soup.find('div', {'id': 'meta'})
    name =  meta_data.find('span').text
    
    return name

def get_team(session, url, soup):    #get name of team pitcher is on
   meta_data = soup.find('div', {'id': 'meta'})
   team = meta_data.find('a').text
   
   return team
   
def get_era(session, url, soup):    #get era of pitcher
    table = soup.find('div', {'id': 'all_pitching_standard'})
    table_foot = table.find('tfoot')

    era = float(table_foot.find('td', {'data-stat': 'earned_run_avg'}).text)
    
    return era

def get_whip(session, url, soup):    #get whip of pitcher
    table = soup.find('div', {'id': 'all_pitching_standard'})
    table_foot = table.find('tfoot')

    whip = float(table_foot.find('td', {'data-stat': 'whip'}).text)
    
    return whip

def get_fip(session, url, soup):    #get fip of pitcher
    table = soup.find('div', {'id': 'all_pitching_standard'})
    table_foot = table.find('tfoot')
    fip = float(table_foot.find('td', {'data-stat': 'fip'}).text)

    return fip

def get_so_rate(session, url, soup):    #get strikeout rate of pitcher
    table = soup.find('div', {'id': 'all_pitching_standard'})
    table_foot = table.find('tfoot')

    so = float(table_foot.find('td', {'data-stat': 'SO'}).text)
    bf = float(table_foot.find('td', {'data-stat': 'batters_faced'}).text)
    #caluclate strikeout rate given total strikeouts and total batters faced 
    so_rate = so/bf

    return so_rate

def get_wl_rate(session, url, soup):    #get win loss rate of pitcher
    table = soup.find('div', {'id': 'all_pitching_standard'})
    table_foot = table.find('tfoot')
    
    wins = float(table_foot.find('td', {'data-stat': 'W'}).text)
    losses = float(table_foot.find('td', {'data-stat': 'L'}).text)
    try:
        wl_rate = wins / (wins + losses)
    except ZeroDivisionError:
        wl_rate = 0

    return wl_rate

def pitcher_data():    #creates dictionary where each name is indexed with the corresponding data
    with requests.Session() as session:
        response = session.get('https://www.baseball-reference.com/previews/')
        soup = BeautifulSoup(response.text, 'html.parser')
        games = soup.find_all('div', {'class': 'game_summary nohover'})
        
        #initalize array for pitcher urls
        pitcher_urls = []
        
        for game in games:    #get each pitcher's url for every team playing today
            previews = game.find_all('a', href=True)
            if len(previews) >= 4:    #away pitcher url is indexed 3rd on the preview
                away_pitcher_url = re.search(r'href="([^"]*)"', str(previews[3])).group(1)
                away_pitcher_url = away_pitcher_url[:-6] + '-pitch.shtml'
                pitcher_urls.append(away_pitcher_url)
            if len(previews) >= 5:    #home pitcher url is indexed 4th on the preview
                home_pitcher_url = re.search(r'href="([^"]*)"', str(previews[4])).group(1)
                home_pitcher_url = home_pitcher_url[:-6] + '-pitch.shtml'
                pitcher_urls.append(home_pitcher_url)
        
        #initalize dictionary for pitcher data
        pitcher_dict = {}
        
        for url in pitcher_urls:
            if url:
                response = session.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                #get each name
                name = get_name(session, url, soup)
                
                #gets each data point
                team = get_team(session, url, soup)
                era = get_era(session, url, soup)
                whip = get_whip(session, url, soup)
                fip = get_fip(session, url, soup)
                so_rate = get_so_rate(session, url, soup)
                wl_rate = get_wl_rate(session, url, soup)

                #store data in dictionary indexed by name
                pitcher_dict[name] = {
                    'team': team,
                    'era': era,
                    'whip': whip,
                    'fip': fip,
                    'so_rate': so_rate,
                    'wl_rate': wl_rate
                }
            
            else:    #-1 indicating that data for pitcher not found
                pitcher_data[-1] = {}
            
            #avoiding sending too many requests at once
            time.sleep(random.uniform(2.05, 2.2))

    return pitcher_dict 

def adj_era(era):
    if 2 < era <= 6:
        adj_era = 100 - (((era - 2.0) / (6 - 2.0)) * 100)
    elif 2 > era:
        adj_era = 100
    else:
        adj_era = 5
    return adj_era

def adj_whip(whip):
    if 0.9 < whip <= 1.45:
        adj_whip = 100 - (((whip - 0.9) / (1.45 - 0.9)) * 100)
    elif 0.9 > whip:
        adj_whip = 100
    else:
        adj_whip = 5
    return adj_whip

def adj_fip(fip):
    if 2.75 < fip <= 5:
        adj_fip = 100 - (((fip - 2.75) / (5 - 2.75)) * 100)
    elif fip <= 2.75:
        adj_fip = 100
    else:
        adj_fip = 5
    return adj_fip

def adj_so_rate(so_rate):
    if 0.195 < so_rate <= 0.255:
        adj_so_rate = ((so_rate - 0.195) / (0.255 - 0.195)) * (100 - 5) + 5
    elif 0.255 <= so_rate:
        adj_so_rate = 100
    else:
        adj_so_rate = 5
    return adj_so_rate

def adj_wl_rate(wl_rate):
    if 0.4 < wl_rate <= 0.6:
        adj_wl_rate = ((wl_rate - 0.4) / (0.6 - 0.4)) * 100
    elif 0.6 <= wl_rate:
        adj_wl_rate = 100
    else:
        adj_wl_rate = 5
    return adj_wl_rate

def pitcher_profiles(pitcher_data):
    #number of variables
    num_vars = 5

    #create a 5-sided polygon (pentagon)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    #rotate the angles by 90 degrees counter-clockwise
    angles = [(angle + np.pi / 2) % (2 * np.pi) for angle in angles]

    #repeat the first angle to close the polygon
    angles += angles[:1]

    #variables for plotting
    text = ['ERA', 'WHIP', 'FIP', 'SO Rate', 'WL Rate']

    # Plotting
    pitchers = list(pitcher_data.keys())
    num_pitchers = len(pitchers)
    num_pairs = num_pitchers // 2  #number of pairs of pitchers

    for i in range(num_pairs):
        fig, axes = plt.subplots(1, 2, subplot_kw=dict(polar=True), figsize=(15, 7))
        fig.suptitle(f'{pitcher_data[pitchers[i*2]]["team"]} vs {pitcher_data[pitchers[i*2+1]]["team"]}', color='white', size=20)
        
        for j, ax in enumerate(axes.flat):
            pitcher = pitchers[i*2 + j]
            data = pitcher_data[pitcher]
            
            values = [(data['era']), data['whip'], data['fip'], data['so_rate'], data['wl_rate']]
            adj_values = [adj_era(data['era']), adj_whip(data['whip']), adj_fip(data['fip']), 
                        adj_so_rate(data['so_rate']), adj_wl_rate(data['wl_rate'])]
            
            #coloring the background
            fig.patch.set_facecolor('#1d1f21')
            ax.set_facecolor('#1d1f21')
            #making data point labels
            ax.spines['polar'].set_visible(False)
            ax.set_xticks(angles[:-1])
            ticks = [f'{label}\n({value:.2f})' if i == 0 else f'{label}\n{value:.2f}' for i, (label, value) in enumerate(zip(text, values))]
            ax.set_xticklabels(ticks, color='white', size=14)
            
            ax.set_yticks([26, 52, 78, 104])    #inner circles in the radar
            ax.set_ylim(0, 104)    #sets radius of plot
            ax.set_yticklabels([])  #removes labels of inner circles

            ax.plot(angles, adj_values + [adj_values[0]], color='#61fa99')
            ax.fill(angles, adj_values + [adj_values[0]], color='#61fa99', alpha=0.25)

            ax.set_title(f'{pitcher}', color='white', size=18, pad=65)
            ax.tick_params(axis='x', pad=20)
       
        plt.tight_layout(pad=3)
        plt.show()

#call pitcher_data to fetch data
pitcher_data = pitcher_data()

#creates pitcher profiles using the fetched data
pitcher_profiles(pitcher_data)