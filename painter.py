import matplotlib.pyplot as plt
import sunpy.map
import astropy.units as u
from astropy.coordinates import SkyCoord
import requests
import re
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

image_save_path = './Images/'
fits_save_path = './fits/'
hour_for_update = 3

def decideUpdate(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    fits_link = soup.find('a', href=lambda href: href and 'fits' in href)
    if fits_link:
    
        details = fits_link.parent.get_text()
        
        last_modified_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', details)
        if last_modified_match:
            last_modified_time_str = last_modified_match.group(0)
            last_modified_time = datetime.strptime(last_modified_time_str, '%Y-%m-%d %H:%M')
            current_time = datetime.utcnow()
            time_difference = current_time - last_modified_time

            if time_difference < timedelta(hours=hour_for_update):
                return True
            else: 
                print('No update')
        else:
            print("No 'Last modified' timestamp found in the text.")
    else:
        print("No FITS file link found in the HTML content.")
    return False

def ifExists(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Directory created: {path}")
    else:
        print(f"Directory already exists: {path}")


def fitsDownloader():
    url = "https://www.sidc.be/EUI/data/lastDayFSI/"
    response = requests.get(url + '?C=M;O=D')
    fits_list = []

    if response.status_code != 200:
        print('Request Error: status code ' + str(response.status_code))
    else:
        if decideUpdate(response.text):
            fits_list = re.findall(r'href="([^"]+\.fits)"', response.text)
            if fits_list:
                print('Number of Images: ' + str(len(fits_list)))
                for fits_file in fits_list:
                    url_fits = url + fits_file
                    save_path = fits_save_path + fits_file
                    r = requests.get(url_fits, timeout=10)
                    with open(save_path, "wb") as f:
                        f.write(r.content)
    return fits_list
    

def saveMap(fits_file, file_name='save_fig.png', rotate=True, clean=False):
    map_data = sunpy.map.Map(fits_file)
    if rotate:
        map_data = map_data.rotate()

    sun_radius_pixels = map_data.rsun_obs
    radius = 1.3 * sun_radius_pixels

    top_right = SkyCoord(radius, radius, frame=map_data.coordinate_frame)
    bottom_left = SkyCoord(-radius, -radius, frame=map_data.coordinate_frame)

    map_data = map_data.submap(bottom_left, top_right=top_right)

    fig = plt.figure()

    if clean:
        map_data.plot(clip_interval=(1, 99.99)*u.percent)
        plt.axis('off')
    
    else:
        ax = fig.add_subplot(projection=map_data)
        map_data.plot(clip_interval=(1, 99.99)*u.percent)
        ax.grid(False)
        # map_data.draw_limb()
        grid_spacing = 180 * u.deg
        map_data.draw_grid(grid_spacing=grid_spacing)
    
    plt.savefig(file_name, dpi=150)
    
ifExists(image_save_path)
ifExists(fits_save_path)
fits_list = fitsDownloader()
if fits_list:
    for fits_file in fits_list:
        fits_path = fits_save_path + fits_file
        img_name = image_save_path + fits_file[:-5] + '.png'
        saveMap(fits_path, file_name=img_name)
    print('All Done!')
else:
    print('Empty file list')



