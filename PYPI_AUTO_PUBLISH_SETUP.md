# PyPI 自动发布配置说明

## 问题分析

当前仓库的 PyPI 发布流程存在以下问题：

1. **需要手动创建 tag**：`publish.yml` 只在推送 tag 时触发，合并代码后不会自动发布
2. **缺少自动化流程**：开发者需要记住手动打 tag 并推送
3. **容易遗忘**：合并代码后忘记创建 tag，导致新版本未发布到 PyPI

## 解决方案

添加了自动 tag 创建工作流，实现完全自动化的发布流程：

### 新增文件

1. **`.github/workflows/auto-tag.yml`** - 自动 tag 创建工作流
   - 监听 main 分支的 push 事件
   - 从 `pyproject.toml` 读取版本号
   - 检查 tag 是否已存在
   - 自动创建并推送 tag（格式：`v{version}`）
   - 触发 publish 工作流

2. **`docs/RELEASE.md`** - 发布流程文档
   - 详细的自动发布流程说明
   - 手动发布的备选方案
   - PyPI Trusted Publisher 配置指南
   - 常见问题排查

3. **`.github/pull_request_template.md`** - PR 模板
   - 提醒开发者更新版本号
   - 标准化 PR 描述格式
   - 版本更新检查清单

4. **`scripts/bump_version.py`** - 版本管理脚本
   - 自动更新 `pyproject.toml` 中的版本
   - 支持 major/minor/patch 版本递增
   - 自动创建 git commit
   - 检查 tag 冲突

### 修改文件

1. **`.github/workflows/publish.yml`**
   - 添加 `skip-tests` 选项用于手动触发时跳过测试
   - 保持原有的 tag 触发机制

## 工作流程

### 自动发布流程（推荐）

```
开发者更新版本 → 合并到 main → 自动创建 tag → 自动发布到 PyPI
```

详细步骤：

1. **更新版本号**
   ```bash
   # 方式 1: 使用脚本（推荐）
   python scripts/bump_version.py patch  # 0.1.0 -> 0.1.1
   python scripts/bump_version.py minor  # 0.1.0 -> 0.2.0
   python scripts/bump_version.py major  # 0.1.0 -> 1.0.0
   
   # 方式 2: 手动编辑 pyproject.toml
   # 修改 version = "0.2.0"
   ```

2. **创建 PR 并合并到 main**
   ```bash
   git push origin feature/your-feature
   # 在 GitHub 上创建 PR
   # Review 并合并到 main
   ```

3. **自动执行**
   - `auto-tag.yml` 检测到 main 分支更新
   - 读取 `pyproject.toml` 中的版本（如 `0.2.0`）
   - 创建 tag `v0.2.0` 并推送
   - `publish.yml` 被 tag 触发
   - 运行测试 → 构建包 → 发布到 PyPI → 创建 GitHub Release

### 手动发布流程（备选）

如果需要手动控制发布：

```bash
# 1. 更新版本
vim pyproject.toml  # 修改 version

# 2. 提交并推送
git add pyproject.toml
git commit -m "chore: bump version to 0.2.0"
git push origin main

# 3. 手动创建 tag
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

## PyPI 配置要求

### 必须配置 Trusted Publisher

工作流使用 OIDC 认证，需要在 PyPI 上配置 Trusted Publisher：

1. 访问 https://pypi.org/manage/account/publishing/
2. 添加新的 publisher：
   - **PyPI Project Name**: `shotgrid-query`
   - **Owner**: `loonghao`
   - **Repository name**: `shotgrid-query`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`

### GitHub Environment 配置（可选）

在仓库设置中创建 `pypi` environment：

1. Settings → Environments → New environment
2. 名称：`pypi`
3. 可选保护规则：
   - Required reviewers（需要审批）
   - Wait timer（等待时间）
   - Deployment branches（限制为 main 分支）

## 使用示例

### 场景 1：发布 bug 修复版本

```bash
# 当前版本 0.1.0，修复了一个 bug
python scripts/bump_version.py patch
# 版本更新为 0.1.1

git push origin feature/fix-bug
# 创建 PR，合并到 main
# 自动发布 v0.1.1 到 PyPI
```

### 场景 2：发布新功能

```bash
# 当前版本 0.1.0，添加了新功能
python scripts/bump_version.py minor
# 版本更新为 0.2.0

git push origin feature/new-feature
# 创建 PR，合并到 main
# 自动发布 v0.2.0 到 PyPI
```

### 场景 3：发布重大更新

```bash
# 当前版本 0.9.0，准备发布 1.0.0
python scripts/bump_version.py major
# 版本更新为 1.0.0

git push origin feature/v1-release
# 创建 PR，合并到 main
# 自动发布 v1.0.0 到 PyPI
```

## 监控和验证

### 查看工作流执行状态

访问 GitHub Actions 页面：
https://github.com/loonghao/shotgrid-query/actions

### 验证发布成功

1. **PyPI 页面**：https://pypi.org/project/shotgrid-query/
2. **GitHub Releases**：https://github.com/loonghao/shotgrid-query/releases
3. **安装测试**：
   ```bash
   pip install shotgrid-query==0.2.0
   ```

## 常见问题

### Q: Tag 已存在怎么办？

A: `auto-tag.yml` 会检测 tag 是否存在，如果存在则跳过创建。需要更新 `pyproject.toml` 中的版本号。

### Q: 测试失败导致发布中断？

A: `publish.yml` 会先运行测试，失败则不会发布。修复问题后重新推送即可。

### Q: 如何跳过测试直接发布？

A: 在 GitHub Actions UI 手动触发 `Publish to PyPI` 工作流，勾选 `skip-tests` 选项（不推荐用于生产）。

### Q: 版本号格式要求？

A: 遵循语义化版本（Semantic Versioning）：`MAJOR.MINOR.PATCH`，如 `1.2.3`。

## 下一步

1. **配置 PyPI Trusted Publisher**（必须）
2. **测试自动发布流程**：
   - 更新版本到 `0.1.1`
   - 合并到 main
   - 观察工作流执行
3. **配置 GitHub Environment**（可选，增强安全性）

## 参考文档

- [完整发布文档](docs/RELEASE.md)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Actions Workflows](https://docs.github.com/en/actions)

