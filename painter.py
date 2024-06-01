import matplotlib.pyplot as plt
import sunpy.map
import astropy.units as u
from astropy.coordinates import SkyCoord
import requests
import re
import os

def getSecondFilename(directory):
    files_and_dirs = sorted(os.listdir(directory))
    files = [f for f in files_and_dirs if os.path.isfile(os.path.join(directory, f))]
    if len(files) > 1:
        return files[1]  
    else:
        return None
    
def DeleFilesInFolder(folder_path):
    if not os.path.exists(folder_path):
        print("Folder not exist: ", folder_path)
        return

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  
                print(f"File deleted: {file_path}")
            elif os.path.isdir(file_path):
                os.rmdir(file_path)  
                print(f"Empty folder deleted: {file_path}")
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def fitsDownloader():
    url = "https://www.sidc.be/EUI/data/lastDayFSI/"
    response = requests.get(url)
    fits_dict = []

    if response.status_code != 200:
        print('Request Error: status code ' + str(response.status_code))
        return fits_dict
    else:
        fits_list = re.findall(r'href="([^"]+\.fits)"', response.text)
        if len(fits_list) > 1:
            if fits_list[1] == getSecondFilename('fits'):
                return fits_dict
        print('Number of Images: ' + str(len(fits_list)))
        DeleFilesInFolder('Images')
        DeleFilesInFolder('fits')
        for fits_file in fits_list:
            url_fits = url + fits_file
            save_path = './fits/' + fits_file
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
    
fits_list = fitsDownloader()
if fits_list:
    for fits_file in fits_list:
        fits_path = './fits/' + fits_file
        img_name = './Images/' + fits_file[:-5] + '.png'
        saveMap(fits_path, file_name=img_name)
    print('All Done!')
else:
    print('Empty file list')



