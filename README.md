## 在 GitHub 仓库中配置 Secrets

进入你的 GitHub 仓库页面，按以下步骤添加 Secrets：

### 1. 打开 Secrets 设置

- 点击仓库顶部的 **Settings**（设置）。
- 在左侧边栏找到 **Secrets and variables**，点击展开，选择 **Actions**。
- 点击右侧的 **New repository secret** 按钮。

### 2. 添加以下四个 Secrets

依次添加以下四个 Secret，名称必须完全一致：

| Secret 名称 | 说明 | 示例值 |
|---|---|---|
| `ALIYUN_ACCESS_KEY_ID` | 阿里云 RAM 用户的 AccessKey ID | `LTAI5t...` |
| `ALIYUN_ACCESS_KEY_SECRET` | 对应的 AccessKey Secret | `xXxXxX...` |
| `ALIYUN_DOMAIN_NAME` | 主域名 | `example.com` |
| `ALIYUN_RR` | 主机记录（子域名前缀） | `www` 或 `@` |

> **注意**：
> - `ALIYUN_RR` 填写 `@` 表示主域名本身，填写 `www` 表示 `www.example.com`。
> - 所有 Secret 名称区分大小写，请严格按上表填写。

### 3. 添加步骤示例

以添加 `ALIYUN_ACCESS_KEY_ID` 为例：

1. 点击 **New repository secret**。
2. 在 **Name** 输入框中填写 `ALIYUN_ACCESS_KEY_ID`。
3. 在 **Secret** 输入框中粘贴你的 AccessKey ID。
4. 点击 **Add secret** 保存。
5. 重复上述步骤，添加其余三个 Secrets。

添加完成后，列表应显示四个 Secrets（值会被隐藏，只显示名称和更新时间）。
