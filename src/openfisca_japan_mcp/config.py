from typing import Dict, Any, List

ATTRIBUTE_DICT: Dict[str, Dict[str, Any]] = {
    "年齢": {
        "type": "int",
        "unit": "歳",
        "description": "世帯メンバーの年齢",
        "household_or_member": "member",
    },
    "学年": {
        "type": "int",
        "unit": "",
        "description": "世帯メンバーの学年。ユーザー入力を小学n年生はn, 中学m年生はm+6, 高校l年生はl+9として整数に変換する。小学生未満、大学生以上は`null`とする。",
        "household_or_member": "member",
    },
    "年収": {
        "type": "int",
        "unit": "円",
        "description": "世帯メンバーの年収。賞与も含む。",
        "household_or_member": "member",
    },
    "年1回目の賞与": {
        "type": "int",
        "unit": "円",
        "description": "世帯メンバーの年1回目の賞与",
        "household_or_member": "member",
    },
    "年2回目の賞与": {
        "type": "int",
        "unit": "円",
        "description": "世帯メンバーの年2回目の賞与",
        "household_or_member": "member",
    },
    "年3回目の賞与": {
        "type": "int",
        "unit": "円",
        "description": "世帯メンバーの年3回目の賞与",
        "household_or_member": "member",
    },
    "年4回目以降の賞与合計": {
        "type": "int",
        "unit": "円",
        "description": "世帯メンバーの年4回目以降の賞与の合計",
        "household_or_member": "member",
    },
    "個人事業主の必要経費": {
        "type": "int",
        "unit": "円",
        "description": "世帯メンバーが個人事業主である場合の必要経費。給与所得者の場合は0",
        "household_or_member": "member",
    },
    "身体障害者手帳等級": {
        "type": "str",
        "unit": "",
        "description": "'無', '一級', '二級', '三級', '四級', '五級', '六級', '七級'のいずれか",
        "household_or_member": "member",
    },
    "精神障害者保健福祉手帳等級": {
        "type": "str",
        "unit": "",
        "description": "'無', '一級', '二級', '三級'のいずれか",
        "household_or_member": "member",
    },
    "療育手帳等級": {
        "type": "str",
        "unit": "",
        "description": "'無', 'A', 'B'のいずれか",
        "household_or_member": "member",
    },
    "愛の手帳等級": {
        "type": "str",
        "unit": "",
        "description": "'無', '一度', '二度', '三度', '四度'のいずれか",
        "household_or_member": "member",
    },
    "学生": {
        "type": "bool",
        "unit": "",
        "description": "小・中・高校、大学、専門学校、職業訓練学校等の学生であるか否か",
        "household_or_member": "member",
    },
    "国民年金基金掛金": {
        "type": "int",
        "unit": "円",
        "description": "国民年金基金の掛金の年額。国民年金の保険料ではない。",
        "household_or_member": "member",
    },
    "厚生年金基金掛金": {
        "type": "int",
        "unit": "円",
        "description": "厚生年金基金の掛金の年額。厚生年金の保険料ではない。",
        "household_or_member": "member",
    },
    "介護施設入所中": {
        "type": "bool",
        "unit": "",
        "description": "介護施設に入所しているか否か",
        "household_or_member": "member",
    },
}

TAX_BENEFIT_DICT: Dict[str, Dict[str, Any]] = {
    "所得税": {
        "output_level": "member",
        "input_attribute": [
            {"name": "年齢", "required": True},
            {"name": "年収", "required": True},
            {"name": "個人事業主の必要経費", "required": True},
            {"name": "年1回目の賞与", "required": False},
            {"name": "年2回目の賞与", "required": False},
            {"name": "年3回目の賞与", "required": False},
            {"name": "年4回目以降の賞与合計", "required": False},
            {"name": "国民年金基金掛金", "required": False},
            {"name": "厚生年金基金掛金", "required": False},
            {"name": "身体障害者手帳等級", "required": False},
            {"name": "精神障害者保健福祉手帳等級", "required": False},
            {"name": "療育手帳等級", "required": False},
            {"name": "愛の手帳等級", "required": False},
            {"name": "学生", "required": False},
            {"name": "介護施設入所中", "required": False},
        ]
    },
    "住民税": {
        "output_level": "member",
        "input_attribute": [
            {"name": "年齢", "required": True},
            {"name": "年収", "required": True},
            {"name": "個人事業主の必要経費", "required": True},
            {"name": "年1回目の賞与", "required": False},
            {"name": "年2回目の賞与", "required": False},
            {"name": "年3回目の賞与", "required": False},
            {"name": "年4回目以降の賞与合計", "required": False},
            {"name": "国民年金基金掛金", "required": False},
            {"name": "厚生年金基金掛金", "required": False},
            {"name": "身体障害者手帳等級", "required": False},
            {"name": "精神障害者保健福祉手帳等級", "required": False},
            {"name": "療育手帳等級", "required": False},
            {"name": "愛の手帳等級", "required": False},
            {"name": "学生", "required": False},
            {"name": "介護施設入所中", "required": False},
        ]
    },
    "社会保険料": {
        "output_level": "member",
        "input_attribute": [
            {"name": "年齢", "required": True},
            {"name": "年収", "required": True},
            {"name": "個人事業主の必要経費", "required": True},
            {"name": "年1回目の賞与", "required": False},
            {"name": "年2回目の賞与", "required": False},
            {"name": "年3回目の賞与", "required": False},
            {"name": "年4回目以降の賞与合計", "required": False},
            {"name": "国民年金基金掛金", "required": False},
            {"name": "厚生年金基金掛金", "required": False},
            {"name": "身体障害者手帳等級", "required": False},
            {"name": "精神障害者保健福祉手帳等級", "required": False},
            {"name": "療育手帳等級", "required": False},
            {"name": "愛の手帳等級", "required": False},
            {"name": "学生", "required": False},
            {"name": "介護施設入所中", "required": False},
        ]
    },
    "児童手当": {
        "output_level": "household",
        "input_attribute": [
            {"name": "年齢", "required": True},
            {"name": "学年", "required": False},
            # 所得制限は撤廃されているため年収は不要
        ]
    }
}
