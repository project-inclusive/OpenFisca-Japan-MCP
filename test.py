import json
from src.openfisca_japan_mcp.sdk import get_tax_benefit_info, calc

def run_tests():
    print("--- 1. get_tax_benefit_info のテスト ---")
    attrs_shotoku = get_tax_benefit_info("所得税")
    print(json.dumps(attrs_shotoku, indent=2, ensure_ascii=False))

    attrs_invalid = get_tax_benefit_info("架空の税金")
    print("invalid:", attrs_invalid)

    print("\n--- 2. calc のテスト ---")
    household_list = [  
        {
            "name": "household1",
            "household_attribute": { 
                "居住都道府県": "東京都", 
                "居住市区町村": "千代田区", 
            },
            "member_attribute": [{
                "name": "member1",  
                "年齢": 40,  
                "年収": 10000000,  
                "個人事業主の必要経費": None,
                }
            ]
        },
        {
            "name": "household2",
            "household_attribute": { 
                "居住都道府県": None, 
                "居住市区町村": None, 
            },
            "member_attribute": [{
                "name": "member1",  
                "年齢": 50,  
                "年収": 10001000,  
                "個人事業主の必要経費": 0,
                },
                {
                "name": "member2",  
                "年齢": 15,  
                "年収": 0,  
                "個人事業主の必要経費": None,
                }
            ]
        }
    ]

    output_list = calc(
        household_list, 
        [
            # 所得税はOpenFisca-Japan 2.1.0で未実装
            # {"name": "所得税", "household_or_member": "member"}, 
            {"name": "児童手当", "household_or_member": "household"}
        ], 
        "2025-01-01"
    )
    print(json.dumps(output_list, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run_tests()
