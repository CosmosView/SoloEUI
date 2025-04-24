import matplotlib.pyplot as plt
import sunpy.map
import astropy.units as u
from astropy.coordinates import SkyCoord
import requests
import re
import os
import shutil

publish_url = 'https://www.cosmosview.top/SoloEUI/'
fits_url = 'https://www.sidc.be/EUI/data/lastDayFSI/'
image_save_path = './public/Images/'
fits_save_path = './public/fits/'

def fileDownloader(url, save_path, timeout = 10):
    r = requests.get(url, timeout = timeout)
    with open(save_path, "wb") as f:
        f.write(r.content)

def getFitsList(fits_url):
    response = requests.get(fits_url)
    fits_list = []
    if response.status_code != 200:
        print('Error in requeseting data source: status code ' + str(response.status_code))
    else:
        fits_list = re.findall(r'href="([^"]+)\.fits"', response.text)
        fits_list = [item for item in fits_list if 'short' not in item.lower()]
        
        fits_list_174 = [item for item in fits_list if 'fsi174' in item]
        fits_list_304 = [item for item in fits_list if 'fsi304' in item]
        
        if len(fits_list_174) > 4:
            last_174 = fits_list_174[-1]
            remaining_174 = fits_list_174[:-1]
            
            interval_174 = len(remaining_174) // 3
            selected_174 = [remaining_174[i * interval_174] for i in range(3)]
            
            fits_list_174 = selected_174 + [last_174]
        
        if len(fits_list_304) > 4:
            last_304 = fits_list_304[-1]
            remaining_304 = fits_list_304[:-1]
            
            interval_304 = len(remaining_304) // 3
            selected_304 = [remaining_304[i * interval_304] for i in range(3)]
            
            fits_list_304 = selected_304 + [last_304]
        
        fits_list = fits_list_174 + fits_list_304
        
        print('Number of data source images: ' + str(len(fits_list)))
    # Format ['solo_L2_eui-fsi174-image_20240614T000045244_V00']
    return fits_list

def getExistImages(publish_url):
    response = requests.get(publish_url)
    images_list = []

    if response.status_code != 200:
        print('Error in requeseting published website: status code ' + str(response.status_code))
    else:
        # Format ['Images/solo_L2_eui-fsi174-image_20240614T000045244_V00.png']
        images_list = re.findall(r'\bsrc="([^"]+\.png)"', response.text)
        for image_path in images_list:
            fileDownloader(publish_url + image_path, image_save_path + image_path.replace('Images/', '')) 
        # Format ['solo_L2_eui-fsi174-image_20240614T000045244_V00']
        images_list = [path.replace('Images/', '').replace('.png', '') for path in images_list]

    return images_list


def ifExists(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Directory created: {path}")
    else:
        print(f"Directory already exists: {path}")

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
        ax.text(
            x=1,  # x为1表示轴的最右端
            y=0,  # y为0表示轴的最底部
            s='www.cosmosview.top/SoloEUI',  # 文本内容
            ha='right',  # 水平对齐方式为'right'
            va='bottom',  # 垂直对齐方式为'bottom'
            alpha=0.8,
            fontsize=8,  # 字体大小
            color='silver',  # 字体颜色
            family='monospace',  # 字体类型
            transform=ax.transAxes  # 使用轴的比例尺进行转换
        )

    plt.savefig(file_name, dpi=150)


# Create Path    
ifExists(image_save_path)
ifExists(fits_save_path)

# Get exist images list and data source list 
exist_images = getExistImages(publish_url)
data_source_fits = getFitsList(fits_url)
# Draw new images
for fits in data_source_fits:
    if fits in exist_images:
        print(f'Image already exist: {fits}')
    else:
        url = fits_url + fits + '.fits'
        fits_temp_path = fits_save_path + fits + '.fits'
        fileDownloader(url, fits_temp_path)
        png_save_path = image_save_path + fits + '.png'
        print(f'Drawing: {png_save_path}')
        saveMap(fits_temp_path, png_save_path)
        exist_images.append(fits)

# Remove source fits file
try:
    shutil.rmtree(fits_save_path)
    print("Fits Folder Deleted.")
except Exception as e:
    print(f"Error: {e}")


# Remove old images
if len(data_source_fits) > 3:
    for image in exist_images:
        if image not in data_source_fits:
            try:
                file_path = image_save_path + image + '.png'
                os.remove(file_path)
                print(f'Image deleted: {file_path}')
            except OSError as error:
                print(f"Error: {error.strerror}")

print('All Done!')

