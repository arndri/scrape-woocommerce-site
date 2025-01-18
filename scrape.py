import requests as r
from bs4 import BeautifulSoup
import re, os, random, time

def sanitize_folder_name(name):
    invalid_chars = r'[\/:*?"<>|]'
    return re.sub(invalid_chars, '_', name)

def download_image(image_url, folder_name):
    try:
        img_data = r.get(image_url)
        img_name = os.path.join(folder_name, image_url.split("/")[-1])
        with open(img_name, 'wb') as img_file:
            img_file.write(img_data.content)
        print(f"Downloaded {img_name}")
    except Exception as e:
        print(f"Error downloading {image_url}: {e}")

def get_product_data(page_num):
    url = f'{page_num}'
    req1 = r.get(url)
    soup = BeautifulSoup(req1.text, 'html.parser')

    products = soup.find_all("li", class_=lambda c: c and "type-product" in c)
    print(f"Found {len(products)} products on page {page_num}")
    
    for product in products:
        name = product.find('h2', class_='woocommerce-loop-product__title').text.strip()
        bdi_tags = product.find_all('bdi')
        discounted_price = None
        original_price = None
        if len(bdi_tags) == 2:
            original_price = bdi_tags[0].text.strip()
            discounted_price = bdi_tags[1].text.strip()
            price = f"Harga Asli: {original_price}, Harga Diskon: {discounted_price}"
        elif len(bdi_tags) == 1:
            price = f"Harga: {bdi_tags[0].text.strip()}"
        else:
            price = "Harga tidak tersedia"
        
        link = product.find('a', class_='woocommerce-LoopProduct-link')['href']
        print(f"{name} - {price}\n")
        print(f"Product Link: {link}")

        product_req = r.get(link)
        product_soup = BeautifulSoup(product_req.text, 'html.parser')
        img_tags = product_soup.find_all('div', class_='woocommerce-product-gallery__image')
        image_urls = [img.find('a')['href'] for img in img_tags if img.find('a')]

        folder_name = name.replace(" ", "_")
        folder_name = sanitize_folder_name(folder_name)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"Created folder: {folder_name}")

        for img_url in image_urls:
            download_image(img_url, folder_name)

        description = "Description not available"
        desc_div = product_soup.find('div', class_='elementor-widget-woocommerce-product-content')
        if desc_div:
            p_tag = desc_div.find('p') 
            if p_tag:
                description = p_tag.text.strip()
        
        desc_file_path = os.path.join(folder_name, f"Deskripsi_{folder_name}.txt")
        with open(desc_file_path, 'w', encoding='utf-8') as desc_file:
            if discounted_price: 
                desc_file.write(f"{name}\nHarga Asli: {original_price}\nHarga Diskon: {discounted_price}\n{description}")
            else: 
                desc_file.write(f"{name}\n{price}\n{description}")
        
        print(f"Saved description in: {desc_file_path}\n")
        delay = random.uniform(1,3)
        print(f"Sleeping in product for {delay:.2f} seconds...\n")
        time.sleep(delay)

for page_num in range(3, 5): 
    get_product_data(page_num)
    delay = random.uniform(3, 10)
    print(f"Sleeping in page {page_num} for {delay:.2f} seconds...\n")
    time.sleep(delay)
