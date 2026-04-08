以下の指示に従って、MCPサーバーを実装してください。計画や実行結果は日本語で説明してください。MCPクライアントに提供する説明も日本語で記載してください。
計画を実行する前に、その他に指定しておいた方が良い条件があれば私に確認してください。

# 概要
入力された世帯情報に応じた所得税などの計算結果を出力する"OpenFisca-Japan"というPythonライブラリが既に存在する。このMCPサーバーは、そのスキーマをより扱いやすくしたtoolsをMCPクライアントに提供する。

# 形態
- Pythonで実装
- `OpenFisca-Japan-MCP`という名前でPyPIに公開できるようにする。
- fastmcpライブラリを利用して、ビジネスロジックとトランスポート層は分離する。uvxとstdioで配布する方法と、httpとSSEでデプロイして利用する方法を両方実装する。
- uvxとstdioで配布する方法として、`OpenFisca-Japan-MCP`ライブラリをuvで環境構築し、uvxで実行できるようにする。以下のようにローカルのMCPクライアントにuvで配布されているMCPサーバーを設定するイメージ。
    ```json
    // Claude Desktop の設定例 (mcp_settings.json)
    {
        "mcpServers": {
            "my-server": {
            "command": "uvx",
            "args": ["openfisca-japan-mcp"]
            }
        }
    }
    ```
- MCPサーバーのtoolsは、ユーザーがSDKとしても利用できるようにする。

- 必要なライブラリはnumpy, OpenFisca-Core, OpenFisca-Japan, fastmcp


# Toolsの仕様
`get_attribute_info`と`calc`の2つのtoolを実装する。

## get_attribute_info
入力された制度を`calc`toolで計算するために必要なattributeのリストを返す。
所得税, 住民税, 社会保険料, 児童手当のみ計算可能。それ以外の制度名が入力された場合は空のリストを返す。

### 入力
- tax_benefit_name: string. `calc`で計算する制度名

### 出力
入力されたtax_benefit_nameを`calc`toolで計算するために必要なattributeのリスト。MCPクライアントはユーザーにこれらのattributeを質問し、その回答を`calc`toolに渡す。"required"がtrueのattributeは必須回答、falseは任意回答（答えた方が計算結果はより正確）であることをユーザーに伝える。

- attribute: list of dict. 各要素は 
```json
{"name": "", "type": "", "unit": "", "description": "", 
"household_or_member": "household" or "member",
"required": true/false} 
```

### 内部処理
以下のようにtax_benefit_nameに対応するattributeのlistを返す。tax_benefit_nameは所得税, 住民税, 社会保険料, 児童手当のいずれかとし、それら以外の場合は空のリストを返す。
（返すattributeのパターンをtax_benefit_nameに応じて変更できるよう、tax_benefit_nameをキーとしてattribute_listを格納した辞書を用意し、そこから返すようにする）

- 所得税, 住民税, 社会保険料, 児童手当

```json
[
    {
        "name": "年齢",
        "type": "int",
        "unit": "歳",
        "description": "世帯メンバーの年齢",
        "household_or_member": "member",
        "required": true
    },
    {
        "name": "年収",
        "type": "int",
        "unit": "円",
        "description": "世帯メンバーの年収",
        "household_or_member": "member",
        "required": true
    },
    {
        "name": "個人事業主の必要経費",
        "type": "int",
        "unit": "円",
        "description": "世帯メンバーが個人事業主である場合の必要経費。給与所得者の場合は0",
        "household_or_member": "member",
        "required": true
    }
]
```


## calc
入力された世帯情報をもとに、入力で指定された制度の金額計算結果を出力する。

### 入力

- household_list: 必須引数。世帯単位のdictのリスト。リストの要素数は世帯数に応じて可変。
dictの"name", "household_attribute", "member": {"name"}のkeyは必須で、valueのdefaultは`null`。以下は例
```json
[  // 世帯のリスト。要素数は世帯の数に応じて可変。
	{
		"name": "household1",  // 世帯名は一意に設定
        "household_attribute": {  // この中のオプションkeyがない場合はvalueはnull
            "居住都道府県": null, // オプションkey.
　　	    "居住市区町村": null // オプションkey.
        },
		"member_attribute": [{  // 世帯員のリスト。要素数は世帯員の数に応じて可変。
			"name": "太郎",  // 必須key. 世帯員の名前は世帯内で一意だが、異なる世帯間で重複しても良い
			"年齢": 40,  // オプションkey. int
			"年収": 10000000,  // オプションkey. int
			"個人事業主の必要経費": null,  // オプションkey. int
			},
        { // ...
        }
        ]
    },
    {
        "name": "household2",
        // ...
    },
    // ...
]
```

- output_tax_benefit_list: 必須引数。出力したい制度のリスト。"所得税", "住民税", "社会保険料", "児童手当"のいずれか、または複数。
　　ex. `["所得税", "住民税", "児童手当"]`
- date: オプション引数。`YYYY-MM-DD`形式。計算する時点となる日付。入力されていない場合は現在の日付とする。

