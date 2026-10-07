# xunji-sync
训记数据每日同步（只读）+ Agent 模版写入。

- `pull` 每天 22:53（新加坡）拉最近 4 天训练、一年身体数据、Agent 模版 → `data/`
- 改 `templates/payload.json` 并推送 → 自动写入训记「Agent 模版」文件夹（同名模版会更新）
- 密钥存在仓库 Settings › Secrets：`XUNJI_TRAIN_KEY`、`XUNJI_BODY_KEY`、`XUNJI_TPL_KEY`
