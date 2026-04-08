# OpenFisca-Japan-MCP

OpenFisca-Japan-MCP は、OpenFisca-Japan を MCP (Model Context Protocol) 経由で呼び出すためのサーバーおよび Python SDK です。LLM エージェント（Claude Desktop など）から利用しやすい型とインターフェースを提供します。

## 機能
- `get_attribute_info(tax_benefit_name)`: 入力された制度を計算するために必要な属性情報を取得します。
- `calc(household_list, output_tax_benefit_list, date)`: 世帯の配列データを元に、指定した制度（所得税、住民税など）の金額を計算し、元の配列拡張して返します。

## Claude Desktop からの利用 (MCP Client)

`uv` を利用して直接 Claude Desktop などに組み込むことができます。
`mcp_settings.json` の設定例：

```json
{
  "mcpServers": {
    "openfisca-japan-mcp": {
      "command": "uvx",
      "args": [
        "--from", "githubへのパス または デプロイ先のパッケージ名",
        "openfisca-japan-mcp"
      ]
    }
  }
}
```

ローカルで検証する場合は以下のようになります。
```json
{
  "mcpServers": {
    "openfisca-japan-mcp": {
      "command": "uvx",
      "args": [
        "--from", "/Users/to/OpenFisca-Japan-MCP",
        "openfisca-japan-mcp"
      ]
    }
  }
}
```

## HTTP SSE サーバーとしての起動

以下のコマンドで HTTP SSE サーバーとして起動し、別ホストの MCP クライアントから接続することも可能です。

```bash
uvx openfisca-japan-mcp --transport sse --port 8080
```
