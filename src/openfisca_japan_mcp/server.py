from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from .sdk import get_tax_benefit_info, calc

mcp = FastMCP("OpenFisca-Japan-MCP")

@mcp.tool()
def tax_benefit_info(tax_benefit_name: str) -> Dict[str, Any]:
    """
    指定された制度を計算するために必要な入力属性のリストと出力単位を返します。
    MCPクライアントはユーザーにこれらの属性内容を質問し、その回答を集めて `calculate_tax_benefit` ツールに渡してください。
    
    戻り値のフォーマット:
    以下のキーを持つ辞書を返します。
    - "input_attribute": 以前のattribute_infoが返していた属性情報のリスト
    - "output_level": 制度の出力単位 ("household" または "member")

    Args:
        tax_benefit_name: 計算したい制度名（例: 所得税, 住民税, 社会保険料, 児童手当）
    """
    return get_tax_benefit_info(tax_benefit_name)

@mcp.tool()
def calculate_tax_benefit(
    household_list: List[Dict[str, Any]], 
    output_tax_benefit_list: List[Dict[str, str]], 
    date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    入力された世帯情報をもとに、指定された制度の金額計算結果を出力します。
    
    `tax_benefit_info` で得られた"input_attribute"の各要素は、
    その "household_or_member" の値に応じて
    household_list 内の適切な場所へ以下のように追加した上で入力してください。
    (得られた属性名は変更せずそのままキー名としてください。)
    
    - "household_or_member" が "household" の場合:
      各世帯を表す辞書内の `household_attribute` 辞書に、キー名を属性名として、値をユーザー回答として追加してください。
    - "household_or_member" が "member" の場合:
      各世帯を表す辞書内の `member_attribute` リストに含まれる、各個人の辞書に直接キー名を属性名として、値をユーザー回答として追加してください。
    
    ユーザーの入力情報は、属性のdescriptionに従って適切に変換してから入力してください。
    特に文字列の場合は指定された選択肢以外の値は入力しないでください。

    `tax_benefit_info` で得られた"output_level"の値に応じて、
    output_tax_benefit_listの各要素の"household_or_member"を設定してください。
    ("input_attribute"の各要素の"household_or_member"とは別物です。)

    Args:
        household_list: 世帯情報のリスト。"name", "household_attribute", "member_attribute" を含む。
        output_tax_benefit_list: 出力したい制度のリスト。各要素は {"name": "制度名", "household_or_member": "household" または "member"}。
        date: 計算する基準日 (YYYY-MM-DD)。省略時は現在日時を使用します。
        
    Returns:
        計算結果が付与された世帯情報のリスト。
    """
    return calc(household_list, output_tax_benefit_list, date)
