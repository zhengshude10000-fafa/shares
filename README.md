# A股全自动盘前/盘后报告

GitHub Actions 在工作日北京时间 09:00 生成盘前观察、15:40 生成盘后复盘，电脑关机也可运行。报告由公开行情数据和透明规则生成，不需要 OpenAI API Key。

## 部署

1. 在 GitHub 新建公开仓库，默认分支设为 `main`。
2. 上传本项目全部文件（必须保留 `.github/workflows`）。
3. 打开仓库 `Settings → Pages → Source`，选择 **GitHub Actions**。
4. 打开 `Actions → Generate A-share reports → Run workflow`，分别手动生成一次盘前和盘后报告。
5. Pages 工作流完成后，在仓库 `Settings → Pages` 获取手机可访问的网址。

GitHub 计划任务可能延迟数分钟。周末不会定时运行；法定节假日因未连接交易所日历，脚本可能生成一份标记为工作日的静态报告，后续可接入节假日日历文件。

## 调整自选

编辑 `config.json`。沪市 `market` 为 1，深市为 0。不要把持仓成本写进公开仓库；成本建议继续只保存在浏览器本地。

## 本地测试

```bash
python -m unittest discover -s tests
python src/report.py after-market
```

## 数据与风险边界

- 行情源为东方财富公开接口，失败时会重试并在报告中标注缺失。
- 09:00 盘前版不包含当日集合竞价，内容是隔夜/上一交易日快照基础上的条件计划。
- 报告为规则分析，不是收益预测，不构成投资建议。
