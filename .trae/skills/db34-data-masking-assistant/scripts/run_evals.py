import pandas as pd
import os
import sys

# 获取脚本所在目录的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
# 将脚本目录加入 sys.path 以便导入 masking_engine
sys.path.append(SCRIPT_DIR)

from masking_engine import apply_masking_to_csv, mask_phone, hash_id, offset_date, generalize_income, truncate_address

def run_eval_case(case_name, input_data, masking_rules, expected_output_data, eval_function):
    print(f"\n--- Running Eval Case: {case_name} ---")
    
    # 使用绝对路径
    cases_dir = os.path.join(PROJECT_ROOT, "evals", "cases")
    os.makedirs(cases_dir, exist_ok=True)
    
    input_csv_path = os.path.join(cases_dir, f"{case_name}_input.csv")
    output_csv_path = os.path.join(cases_dir, f"{case_name}_output.csv")
    expected_csv_path = os.path.join(cases_dir, f"{case_name}_expected.csv")

    # 创建输入 CSV
    pd.DataFrame(input_data).to_csv(input_csv_path, index=False)
    # 创建预期输出 CSV
    pd.DataFrame(expected_output_data).to_csv(expected_csv_path, index=False)

    # 执行脱敏
    apply_masking_to_csv(input_csv_path, output_csv_path, masking_rules)

    # 评估输出
    return eval_function(output_csv_path, expected_csv_path)

def eval_csv_content(actual_path, expected_path):
    try:
        actual_df = pd.read_csv(actual_path)
        expected_df = pd.read_csv(expected_path)

        # 转换为字符串进行比较，避免类型不匹配
        actual_df = actual_df.astype(str)
        expected_df = expected_df.astype(str)

        if actual_df.equals(expected_df):
            print(f"Eval Passed: Output matches expected.")
            return True
        else:
            print(f"Eval Failed: Output does not match expected.")
            print("Actual:\n", actual_df)
            print("Expected:\n", expected_df)
            return False
    except Exception as e:
        print(f"Eval Failed due to error: {e}")
        return False

def eval_text_content(actual_content, expected_substring):
    if expected_substring in actual_content:
        print(f"Eval Passed: Expected substring \'{expected_substring}\' found.")
        return True
    else:
        print(f"Eval Failed: Expected substring \'{expected_substring}\' not found.")
        print("Actual content:\n", actual_content)
        return False


if __name__ == '__main__':
    all_passed = True

    # 案例 1: 开发测试场景 (CSV 脱敏)
    input_data_case1 = {
        'Name': ['张三', '李四', '王五'],
        'Phone': ['13812345678', '13987654321', '13011112222'],
        'ID_Number': ['34010119900101123X', '340102198505054567', '340103200010107890'],
        'Birth_Date': ['1990-01-01', '1985-05-05', '2000-10-10'],
    }
    masking_rules_case1 = {
        'Phone': 'phone',
        'ID_Number': 'hash',
        'Birth_Date': 'date_offset',
    }
    expected_data_case1 = {
        'Name': ['张三', '李四', '王五'],
        'Phone': [mask_phone('13812345678'), mask_phone('13987654321'), mask_phone('13011112222')],
        'ID_Number': [hash_id('34010119900101123X'), hash_id('340102198505054567'), hash_id('340103200010107890')],
        'Birth_Date': [offset_date('1990-01-01'), offset_date('1985-05-05'), offset_date('2000-10-10')],
    }
    if not run_eval_case('case1_dev_test', input_data_case1, masking_rules_case1, expected_data_case1, eval_csv_content):
        all_passed = False

    # 案例 2: 数据分析场景 (包含收入/地址的 CSV 脱敏)
    input_data_case2 = {
        'Customer_ID': [1, 2, 3],
        'Income': [8000, 15000, 3000],
        'Address': ['安徽省合肥市蜀山区望江路', '安徽省芜湖市镜湖区长江路', '北京市朝阳区建国门外大街']
    }
    masking_rules_case2 = {
        'Income': 'income_generalize',
        'Address': 'address_truncate'
    }
    expected_data_case2 = {
        'Customer_ID': [1, 2, 3],
        'Income': [generalize_income(8000), generalize_income(15000), generalize_income(3000)],
        'Address': [truncate_address('安徽省合肥市蜀山区望江路'), truncate_address('安徽省芜湖市镜湖区长江路'), truncate_address('北京市朝阳区建国门外大街')]
    }
    if not run_eval_case('case2_data_analysis', input_data_case2, masking_rules_case2, expected_data_case2, eval_csv_content):
        all_passed = False

    # 案例 3: 合规咨询 (文本查询)
    consultation_query = "脱敏的基本要求有哪些？"
    expected_answer_keywords = ["降低或去除敏感数据被恢复的风险", "确保脱敏前后的数据可用性", "策略符合我国法律法规与相关标准"]
    
    simulated_response_case3 = (
        "根据《DB34/T 政务数据 第2部分：脱敏技术规范》，数据脱敏的基本要求包括："\
        "1. 降低或去除敏感数据被恢复的风险。"\
        "2. 确保脱敏前后的数据可用性。"\
        "3. 脱敏数据尽量满足其预期目的。"\
        "4. 策略符合我国法律法规与相关标准。"
    )

    case3_passed = True
    for keyword in expected_answer_keywords:
        if not eval_text_content(simulated_response_case3, keyword):
            case3_passed = False
            break
    if not case3_passed:
        all_passed = False

    if all_passed:
        print("\nAll evaluation cases passed!")
        sys.exit(0)
    else:
        print("\nSome evaluation cases failed.")
        sys.exit(1)
