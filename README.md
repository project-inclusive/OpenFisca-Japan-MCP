# OpenFisca-Japan-MCP

OpenFisca-Japan-MCP は、[OpenFisca-Japan](https://github.com/project-inclusive/OpenFisca-Japan) を MCP (Model Context Protocol) 経由で呼び出すためのサーバーおよび Python SDK です。LLM エージェント（Claude Desktop など）から利用しやすい型とインターフェースを提供します。

OpenFisca-Japanは、日本の税制・社会保障制度をシミュレーションするためのオープンソースソフトウェアです。主に官庁・自治体が公開している制度情報を基に計算ロジックを実装していますが、例外的な条件などは反映されていない場合があり、完全に正しい結果を保証するものではありません。あくまで目安としてご利用ください。  
[OpenFisca-JapanのGitHubリポジトリ](https://github.com/project-inclusive/OpenFisca-Japan)上で、実装されている計算ロジックおよび必要条件を確認できます。

## 機能 (Tools)
- `tax_benefit_info(tax_benefit_name)`: 入力された制度を計算するために必要な属性情報を取得します。
- `calculate_tax_benefit(household_list, output_tax_benefit_list, date)`: 世帯の配列データを元に、指定した制度の金額を計算し、元の配列を拡張して返します。

### データ構造の例

`calculate_tax_benefit` ツールに渡す `household_list` は以下のような構造になります。

```json
[
  {
    "name": "世帯1",
    "household_attribute": {
      "居住都道府県": "東京都",
      "居住市区町村": "千代田区"
    },
    "member_attribute": [
      {
        "name": "親1",
        "年齢": 40,
        "年収": 6000000,
        "個人事業主の必要経費": 0
      },
      {
        "name": "子1",
        "年齢": 10,
        "年収": 0
      }
    ]
  }
]
```

## 対応制度
- 所得税
- 住民税
- 社会保険料
- 児童手当
- 生活保護

## MCP Client からの利用

`openfisca-japan-mcp` は PyPI に登録されており、`uvx` を使用して、様々な MCP クライアントから簡単に呼び出すことができます。

> [!IMPORTANT]
> 本パッケージは **Python 3.11** で動作させる必要があります（OpenFisca の依存関係の制約による）。
> `uvx` で実行する際は、必ず **`--python 3.11`** オプションを指定してください。

### 設定の基本構成 (JSON)

多くのクライアント（Claude, Copilot, Gemini など）では、以下の内容を設定ファイルに追加します。

```json
{
  "mcpServers": {
    "openfisca-japan-mcp": {
      "command": "uvx",
      "args": ["--python", "3.11", "openfisca-japan-mcp"]
    }
  }
}
```

### 各クライアントの設定場所

> [!NOTE]
> Claude Desktop と Claude Code (CLI) は設定ファイルを共有しません。両方で利用する場合は、それぞれに対して設定が必要です。

- **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Claude Code (CLI)**: 以下のように CLI コマンドで追加するのが推奨されています。
  ```bash
  claude mcp add openfisca-japan-mcp -- uvx --python 3.11 openfisca-japan-mcp
  ```
  *(手動設定の場合は `~/.claude.json` に追記します)*
- **GitHub Copilot CLI**: `~/.config/github-copilot/mcp-servers.json`
- **Gemini CLI / Google AI Studio**: `~/.gemini/settings.json`
- **Cursor / Codex**: 
    - 設定画面の MCP セクションから以下のコマンドを登録します。
    - **Type**: `command`
    - **Command**: `uvx --python 3.11 openfisca-japan-mcp`

---

## ローカルでの開発・検証

GitHub からクローンしたリポジトリを直接参照する場合は、`--from` オプションでディレクトリを指定します。

```json
{
  "mcpServers": {
    "openfisca-japan-mcp": {
      "command": "uvx",
      "args": [
        "--python", "3.11",
        "--from", "/path/to/OpenFisca-Japan-MCP",
        "openfisca-japan-mcp"
      ]
    }
  }
}
```

## Python SDK としての利用

MCP を介さず、Python ライブラリとして直接計算ロジックを利用することも可能です。

```python
from openfisca_japan_mcp.sdk import calc

household_list = [
    {
        "name": "household1",
        "household_attribute": { "居住都道府県": "東京都" },
        "member_attribute": [
            { "name": "member1", "年齢": 35, "年収": 5000000 }
        ]
    }
]

# 計算の実行
result = calc(
    household_list, 
    [{"name": "児童手当", "household_or_member": "household"}]
)

print(result[0]["household_attribute"]["児童手当"])
```

## 開発者向けのセットアップ

リポジトリをクローンしてローカルで開発・テストを行う手順です。

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/project-inclusive/OpenFisca-Japan-MCP.git
   cd OpenFisca-Japan-MCP
   ```

2. **依存関係のインストール**
   `uv` を使用して環境を構築します。Python 3.11 がインストールされている必要があります。
   ```bash
   uv python install 3.11
   uv sync --python 3.11
   ```

3. **テストの実行**
   ```bash
   uv run test.py
   ```

## ライセンス

[Apache License 2.0](LICENSE)
