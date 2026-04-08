from typing import List, Dict, Any, Optional
from datetime import datetime

import numpy as np
from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_japan import CountryTaxBenefitSystem

def get_attribute_info(tax_benefit_name: str) -> List[Dict[str, Any]]:
    """
    指定された制度をcalc toolで計算するために必要なattributeのリストを返します。
    """
    supported_benefits = ["所得税", "住民税", "社会保険料", "児童手当"]
    if tax_benefit_name not in supported_benefits:
        return []
    
    return [
        {
            "name": "年齢",
            "type": "int",
            "unit": "歳",
            "description": "世帯メンバーの年齢",
            "household_or_member": "member",
            "required": True
        },
        {
            "name": "年収",
            "type": "int",
            "unit": "円",
            "description": "世帯メンバーの年収",
            "household_or_member": "member",
            "required": True
        },
        {
            "name": "個人事業主の必要経費",
            "type": "int",
            "unit": "円",
            "description": "世帯メンバーが個人事業主である場合の必要経費。給与所得者の場合は0",
            "household_or_member": "member",
            "required": True
        }
    ]

def calc(household_list: List[Dict[str, Any]], output_tax_benefit_list: List[Dict[str, str]], date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    入力された世帯情報をもとに、入力で指定された制度の金額計算結果を出力します。
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
        
    tax_benefit_list = [tb for tb in output_tax_benefit_list if tb.get("name") in ["所得税", "住民税", "社会保険料", "児童手当"]]
    
    if not tax_benefit_list:
        return household_list

    # OpenFisca-Japan の準備
    tax_benefit_system = CountryTaxBenefitSystem()
    
    # データを解析して ndarray のリストを構築
    person_id_list = []
    household_id_list = []
    person_role_list = []
    birth_date_list = []
    income_list = []
    expenses_list = []
    
    hh_id_list = []
    hh_pref_list = []
    hh_city_list = []
    
    target_date = datetime.strptime(date, "%Y-%m-%d")
    
    p_id = 0
    h_id = 0
    
    for hh in household_list:
        hh_id_list.append(h_id)
        hh_attr = hh.get("household_attribute", {}) or {}
        hh_pref_list.append(hh_attr.get("居住都道府県"))
        hh_city_list.append(hh_attr.get("居住市区町村"))
        
        members = hh.get("member_attribute", [])
        for m in members:
            if "name" not in m:
                m["name"] = f"member{p_id+1}"
            
            age = m.get("年齢", 0)
            birth_year = target_date.year - age
            birth_date = f"{birth_year}-{target_date.month:02d}-{target_date.day:02d}"
            
            role = "子" if age < 18 else "親"
            
            person_id_list.append(p_id)
            household_id_list.append(h_id)
            person_role_list.append(role)
            birth_date_list.append(birth_date)
            
            income_list.append(m.get("年収", 0))
            
            expenses = m.get("個人事業主の必要経費")
            expenses_list.append(expenses if expenses is not None else 0)
            
            p_id += 1
        h_id += 1

    data_persons_dict = {
        "person_id": np.array(person_id_list, dtype=int),
        "household_id": np.array(household_id_list, dtype=int),
        "person_role_in_household": np.array(person_role_list, dtype=str),
        "誕生年月日": np.array(birth_date_list, dtype=str),
        "収入": np.array(income_list, dtype=int),
        "個人事業主の必要経費": np.array(expenses_list, dtype=int),
    }

    data_households_dict = {
        "household_id": np.array(hh_id_list, dtype=int),
        "居住都道府県": np.array([p if p is not None else "" for p in hh_pref_list], dtype=str),
        "居住市区町村": np.array([c if c is not None else "" for c in hh_city_list], dtype=str)
    }

    sb = SimulationBuilder()
    sb.create_entities(tax_benefit_system)

    sb.declare_person_entity("人物", data_persons_dict["person_id"])
    household_instance = sb.declare_entity("世帯", data_households_dict["household_id"])

    person_household = data_persons_dict["household_id"]
    person_household_role = data_persons_dict["person_role_in_household"]
    sb.join_with_persons(household_instance, person_household, person_household_role)

    simulation = sb.build(tax_benefit_system)

    for input_key, input_value in data_households_dict.items():
        if input_key == "household_id":
            continue
        try:
            simulation.set_input(input_key, date, input_value)
        except Exception:
            pass

    for input_key, input_value in data_persons_dict.items():
        if input_key in ["household_id", "person_role_in_household", "person_id"]:
            continue
        try:
            simulation.set_input(input_key, date, input_value)
        except Exception:
            pass

    for tb in tax_benefit_list:
        tax_benefit = tb.get("name")
        household_or_member = tb.get("household_or_member")
        try:
            amount_array = simulation.calculate(tax_benefit, date)
            if household_or_member == "member":
                # Person
                for p_id_val, amount in enumerate(amount_array):
                    hh_idx = household_id_list[p_id_val]
                    hh = household_list[hh_idx]
                    members = hh.get("member_attribute", [])
                    
                    local_idx = 0
                    for prev_hh_idx in range(hh_idx):
                        local_idx += len(household_list[prev_hh_idx].get("member_attribute", []))
                    member_local_idx = p_id_val - local_idx
                    
                    if member_local_idx < len(members):
                        m = members[member_local_idx]
                        if hasattr(np, "isnan"):
                            # Numpy version check for float parsing
                            try:
                                is_nan = np.isnan(amount)
                            except TypeError:
                                is_nan = False
                        else:
                            is_nan = False
                        
                        m[tax_benefit] = int(amount) if not is_nan else 0

            elif household_or_member == "household":
                # Household
                for h_id_val, amount in enumerate(amount_array):
                    hh = household_list[h_id_val]
                    if "household_attribute" not in hh or hh["household_attribute"] is None:
                        hh["household_attribute"] = {}
                        
                    try:
                        is_nan = np.isnan(amount)
                    except TypeError:
                        is_nan = False
                        
                    hh["household_attribute"][tax_benefit] = int(amount) if not is_nan else 0
        except Exception as e:
            # 万が一の計算エラーはスキップ
            print(f"[{tax_benefit}] Calculation skip. Error: {e}")
            pass

    return household_list
