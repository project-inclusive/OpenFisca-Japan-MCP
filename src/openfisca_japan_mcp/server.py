from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from .sdk import get_attribute_info, calc

mcp = FastMCP("OpenFisca-Japan-MCP")

@mcp.tool()
def attribute_info(tax_benefit_name: str) -> List[Dict[str, Any]]:
    """
    指定された制度を計算するために必要な入力属性のリストを返します。
    MCPクライアントはユーザーにこれらの属性内容を質問し、その回答を集めて `calculate_tax_benefit` ツールに渡してください。
    
    戻り値のフォーマット:
    それぞれの要素が以下のキーを持つ辞書のリストを返します。
    - "name": 属性の名称 (例: "年齢", "年収")
    - "type": 属性のデータ型 (例: "int")
    - "unit": 属性の単位 (例: "歳", "円")
    - "description": 属性に関する説明
    - "household_or_member": その属性が世帯単位 ("household") か個人単位 ("member") かを示します。
    - "required": 計算にあたって必須の項目であるか (True/False)

    Args:
        tax_benefit_name: 計算したい制度名（例: 所得税, 住民税, 社会保険料, 児童手当）
    """
    return get_attribute_info(tax_benefit_name)

@mcp.tool()
def calculate_tax_benefit(
    household_list: List[Dict[str, Any]], 
    output_tax_benefit_list: List[Dict[str, str]], 
    date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    入力された世帯情報をもとに、指定された制度の金額計算結果を出力します。
    
    `attribute_info` で得られた属性は、その "household_or_member" の値に応じて
    household_list 内の適切な場所へ以下のように追加した上で入力してください。
    
    - "household_or_member" が "household" の場合:
      各世帯を表す辞書内の `household_attribute` 辞書に、キー名を属性名として、値をユーザー回答として追加してください。
    - "household_or_member" が "member" の場合:
      各世帯を表す辞書内の `member_attribute` リストに含まれる、各個人の辞書に直接キー名を属性名として、値をユーザー回答として追加してください。
    
    Args:
        household_list: 世帯情報のリスト。"name", "household_attribute", "member_attribute" を含む。
        output_tax_benefit_list: 出力したい制度のリスト。各要素は {"name": "制度名", "household_or_member": "household" または "member"}。
        date: 計算する基準日 (YYYY-MM-DD)。省略時は現在日時を使用します。
        
    Returns:
        計算結果が付与された世帯情報のリスト。
    """
    return calc(household_list, output_tax_benefit_list, date)
