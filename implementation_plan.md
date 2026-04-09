# OpenFisca-Japan-MCP 実装計画

既存の OpenFisca-Japan パッケージを利用し、MCP クライアント（Claude Desktop など）から利用しやすい型とインターフェースを提供する MCP サーバーを構築します。

## 背景と目的
OpenFisca-Japan を直接呼び出すには、データのベクトル化（ndarray化）や内部の人物・世帯エンティティへの紐付けなど複雑な処理が必要です。この複雑な部分を隠蔽し、使いやすい JSON ベースの API としてアクセスできるようにするツール (`get_attribute_info`, `calc`) を提供します。これにより MCP 経由での LLM からの呼び出しや、Python SDK としての利用が容易になります。

## Proposed Changes

### パッケージ構成の全体像
`OpenFisca-Japan-MCP` リポジトリ直下に以下のような構成で Python プロジェクトを作成します。

```
OpenFisca-Japan-MCP/
├── pyproject.toml
├── README.md
└── src/
    └── openfisca_japan_mcp/
        ├── __init__.py
        ├── sdk.py         # ユーザーがSDKとして利用する機能や内部処理
        ├── server.py      # fastmcp を用いた MCP サーバーの定義
        └── cli.py         # コマンドラインのエントリーポイント
```

### [NEW] `pyproject.toml`
パッケージングの設定と依存関係を定義します。
- `project.name = "openfisca-japan-mcp"`
- 依存関係: `numpy`, `OpenFisca-Core`, `OpenFisca-Japan`, `fastmcp`
- スクリプト: `openfisca-japan-mcp = "openfisca_japan_mcp.cli:main"` とし、`uvx` で実行できるようにします。

### [NEW] `src/openfisca_japan_mcp/sdk.py`
ビジネスロジックを実装します。入力・出力は標準的な辞書やリスト（JSONパース可能な形式）を利用し、独立した関数の集まりとして実装します。

1. **`get_attribute_info(tax_benefit_name: str) -> list[dict]`**
   指定された制度名に必要なプロパティ情報（名称、型、説明、必須かなど）を返します。
   - `["所得税", "住民税", "社会保険料", "児童手当"]` に対応させます。
   - それ以外の場合は空のリストを返します。

2. **`calc(household_list: list[dict], output_tax_benefit_list: list[str], date: str = None) -> list[dict]`**
   世帯情報のリストと出力したい制度名のリストを受け取り、OpenFisca-Japan のシミュレーションを実行します。
   - 入力された dict を `numpy.ndarray` に変換し、`SimulationBuilder` でエンティティを作成。
   - 指定された出力要素 (`output_tax_benefit_list`) を順に評価。
   - 変数が持っているエンティティ (`person` または `household`) に応じて、結果を `member_attribute` または `household_attribute` に書き戻します。

### [NEW] `src/openfisca_japan_mcp/server.py`
`fastmcp` ライブラリを利用して MCP サーバーのインターフェースを定義します。
- `FastMCP` インスタンスを作成（例: `mcp = FastMCP("OpenFisca-Japan-MCP")`）
- `@mcp.tool()` デコレータを用いて、`get_attribute_info` と `calc` を登録します。
- ツールには明確な docstring と型ヒント（Pydantic等の機能が利用されるため）をつけます。

### [NEW] `src/openfisca_japan_mcp/cli.py`
トランスポート層（stdio, SSE）を選択してサーバーを起動するエントリーポイントです。
- デフォルトは `stdio` トランスポートを使用。これにより Claude Desktop からコマンド（例: `["uvx", "openfisca-japan-mcp"]`）で接続できます。
- オプションで HTTP サーバとして振る舞い（SSE）、リモートから実行できる機能も実装します。

## Open Questions

特になし。前提条件・指定された仕様はすべて網羅されています。

## Verification Plan

### 自動検証
- 実装後、パッケージが `pip install .` （または `uv pip install -e .`）で正常にインストールできることを確認。
- CLI を使って直接 API が実行できるかテスト（モックコマンドを使用した stdio 形式での利用確認）。
- ダミーデータを利用して `calc` および `get_attribute_info` を実行し、想定通りの形で JSON 辞書が返却されるかを確認する簡単なテスト用スクリプトを作成・実行します。

### クライアント設定の提供
- デプロイ後に、ユーザーが自身の MCP クライアント (Claude Desktop 等) にどのように設定を記述すればよいか、Readme 等に日本語で記載・説明します。
