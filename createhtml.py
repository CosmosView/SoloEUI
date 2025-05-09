import os
import re
from datetime import datetime

image_save_path = './public/Images'
html_save_path = './public/'

def generate_html(images_folder):
    current_utc_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    
    # 获取并分类所有PNG图片
    images_174 = []
    images_304 = []
    
    for image_name in os.listdir(images_folder):
        if image_name.endswith('.png'):
            if 'fsi174' in image_name:
                images_174.append(image_name)
            elif 'fsi304' in image_name:
                images_304.append(image_name)
    
    # 按照时间正序排序（较早的在前面）
    images_174.sort()
    images_304.sort()
    
    # 生成JavaScript数组
    images_174_js = ",\n                ".join([f'"{img}"' for img in images_174])
    images_304_js = ",\n                ".join([f'"{img}"' for img in images_304])
    
    # 计算图片路径相对于HTML文件的相对路径
    html_image_path = os.path.relpath(images_folder, html_save_path)
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Latest SoloEUI Images</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            text-align: center;
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 15px;
        }}
        h1 {{
            font-size: 24px;
            margin-top: 20px;
        }}
        @media (max-width: 768px) {{
            h1 {{
                font-size: 20px;
            }}
        }}
        .controls {{
            margin: 20px 0;
        }}
        .wavelength-selector {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .wavelength-btn {{
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
        @media (max-width: 480px) {{
            .wavelength-btn {{
                padding: 8px 15px;
                font-size: 14px;
            }}
        }}
        .wavelength-btn.active {{
            background-color: #4CAF50;
            color: white;
        }}
        .image-container {{
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            position: relative;
        }}
        .image-display {{
            width: 100%;
            height: auto;
            margin-bottom: 10px;
        }}
        .slider-container {{
            width: 60%;
            margin: 20px auto;
        }}
        #image-slider {{
            width: 100%;
        }}
        .image-info {{
            margin-top: 10px;
            font-size: 14px;
            color: #333;
        }}
        .note-section {{
            width: 60%;
            margin: 20px auto;
            text-align: left;
        }}
        @media (max-width: 768px) {{
            .slider-container,
            .note-section {{
                width: 90%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Latest Images of Solar Orbiter's Extreme Ultraviolet Imager (EUI)</h1>
        <p>Generated at {current_utc_time}</p>
        <a href="https://www.sidc.be/EUI/data-analysis" target="_blank">Data Source</a> &nbsp; &nbsp; <a href="https://github.com/CosmosView/SoloEUI" target="_blank">Project Home</a>
       
        <div class="controls">
            <div class="wavelength-selector">
                <button class="wavelength-btn active" data-wavelength="174">174 Å</button>
                <button class="wavelength-btn" data-wavelength="304">304 Å</button>
            </div>
            
            <div class="image-container">
                <img id="current-image" class="image-display" src="" alt="EUI Image">
                <div class="image-info" id="image-info">Loading image information...</div>
            </div>
            
            <div class="slider-container">
                <input type="range" min="0" max="100" value="100" class="slider" id="image-slider">
            </div>
        </div>
        
        <br>
        <div class="note-section">
            <p><b>Note:</b> The 0&deg; latitude and 0&deg;/180&deg; longitude lines in the Stonyhurst heliographic coordinates were plotted on the images to help determine the positional relationship between the satellite and the Earth. Details of the satellite's location can be found <a href="https://www.cosmos.esa.int/web/solar-orbiter/where-is-solar-orbiter" target="_blank">here</a>. <b>Data are uncalibrated and should be used with caution.</b></p>
        </div>
        <br>
    </div>

    <script>
        // 图片数据
        const images = {{
            "174": [
                {images_174_js}
            ],
            "304": [
                {images_304_js}
            ]
        }};
        
        let currentWavelength = "174";
        let currentImageIndex = 0;
        const imagePath = "{html_image_path}/";
        
        // 初始化函数
        function init() {{
            updateSlider();
            updateImage();
            setupEventListeners();
        }}
        
        // 更新滑块
        function updateSlider() {{
            const slider = document.getElementById('image-slider');
            const imageCount = images[currentWavelength].length;
            
            if (imageCount > 0) {{
                slider.max = imageCount - 1;
                slider.value = imageCount - 1; // 默认显示最新的图片（最后一张）
                currentImageIndex = imageCount - 1;
            }} else {{
                slider.max = 0;
                slider.value = 0;
            }}
        }}
        
        // 更新显示的图片
        function updateImage() {{
            const imageElement = document.getElementById('current-image');
            const infoElement = document.getElementById('image-info');
            
            if (images[currentWavelength].length > 0) {{
                const imageName = images[currentWavelength][currentImageIndex];
                imageElement.src = `${{imagePath}}${{imageName}}`;
                imageElement.alt = imageName;
                
                // 从文件名中提取时间信息
                const timeMatch = imageName.match(/(\\d{{8}}T\\d{{6}})/);
                if (timeMatch) {{
                    const timeStr = timeMatch[1];
                    const year = timeStr.substr(0, 4);
                    const month = timeStr.substr(4, 2);
                    const day = timeStr.substr(6, 2);
                    const hour = timeStr.substr(9, 2);
                    const minute = timeStr.substr(11, 2);
                    const second = timeStr.substr(13, 2);
                    
                    infoElement.textContent = `${{year}}-${{month}}-${{day}} ${{hour}}:${{minute}}:${{second}} UTC | Wavelength: ${{currentWavelength}} Å`;
                }} else {{
                    infoElement.textContent = `Wavelength: ${{currentWavelength}} Å | ${{imageName}}`;
                }}
            }} else {{
                imageElement.src = "";
                imageElement.alt = "No images available";
                infoElement.textContent = `No images available for ${{currentWavelength}} Å`;
            }}
        }}
        
        // 设置事件监听器
        function setupEventListeners() {{
            // 波长选择按钮
            const wavelengthButtons = document.querySelectorAll('.wavelength-btn');
            wavelengthButtons.forEach(button => {{
                button.addEventListener('click', function() {{
                    wavelengthButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                    
                    currentWavelength = this.getAttribute('data-wavelength');
                    updateSlider();
                    updateImage();
                }});
            }});
            
            // 滑块事件
            const slider = document.getElementById('image-slider');
            slider.addEventListener('input', function() {{
                currentImageIndex = parseInt(this.value);
                updateImage();
            }});
        }}
        
        // 页面加载完成后初始化
        window.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>'''

    with open(os.path.join(html_save_path, 'index.html'), 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f"HTML file {os.path.join(html_save_path, 'index.html')} has been created.")

# 执行函数
generate_html(image_save_path)