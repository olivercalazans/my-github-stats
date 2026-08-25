<h1 align="center"> My Github Stats </h1>

<div align="center">
  <img src="https://img.shields.io/badge/lang-python-%233572A5.svg?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/license-AGPL%20v3-F0B400?style=for-the-badge" />
</div>

<br>

A lightweight, self-hosted tool designed to generate dynamic SVG statistics for your GitHub profile README—completely independent of third-party services.

<br>

## Why Self-Hosted?
Public stats APIs frequently go down, leave you stranded, or suffer from massive update delays (sometimes taking a week or more to refresh) because they serve thousands of users and require heavy financial investment to scale. 

By moving to a self-hosted approach running on your own GitHub Actions:
* **Reliability:** No more third-party downtime; your stats depend only on GitHub's infrastructure.
* **Freshness:** Cards update daily—or at whatever custom interval you choose.
* **Performance:** SVGs are served directly from your own repository for blazing-fast load times.
* **Customization:** Full freedom to modify and adapt the design into any type of image or style you want.

<br>

## How to Use (Quick Start)

1. **Fork** this repository.
2. Generate a personal access token with public repository read permissions (`repo:public_repo` or `public_read`) and add it to your fork's **Settings > Secrets and variables > Actions > Repository secrets** as a secret named `TOKEN`.
3. Go to your fork's **Settings > Actions > General**, scroll down to **Workflow permissions**, select **Read and write permissions**, and save.
4. The GitHub Actions workflow will automatically query the GitHub GraphQL API on schedule, generate your SVGs, and update your repository.
5. Add the generated SVGs to your main profile README using standard Markdown:

```markdown
<img src="https://raw.githubusercontent.com/<USERNAME>/my-github-stats/main/images/languages_stats.svg" />
```

<br>

## LICENSE
This project is licensed under the AGPL-3.0 License. See the [LICENSE](LICENSE) file for details.