### 出力
入力した世帯構成dictのリストに出力属性が追加されたもの。  
ex. 
```json
[  // 世帯のリスト。要素数は世帯の数に応じて可変。
	{
		"name": "household1",  // 世帯名は一意に設定
        "household_attribute": {  // この中のオプションkeyがない場合はvalueはnull
            "居住都道府県": null, // オプションkey.
		    "居住市区町村": null, // オプションkey.
            "児童手当": 10000 // 計算結果(世帯単位)
        },
		"member_attribute": [{  // 世帯員のリスト。要素数は世帯員の数に応じて可変。
			"name": "member1",  // 必須key. 世帯員の名前は世帯内で一意だが、異なる世帯間で重複しても良い。ユーザー入力は不要で、内部で自動生成する。
			"年齢": 40,  // オプションkey. int
			"年収": 10000000,  // オプションkey. int
			"個人事業主の必要経費": null,  // オプションkey. int
            "所得税": 1000000, // 計算結果 (世帯員単位)
            "住民税": 1000000, // 計算結果 (世帯員単位)
			},
        { // ...
        }
        ]
    },
    {
        "name": "household2",
        // ...
    },
    // ...
]
```

### 内部処理
以下のコードを参考にtoolsを実装

```python
import os
import time
import locale
import sys

import numpy as np
from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_japan import CountryTaxBenefitSystem

# 入力されたoutput_tax_benefit_listに対応する制度リスト (ex. ["所得税", "住民税", "社会保険料"])
tax_benefit_list = output_tax_benefit_list

# 入力された制度計算の対象とする日時. YYYY-MM-DD 形式で記述する. 入力されていない場合は現在の日付とする
period = date

# 入力されたhousehold_listからdata_persons_dictを生成する
# data_persons_dictは{key: ndarray}のフォーマットにする
# keyは"person_id", "household_id", "person_role_in_household", "誕生年月日"を必ず含む
# ndarrayは、全世帯の全memberを1列の配列にし、それに対応した値を格納する
# person_id は全世帯の全memberで一意なID(int)とする
# household_id は世帯ごとに一意なID(int)とする
# person_role_in_household は"親", "子"のいずれかの文字列とする。世帯構成にかかわらず、18歳未満は"子"、18歳以上は子供がいなくても"親"とする
# 誕生年月日は"YYYY-MM-DD"形式の文字列とする。date - 年齢で算出する
# その他のkeyとvalueはhousehold_listのmemberに含まれるkey、対応するvalueとする。ただし、household_listの"年収"は"収入"に変換する

# 入力されたhousehold_listからdata_households_dictを生成する
# data_households_dictも{key: ndarray}のフォーマットにする
# keyは"household_id"を必ず含む
# ndarrayは、全世帯を1列の配列にし、それに対応した値を格納する
# household_id はdata_persons_dictのhousehold_idと対応させる
# その他のkeyとvalueはhousehold_listのhousehold_attributeに含まれるkey、対応するvalueとする

# 例えば以下のようにhousehold_listからdata_persons_dictとdata_households_dictを生成する
# household_list
household_list = [  
	{
		"name": "household1",
        "household_attribute": { 
            "居住都道府県": "東京都", 
		    "居住市区町村": "千代田区", 
            "児童手当": 10000 
        },
		"member_attribute": [{
			"name": "member1",  
			"年齢": 40,  
			"年収": 10000000,  
			"個人事業主の必要経費": null,
			}
        ]
    },
    {
        "name": "household2",,
        "household_attribute": { 
            "居住都道府県": null, 
		    "居住市区町村": null, 
            "児童手当": 10000 
        },
		"member_attribute": [{
			"name": "member1",  
			"年齢": 50,  
			"年収": 10001000,  
			"個人事業主の必要経費": null,
			},
			{
			"name": "member2",  
			"年齢": 15,  
			"年収": 0,  
			"個人事業主の必要経費": null,
			}
        ]
    }
]

# 上のhousehold_listから以下を生成
data_persons_dict = {
    "person_id": np.array([0, 1, 2]),
    "household_id": np.array([0, 1, 1]),
    "person_role_in_household": np.array(["親", "親", "子"]),
    "誕生年月日": np.array(["1986-01-01", "1976-01-01", "2011-01-01"]), # MM-DDはdateのMM-DDと同じにする
    "収入": np.array([10000000, 10001000, 0]),
    "個人事業主の必要経費": np.array([0, 0, 0]),
}

data_households_dict = {
    "household_id": np.array([0, 1]),
    "居住都道府県": np.array(["東京都", ""]),
    "居住市区町村": np.array(["千代田区", ""])
}

### 例はここまで ###


### OpenFiscaの準備 ###
tax_benefit_system = CountryTaxBenefitSystem()
sb = SimulationBuilder()
sb.create_entities(tax_benefit_system)

# 人物(世帯員)と世帯のそれぞれ一意なIDの登録
sb.declare_person_entity("人物", data_persons_dict["person_id"])
household_instance = sb.declare_entity("世帯", data_households_dict["household_id"])

# 人物(世帯員)と世帯の紐付け
person_household = data_persons_dict["household_id"]
person_household_role = data_persons_dict["person_role_in_household"]
sb.join_with_persons(household_instance, person_household, person_household_role)


### 入力属性 ###
simulation = sb.build(tax_benefit_system)

# household_attributeの入力
for input_key, input_value in data_households_dict.items():
    if input_key == "household_id":
        continue
    simulation.set_input(input_key, period, input_value)

# personの入力
for input_key, input_value in data_persons_dict.items():
    if input_key == "household_id" or input_key == "person_role_in_household":
        continue
    simulation.set_input(input_key, period, input_value)

### シミュレーション実行 ###
for tax_benefit in tax_benefit_list:
    amount = simulation.calculate(tax_benefit, period)

    # get_attribute_infoで得たattributeの"household_or_member"が"member"であれば、household_listのmember_attributeの全memberにkey (tax_benefit)と value (amount)を追加
    # get_attribute_infoで得たattributeの"household_or_member"が"household"であれば、household_listの各household_attributeにkey (tax_benefit)と value (amount)を追加
    

```

