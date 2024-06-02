import os
from datetime import datetime

image_save_path = './Images'
html_save_path = './'

def generate_html(images_folder):
    current_utc_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')

    html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Latest SoloEUI Images</title>
    <style>
        body {{
            text-align: center; /* 居中页面的所有内容 */
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}
        .gallery {{
            display: flex; /* 使用Flexbox进行布局 */
            flex-wrap: wrap; /* 允许内容换行 */
            justify-content: center; /* 水平居中Flex项 */
        }}
        .img-container {{
            margin: 10px;
            width: calc(100% - 20px); /* 每个容器占据整行宽度，减去间距 */
            display: flex; /* 让图片在容器内并排 */
            justify-content: center; /* 将容器中的内容居中显示 */
        }}
        img {{
            width: 30%; /* 图片宽度为容器的30% */
            height: auto; /* 图片高度自动调整 */
            margin: 0 10px; /* 图片之间和容器边缘的间距 */
        }}
        p:last-of-type {{
            width: 60%;
            margin: 0 auto; /* 上下无间距，左右自动调整以居中 */
            text-align: left;
        }}
    </style>
</head>
<body>
    <h1>Latest Images of Solar Orbiter's Extreme Ultraviolet Imager (EUI)</h1>
    <p>Generated at {current_utc_time}</p>
    <a href="https://www.sidc.be/EUI/data-analysis" target="_blank">Data Source</a> &nbsp; &nbsp; <a href="https://github.com/CosmosView/SoloEUI" target="_blank">Project Home</a>
    
    <div class="gallery">
'''

    count = 0
    for image_name in sorted(os.listdir(images_folder)):
        html_image_path = os.path.relpath(images_folder, html_save_path)
        if image_name.endswith('.png'):
            if count % 2 == 0:
                if count > 0:
                    html_content += '</div>'
                html_content += '<div class="img-container">'
            html_content += f'<img src="{html_image_path}/{image_name}" alt="{image_name}">'
            count += 1


    html_content += '</div>'

    html_content += '''
    </div>
    <br>
    <p><b>Note:</b>The 0° latitude and 0°/180° longitude lines in the Stonyhurst heliographic coordinates were plotted on the images to help determine the positional relationship between the satellite and the Earth. Details of the satellite's location can be found <a href="https://www.cosmos.esa.int/web/solar-orbiter/where-is-solar-orbiter" target="_blank">here</a>. <b>Data are uncalibrated and should be used with caution.</b> </p>
    <br><br>
</body>
</html>
    '''

    with open(html_save_path + 'index.html', 'w') as file:
        file.write(html_content)

    print(f"HTML file {html_save_path}'index.html' has been created.")

generate_html(image_save_path)
