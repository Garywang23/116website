# 116导航自动更新版

文件结构：

- `index.html`：页面
- `sites.json`：网站排名数据
- `update_rank.py`：拉取 Tranco Top 1M 并生成前 116 名
- `.github/workflows/update-rank.yml`：GitHub Actions 定时任务

部署方式：

1. 上传全部文件到 GitHub 仓库根目录。
2. GitHub 仓库 Settings → Actions → General → Workflow permissions，选择 `Read and write permissions`。
3. Cloudflare Pages 绑定这个仓库。
4. 以后 GitHub Actions 每天自动更新 `sites.json`，Cloudflare Pages 会跟着重新部署。

手动更新：

GitHub → Actions → `Update Top Sites Ranking` → `Run workflow`
