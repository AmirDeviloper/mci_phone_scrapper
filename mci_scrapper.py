import time
import requests
import jdatetime
import pandas as pd
from datetime import datetime
import os
from phone_checker import PhoneNumberEvaluator

def gregorian_to_jalali(datetime_str: str):
    if not datetime_str:
        return None
    date_str = datetime_str.split('T')[0]
    g_date = datetime.strptime(date_str, "%Y-%m-%d")
    j_date = jdatetime.date.fromgregorian(date=g_date)
    return j_date.strftime("%Y/%m/%d")


def get_info_from_mci_ir(output_path: str):
    url = "https://shop.mci.ir/api/search/v1/products"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://shop.mci.ir/products/3/sim-card?page=0",
        "platform": "WEB"
    }

    params = {
        "category": 3,
        "size": 16
    }

    title_map = {
        "نوع دسته بندی": "الگوی شماره",
        "نوع فروش": "نوع سیم‌کارت",
        "نوع خط": "دائمی یا اعتباری"
    }

    reverse_map = {v: k for k, v in title_map.items()}

    extracted_data = []
    batch_start_page = 0

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for page in range(0, 625):
        params["page"] = page

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        products = data.get("products", [])

        if not products:
            print(f"page {page} empty.")
            break

        for product in products:
            product_info = {
                "شماره": product.get("name"),
                "وضعیت خرید": product.get("productStatus"),
                "قیمت با مالیات": product.get("priceWithTax"),
                "زمان درج": gregorian_to_jalali(product.get("createdOn")),
                **{k: None for k in title_map}
            }

            for attr in product.get("attributes", []):
                key = reverse_map.get(attr.get("title"))
                if key:
                    product_info[key] = (
                        attr.get("attributeValueVms", [{}])[0].get("displayText")
                    )

            extracted_data.append(product_info)

        print(f"page {page} readed.")

        if (page + 1) % 50 == 0:
            df = pd.DataFrame(extracted_data)
            filename = fr"{output_path}\sim_cards_page_{batch_start_page}_to_{page}.xlsx"
            df.to_excel(filename, index=False)
            print(f"file saved: {filename}")

            extracted_data.clear()
            batch_start_page = page + 1

        time.sleep(1)


    if extracted_data:
        df = pd.DataFrame(extracted_data)
        filename = fr"{output_path}\sim_cards_page_{batch_start_page}_to_last.xlsx"
        df.to_excel(filename, index=False)
        print(f"final_file_saved: {filename}")



def merge_excel_folder(folder_path):
    all_data = []

    excel_files = [f for f in os.listdir(folder_path) if f.endswith((".xlsx", ".xls"))]

    if not excel_files:
        print("no excel file found.")
        return

    for file in excel_files:
        file_path = os.path.join(folder_path, file)
        try:
            df = pd.read_excel(file_path, dtype=str)
            
            all_data.append(df)
            print(f"file {file} readed.")
        except Exception as e:
            print(f"error while reading {file}: {e}")

    if all_data:
        merged_df = pd.concat(all_data, ignore_index=True, sort=False)
        print(f"all files merged.")
        return merged_df
    else:
        print("there is no data for merge.")
        return None


folder_path = "extracted_files"
get_info_from_mci_ir(folder_path)
merged_df = merge_excel_folder(folder_path)
evaluator = PhoneNumberEvaluator()
scores_df = evaluator.evaluate_score_list(list(merged_df['شماره']))
result_df = merged_df.merge(scores_df, on='شماره')
merged_result = 'simcards_score_final.xlsx'
result_df = result_df.sort_values(by="امتیاز", ascending=False)

result_df.to_excel(merged_result, index=False)
print(f"final excel file saved: {merged_result}")
