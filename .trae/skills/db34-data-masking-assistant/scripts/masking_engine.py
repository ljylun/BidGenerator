import pandas as pd
import hashlib
from datetime import datetime, timedelta

def mask_phone(phone_number):
    """手机号脱敏：保留前三后四，中间用星号代替"""
    # 转换为字符串并去除可能的空格
    s = str(phone_number).strip()
    if len(s) < 7:
        return s
    if len(s) == 11 and s.isdigit():
        return s[:3] + '****' + s[7:]
    # 如果不是标准手机号，则遮盖中间部分
    mid = len(s) // 2
    return s[:max(1, mid-2)] + '****' + s[min(len(s)-1, mid+2):]

def hash_id(id_string):
    """对身份证号或敏感ID进行SHA256哈希处理"""
    if not isinstance(id_string, str):
        return id_string
    return hashlib.sha256(id_string.encode('utf-8')).hexdigest()

def offset_date(date_string, days=365):
    """日期偏移：将日期向前偏移指定天数"""
    if not isinstance(date_string, str):
        return date_string
    try:
        original_date = datetime.strptime(date_string, '%Y-%m-%d')
        offset = timedelta(days=days)
        new_date = original_date - offset
        return new_date.strftime('%Y-%m-%d')
    except ValueError:
        return date_string # Return as is if date format is incorrect

def generalize_income(income, bins=[0, 5000, 10000, 20000, 50000, 100000, float('inf')], labels=['<5k', '5k-10k', '10k-20k', '20k-50k', '50k-100k', '>100k']):
    """收入泛化：将具体收入值泛化为区间"""
    if not isinstance(income, (int, float)):
        return income
    for i in range(len(bins) - 1):
        if bins[i] <= income < bins[i+1]:
            return labels[i]
    return income

def truncate_address(address_string, level=2):
    """地址截断：根据级别截断地址信息，例如保留到市/区"""
    if not isinstance(address_string, str):
        return address_string
    parts = address_string.split('省') # Simple split for demonstration
    if len(parts) > 1:
        address_string = parts[1]
    parts = address_string.split('市')
    if len(parts) > 1 and level >= 1:
        return parts[0] + '市'
    parts = address_string.split('区')
    if len(parts) > 1 and level >= 2:
        return parts[0] + '区'
    return address_string

def apply_masking_to_csv(input_csv_path, output_csv_path, masking_rules):
    """根据规则对CSV文件进行脱敏处理"""
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: Input CSV file not found at {input_csv_path}")
        return

    for column, rule_type in masking_rules.items():
        if column in df.columns:
            if rule_type == 'phone':
                df[column] = df[column].apply(mask_phone)
            elif rule_type == 'hash':
                df[column] = df[column].apply(hash_id)
            elif rule_type == 'date_offset':
                df[column] = df[column].apply(offset_date)
            elif rule_type == 'income_generalize':
                df[column] = df[column].apply(generalize_income)
            elif rule_type == 'address_truncate':
                df[column] = df[column].apply(truncate_address)
            # Add more rules as needed
        else:
            print(f"Warning: Column '{column}' not found in the input CSV.")

    df.to_csv(output_csv_path, index=False)
    print(f"Masked data saved to {output_csv_path}")

if __name__ == '__main__':
    # Example Usage:
    # Create a dummy CSV for testing
    dummy_data = {
        'Name': ['张三', '李四', '王五'],
        'Phone': ['13812345678', '13987654321', '13011112222'],
        'ID_Number': ['34010119900101123X', '340102198505054567', '340103200010107890'],
        'Birth_Date': ['1990-01-01', '1985-05-05', '2000-10-10'],
        'Income': [8000, 15000, 3000],
        'Address': ['安徽省合肥市蜀山区望江路', '安徽省芜湖市镜湖区长江路', '北京市朝阳区建国门外大街']
    }
    dummy_df = pd.DataFrame(dummy_data)
    dummy_df.to_csv('test_input.csv', index=False)

    masking_rules = {
        'Phone': 'phone',
        'ID_Number': 'hash',
        'Birth_Date': 'date_offset',
        'Income': 'income_generalize',
        'Address': 'address_truncate'
    }

    print("Applying masking rules...")
    apply_masking_to_csv('test_input.csv', 'test_output_masked.csv', masking_rules)
    print("Masking complete. Check test_output_masked.csv")

    # Verify output
    # masked_df = pd.read_csv('test_output_masked.csv')
    # print(masked_df.head())
